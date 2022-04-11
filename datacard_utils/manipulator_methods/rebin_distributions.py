from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import ROOT
import json
from six.moves import range
cmssw_base = os.environ["CMSSW_BASE"]
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

if not os.path.exists(cmssw_base):
    raise ValueError("Could not find CMSSW base!")
# import CombineHarvester.CombineTools.ch as ch

from optparse import OptionParser, OptionGroup

ROOT.TH1.AddDirectory(False)
try:
    print("importing CombineHarvester")
    import CombineHarvester.CombineTools.ch as ch
    print("done")
except:
    msg = " ".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)
from .common_manipulations import CommonManipulations

class BinManipulator(object):
    choices = "left right all mem half dl third".split()
    def __init__(self):
        self.bin_edges = []
        self.threshold = 15
        self.__debug = 10
        self.log = ""
        self.log_path = os.path.join(os.getcwd(), "rebin.log")
        self.__merge_n_bins = None

    def __del__(self):
        if self.__debug >= 10:
            print(("saving log of rebinning module here: '{}'"\
                        .format(self.log_path)))
        outdir = os.path.dirname(self.log_path)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        with open(self.log_path, "w") as f:
            f.write(self.log)
        
        # super().__del__()

    @property
    def merge_n_bins(self):
        """
        Getter function for the merge_n_bins property
        """
        return self.__merge_n_bins
    @merge_n_bins.setter
    def merge_n_bins(self, val):
        """
        Setter function for the merge_n_bins property.
        First checks wether the input is an integer value.
        If the check passes, the value is set, otherwise raise a ValueError

        Args:
        - val:  number of bins that are to be merged at the right-hand side
                of the distributions. Type must be int
        """
        if isinstance(val, int):
            if self.__debug >= 10:
                print("will merge the last {} bins on the right-hand side".format(val))
            self.__merge_n_bins = int(val)
        else:
            raise ValueError("Input for 'merge_n_bins' must be integer!")
        
    def load_edges(self, proc):
        if isinstance(proc, ROOT.TH1):
            h = proc.Clone("clone")
        else:
            h = proc.ShapeAsTH1F()
        nbins = h.GetNbinsX()
        if self.__debug >= 10:
            print(("loading edges from {} bins".format(nbins)))
        self.bin_edges = [h.GetBinLowEdge(i) for i in range(1, nbins+2)]
        print((self.bin_edges))

    def apply_scheme(self):
        edges = []
        if self.scheme == "all":
            edges = [self.bin_edges[0]]
        elif self.scheme == "right":
            middle = int(len(self.bin_edges)/2.)
            edges = self.bin_edges[:middle+1]
        elif self.scheme == "left":
            middle = int(len(self.bin_edges)/2.)
            edges = [self.bin_edges[0]] + self.bin_edges[middle:]
        elif self.scheme == "mem":
            # drop first bin for tests with SL MEM
            edges = self.bin_edges[1:]
        elif self.scheme == "half":
            # select every second bin edge
            edges = [self.bin_edges[0], self.bin_edges[-1]]
            edges += self.bin_edges[::2]
        elif self.scheme == "third":
            # select every second bin edge
            edges = [self.bin_edges[0], self.bin_edges[-1]]
            edges += self.bin_edges[::3]
        elif self.scheme == "dl":
            edges = [-1, 0, 1]
        elif isinstance(self.scheme, int):
            edges = self.bin_edges[:int(-self.scheme)]
        else:
            print(("ERROR: did not recognice scheme '{}'".format(self.scheme)))
            print("Will not rebin")
            edges = self.bin_edges
        if not self.bin_edges[-1] in edges:
            edges.append(self.bin_edges[-1])
        edges = sorted(list(set(edges)))
        return edges

    def get_statistical_binning(self, combinedHist, datahist):
        """Determine binning based on MC statistics in each bin.
        In statistical analyses, it is important to choose a binning
        where each bin
        - has data to compare against
        - has a minimial amount of statistcs in the bin to ensure
          proper behaviour (e.g. a minimal amount of background
          events or some criterion based on the MC stat uncertainties)
        
        'combinedHist' is the total histogram of all processes
        you want to take into account for the rebinning (e.g. all
        background processes). The function will loop through all
        bins and compare the bin entries agains the threshold.

        If 'threshold' is > 1, the bin content is required to be 
        >= threshold.

        If 'threshold' is < 1, the bin error (i.e. the MC stat uncertainties)
        is required to be smaller than threshold.

        Bins are summed from right to left until the threshold criterion
        is met. 

        Args:
            combinedHist (ROOT.TH1):    total histogram of all processes 
                                        to be considered
            threshold (float):          threshold to compare against. 
                                        threshold > 1: compare bin contents
                                        threshold < 1: compare bin errors

        Returns:
            list(floats):               bin edges after applying the criterion
        """
        squaredError = 0.
        binContent = 0.
        data = 0.
        bin_edges = []
        last_added_edge = 0
        nbins = combinedHist.GetNbinsX()
        for i in range(nbins, 0, -1):
            if i == nbins:
                last_added_edge = combinedHist.GetBinLowEdge(nbins+1)
                if self.__debug >= 10:
                    print(("adding new bin edge at {}".format(last_added_edge)))
                bin_edges.append(last_added_edge)

            # add together squared bin errors and bin contents
            squaredError += combinedHist.GetBinError(i)**2
            binContent += combinedHist.GetBinContent(i)
            data += datahist.GetBinContent(i)
            if self.__debug >= 10:
                print(("bin (low edge): {} ({})".format(i, combinedHist.GetBinLowEdge(i))))
                print(("bkg stack: {}".format(combinedHist.GetBinContent(i))))
                print(("sum: {}".format(binContent)))
                print(("threshold: {}".format(self.threshold)))

            # calculate relative error
            relerror = squaredError**0.5/binContent if not binContent == 0 else squaredError**0.5
            
            if binContent == 0: continue
            criterion = False
            if isinstance(self.threshold, str):
                # check if data is covered by prefit background uncertainties
                dataError = data**0.5
                # MC stat fluctuations are not covered in bin error of 
                # histograms, add manually
                binError = (squaredError + binContent)**0.5 
                print("checking data")
                print(("\tdata: {}".format(data)))
                print(("\tdataError: {}".format(dataError)))
                print(("\tbinContent: {}".format(binContent)))
                print(("\tbinError: {}".format(binError)))
                if data >= binContent:
                    criterion = any(x <= (binContent + binError) for x in [data - dataError, data])
                else:
                    criterion = any(x >= (binContent - binError) for x in [data + dataError, data])
            else:
                if self.threshold > 1:
                    # do rebinning based on the population of the bins enterly
                    # bins are ok if the bin content is larger than the threshold
                    criterion = binContent >= self.threshold
                        
                else:
                    # if relative error is smaller than threshold, start new bin
                    print("Relative error: {}".format(relerror))
                    criterion = relerror <= self.threshold
            # if criterion for binning is met, add new bin edge
            if criterion:
                last_added_edge = combinedHist.GetBinLowEdge(i)
                if self.__debug >= 10:
                    print(("adding new bin edge at {}".format(last_added_edge)))
                bin_edges.append(last_added_edge)
                squaredError = 0.
                binContent = 0.
                data = 0.
        
        
        underflow_edge = combinedHist.GetBinLowEdge(1)
        if not underflow_edge in bin_edges:
            # if underflow_edge is not in bin_edges list the relative
            # error of the last bin is too small, so just merge the
            # first two bins by replacing the last_added_edge with
            # the underflow_edge 
            min_index = bin_edges.index(min(bin_edges))
            bin_edges[min_index] = underflow_edge
        last_added_edge = combinedHist.GetBinLowEdge(nbins+1)
        if not last_added_edge in bin_edges:
            bin_edges.append(last_added_edge)
        bin_edges = sorted(bin_edges)
        if self.__debug >= 1:
            print(("\tnew bin edges: [{}]".format(",".join([str(round(b,4)) for b in bin_edges]))))
        return bin_edges

    def do_statistical_rebinning(self, harvester, channels = [".*"], eras = [".*"],\
                                     bins = [".*"], processes = []):
        harvester.SetFlag("filters-use-regex", True)
        channel_set = harvester.cp().channel(channels).channel_set()
        eras_set = harvester.cp().era(eras).era_set()
        for ch in channel_set:
            for e in eras_set:
                
                current_harvester = harvester.cp().channel([ch]).era([e])
                these_bins = current_harvester.cp().bin(bins).bin_set()
                print(("Rebinning based on MC Statistics with threshold '{}'".\
                            format(self.threshold)))
                print("will perform rebinning for bins:")
                print(these_bins)
                for b in these_bins:
                    log_lines = ["="*60]
                    log_lines.append("channel: '{}'".format(ch))
                    log_lines.append("era: '{}'".format(e))
                    log_lines.append("bin: '{}'".format(b))
                    if len(processes) == 0:
                        relevant_process_harv = current_harvester.cp().bin([b])\
                                                    .backgrounds()
                    else:
                        relevant_process_harv = current_harvester.cp().bin([b])\
                                                    .process(processes)
                    self.bin_edges = []
                    proc_list = ", ".join(relevant_process_harv.process_set())
                    log_lines.append("processes: {}".format(proc_list))
                    if self.__debug >= 10:
                        print(("considered processes for bin '{}'".format(b)))
                        print(proc_list)
                    if isinstance(self.threshold, float) and self.threshold <= 1:
                        hist = relevant_process_harv.GetShape()
                    else:
                        hist = relevant_process_harv.GetShapeWithUncertainty()
                    data = current_harvester.cp().bin([b]).GetObservedShape()
                    self.load_edges(hist)
                    original_edges = self.bin_edges[:]
                    # log edges before and after manipulation
                    log_lines.append("bin edges before rebinning:")
                    log_lines.append(", ".join([str(x) for x in self.bin_edges]))

                    self.bin_edges = self.get_statistical_binning(hist, data)

                    log_lines.append("bin edges after rebinning:")
                    log_lines.append(", ".join([str(x) for x in self.bin_edges]))
                    if not original_edges == self.bin_edges:
                        log_lines.append("Attention: binning changed!")
                    if self.__debug >= 10:
                        print(("\n".join(["\t{}".format(x) for x in self.bin_edges])))
                    harvester.cp().channel([ch]).era([e]).bin([b])\
                            .VariableRebin(self.bin_edges)
                    log_lines.append("="*60+"\n")
                    self.log += "\n".join(log_lines)
        return harvester
    
    def rebin_shapes(self, harvester, channels = [".*"], eras = [".*"],\
                            bins = [".*"]):
        harvester.SetFlag("filters-use-regex", True)
        # harvester.SetFlag("merge-under-overflow-bins", True)
        channel_set = harvester.cp().channel(channels).channel_set()
        eras_set = harvester.cp().era(eras).era_set()
        for ch in channel_set:
            for e in eras_set:
                # load relevant bins for current channel and era
                bins = harvester.cp().channel([ch]).era([e]).bin_set()
                for b in bins:
                    log_lines = ["="*60]
                    log_lines.append("channel: '{}'".format(ch))
                    log_lines.append("era: '{}'".format(e))
                    log_lines.append("bin: '{}'".format(b))
                    self.bin_edges = []
                    this_harvester = harvester.cp().channel([ch]).era([e])\
                                        .bin([b])
                    p = this_harvester.process_set()[-1]
                    this_harvester.cp().process([p]).ForEachProc(\
                        lambda x: self.load_edges(x))
                    log_lines.append("bin edges before rebinning:")
                    log_lines.append(", ".join([str(x) for x in self.bin_edges]))
                    if self.__debug >= 10:
                        print(b)
                        print(("\n".join(["\t{}".format(x) for x in self.bin_edges])))

                    if all(x == None for x in [self.scheme, self.__merge_n_bins]):
                        print("specified no scheme and no merge bins, skipping")
                        return harvester
                    if self.scheme is not None:
                        self.bin_edges = self.apply_scheme()
                    if self.merge_n_bins is not None:
                        index = -self.merge_n_bins
                        self.bin_edges = self.bin_edges[:index] + [self.bin_edges[-1]]

                    log_lines.append("bin edges after rebinning:")
                    log_lines.append(", ".join([str(x) for x in self.bin_edges]))
                    
                    if self.__debug >= 10:
                        print(("after applying scheme {}".format(self.scheme)))
                        print(("\n".join(["\t{}".format(x) for x in self.bin_edges])))

                    harvester.cp().channel([ch]).era([e]).bin([b])\
                        .VariableRebin(self.bin_edges)

                    log_lines.append("="*60+"\n")
                    self.log += "\n".join(log_lines)
        return harvester

def WriteCards(harvester, newpath, output_rootfile, bins):
    writer = ch.CardWriter(newpath, output_rootfile)
    writer.SetWildcardMasses([])
    writer.SetVerbosity(1)
    writer.WriteCards("cmb", harvester.cp().bin(bins))

def main(*args, **kwargs):

    harvester = ch.CombineHarvester()
    #harvester.SetFlag("check-negative-bins-on-import", False)
    harvester.SetFlag("allow-missing-shapes", False)
    
    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "test", "13TeV", "")

    # harvester.PrintAll()
    scheme = kwargs.get("scheme", None)
    if not scheme:
        msg = "Could not find rebin scheme, abort!"
        raise ValueError(msg)
    bin_manipulator = BinManipulator()
    bin_manipulator.scheme = scheme
    harvester = bin_manipulator.do_statistical_rebinning(harvester)
    harvester = bin_manipulator.rebin_shapes(harvester = harvester)

    common_manipulations = CommonManipulations()
    common_manipulations.apply_common_manipulations(harvester)
    

    # harvester.PrintSysts()
    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    basename = os.path.basename(cardpath)
    prefix = kwargs.get("prefix", None)
    basename = "{}_{}".format(prefix, basename) if prefix else basename
    newpath = os.path.join(outdir, "datacards", basename)
    output_rootfile = kwargs.get("output_rootpath")
    if output_rootfile is None:
        output_rootfile = ".".join(basename.split(".")[:-1] + ["root"])
    output_rootfile = "{}_{}".format(prefix, output_rootfile) \
                        if prefix else output_rootfile
    output_rootfile = os.path.join(outdir, "rootfiles", output_rootfile)

    # harvester.WriteDatacard(newpath)
    writer = ch.CardWriter(newpath, output_rootfile)
    writer.SetWildcardMasses([])
    writer.SetVerbosity(1)
    writer.WriteCards("cmb", harvester)
    
def parse_arguments():
    usage = " ".join("""
    Tool to change inputs for combine based on output of
    'ValidateDatacards.py'. This tool employs functions
    from the CombineHarvester package. Please make sure
    that you have installed it!
    """.split())
    parser = OptionParser(usage = usage)
    parser.add_option("-d", "--datacard",
                        help = " ".join(
                            """
                            path to datacard to change
                            """.split()
                        ),
                        dest = "datacard",
                        metavar = "path/to/datacard",
                        type = "str"
                    )

    parser.add_option("-o", "--outputrootfile",
                        help = " ".join(
                            """
                            use this root file name for the varied
                            inputs. Default is the original root file
                            name
                            """.split()
                        ),
                        dest = "output_rootpath",
                        metavar = "path/for/output",
                        # default = ".",
                        type = "str"
                    )
    
    parser.add_option("-s", "--rebin-scheme",
                        help = " ".join(
                            """
                            rebin the shapes in the different channels
                            according to this scheme. Current choices:
                            {}
                            """.format(",".join(BinManipulator.choices)).split()
                        ),
                        dest = "scheme",
                        metavar = "scheme",
                        choices = BinManipulator.choices,
                        default = "all",
                        # type = "str"
                    )
    parser.add_option("-m", "--mergeLastNbins",
                        help = " ".join("""
                            merge the last N bins of the distributions.
                            The logic is based on the python list comprehension.
                            For example, to merge the last two bins, i.e. N=2,
                            the bin edge at position [-2] will be removed.
                        """.split()),
                        metavar = "N",
                        dest = "merge_n_bins",
                        type = "int"
                    )
    

    optional_group = OptionGroup(parser, "optional options")
    optional_group.add_option("--directory",
                        help = " ".join(
                            """
                            save new datacards in this directory.
                            Default = "."
                            """.split()
                        ),
                        dest = "outdir",
                        metavar = "path/for/output",
                        default = ".",
                        type = "str"
                    )
    optional_group.add_option("-p", "--prefix",
                        help = " ".join(
                            """
                            prepend this string to the datacard names.
                            Output will have format 'PREFIX_DATACARDNAME'
                            """.split()
                        ),
                        dest = "prefix",
                        type = "str"
                    )
    parser.add_option_group(optional_group)
    options, files = parser.parse_args()

    # cardpath = options.datacard
    # if not cardpath:
    #     parser.error("You need to provide the path to a datacard!")
    # elif not os.path.exists(cardpath):
    #     parser.error("Could not find datacard in '{}'".format(cardpath))
    
    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))
