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

bin_edges = []
def load_edges(proc):
    h = proc.ShapeAsTH1F()
    nbins = h.GetNbinsX()
    global bin_edges
    bin_edges = [h.GetBinLowEdge(i) for i in range(1, nbins+2)]
    print(bin_edges)

def apply_scheme(bin_edges, scheme):
    edges = []
    if scheme == "all":
        edges = bin_edges[::2]
    
    if not bin_edges[-1] in edges:
        edges.append(bin_edges[-1])
    return edges

def rebin_shapes(harvester, scheme):
    bins = harvester.bin_set()
    for b in bins:
        global bin_edges
        bin_edges = []
        p = harvester.cp().bin([b]).process_set()[-1]
        harvester.cp().bin([b]).process([p]).ForEachProc(\
            lambda x: load_edges(x))
        print(b)
        print("\n".join(["\t{}".format(x) for x in bin_edges]))
        bin_edges = apply_scheme(bin_edges, scheme)
        print("after applying scheme {}".format(scheme))
        print("\n".join(["\t{}".format(x) for x in bin_edges]))
        harvester.cp().bin([b]).VariableRebin(bin_edges)
    return harvester

def main(*args, **kwargs):

    harvester = ch.CombineHarvester()
    #harvester.SetFlag("check-negative-bins-on-import", False)
    harvester.SetFlag("allow-missing-shapes", False)
    
    # print(cardpath)
    # harvester.ParseDatacard(cardpath, "$ANALYSIS_$CHANNEL_hdecay.txt")
    for f in args:
        print(f)
        harvester.ParseDatacard(f, "ttH")

    # harvester.PrintAll()
    scheme = kwargs.get("scheme", None)
    if not scheme:
        msg = "Could not find rebin scheme, abort!"
        raise ValueError(msg)
    harvester = rebin_shapes(harvester = harvester, scheme = scheme)

    

    # harvester.PrintSysts()
    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    # basename = os.path.basename(cardpath)
    prefix = kwargs.get("prefix", None)
    # basename = "{}_{}".format(prefix, basename) if prefix else basename
    newpath = os.path.join(outdir, "datacards", "$BIN.txt")
    output_rootfile = kwargs.get("output_rootpath")
    output_rootfile = "{}_{}".format(prefix, output_rootfile) if prefix else output_rootfile
    output_rootfile = output_rootfile.replace(".root", "_$BIN.root")
    output_rootfile = os.path.join(outdir, output_rootfile)

    # harvester.WriteDatacard(newpath)
    writer = ch.CardWriter(newpath, output_rootfile)
    writer.SetWildcardMasses([])
    writer.SetVerbosity(1)
    bins = harvester.bin_set()
    for b in bins:
        writer.WriteCards("cmb", harvester.cp().bin([b]))


def parse_arguments():
    usage = " ".join("""
    Tool to change inputs for combine based on output of
    'ValidateDatacards.py'. This tool employs functions
    from the CombineHarvester package. Please make sure
    that you have installed it!
    """.split())
    parser = OptionParser(usage = usage)
    # parser.add_option("-d", "--datacard",
    #                     help = " ".join(
    #                         """
    #                         path to datacard to change
    #                         """.split()
    #                     ),
    #                     dest = "datacard",
    #                     metavar = "path/to/datacard",
    #                     type = "str"
    #                 )

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
    choices = "left right all".split()
    parser.add_option("-s", "--rebin-scheme",
                        help = " ".join(
                            """
                            rebin the shapes in the different channels
                            according to this scheme. Current choices:
                            {}
                            """.format(",".join(choices)).split()
                        ),
                        dest = "scheme",
                        metavar = "scheme",
                        choices = choices,
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