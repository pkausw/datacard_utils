import os
import sys
import ROOT
import json
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

class BinManipulator(object):
    choices = "left right all mem".split()
    def __init__(self):
        self.bin_edges = []
        
    def load_edges(self, proc):
        h = proc.ShapeAsTH1F()
        nbins = h.GetNbinsX()
        self.bin_edges = [h.GetBinLowEdge(i) for i in range(1, nbins+2)]
        print(self.bin_edges)

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
        else:
            print("ERROR: did not recognice scheme '{}'".format(self.scheme))
            print("Will not rebin")
            edges = self.bin_edges
        if not self.bin_edges[-1] in edges:
            edges.append(self.bin_edges[-1])
        return edges

    def rebin_shapes(self, harvester):
        bins = harvester.bin_set()
        for b in bins:
            self.bin_edges = []
            p = harvester.cp().bin([b]).process_set()[-1]
            harvester.cp().bin([b]).process([p]).ForEachProc(\
                lambda x: self.load_edges(x))
            print(b)
            print("\n".join(["\t{}".format(x) for x in self.bin_edges]))
            self.bin_edges = self.apply_scheme()
            print("after applying scheme {}".format(self.scheme))
            print("\n".join(["\t{}".format(x) for x in self.bin_edges]))
            harvester.cp().bin([b]).VariableRebin(self.bin_edges)
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
    harvester = bin_manipulator.rebin_shapes(harvester = harvester)

    

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