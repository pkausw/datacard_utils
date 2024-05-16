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
thisdir = os.path.dirname(os.path.realpath(__file__))
if not thisdir in sys.path:
    sys.path.append(os.path.abspath(thisdir))
manipulator_dir = os.path.join(thisdir, "manipulator_methods")
if not manipulator_dir in sys.path:
    sys.path.append(manipulator_dir)

from manipulator_methods.process_manipulator import ProcessManipulator

proc_manipulator = ProcessManipulator()

def freeze_nuisances(harvester):
    to_freeze = """kfactor_wjets kfactor_zjets
                                .*bgscale_MCCR.* .*bgnorm_ttcc_FH""".split()
    harvester.SetFlag("filters-use-regex", True)
    for par in to_freeze:
        systs = harvester.cp().syst_name([par]).syst_name_set()
        for p in systs:
            harvester.GetParameter(p).set_frozen(True)



def main(**kwargs):

    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    harvester.SetFlag("filters-use-regex", True)
    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    
    rebin_scheme = kwargs.get("scheme", None)
    if rebin_scheme:
        bin_manipulator = BinManipulator()
        bin_manipulator.scheme = rebin_scheme
        harvester = bin_manipulator.rebin_shapes(harvester = harvester)
    
    freeze_nuisances(harvester)

    removal_list = kwargs.get("removal_list", [])
    bin_list = kwargs.get("bin_list", [".*"])

    proc_manipulator.drop_all_processes(  harvester = harvester,
                    to_drop = removal_list,
                    bins = bin_list)
    
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
    This tool combines multiple manipulator methods.
    Current list of implemented methods:
    apply_validation, group_manipulator, nuisance_manipulator, 
    rebin_distributions, scale_higgs_mass. 
    This tool employs functions from the CombineHarvester package. 
    Please make sure that you have installed it!

    The script will first scale the higgs mass and will then proceed
    with other manipulations.
    """.split())

    usage += """

    python %prog [options]
    """
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
    optional_group.add_option("--prefix",
                        help = " ".join(
                            """
                            prepend this string to the datacard names.
                            Output will have format 'PREFIX_DATACARDNAME'
                            """.split()
                        ),
                        dest = "prefix",
                        type = "str"
                    )
    
    optional_group.add_option("-b", "--bin",
                        help = " ".join(
                            """
                            remove processes from this bin. Can be called
                            multiple times. Default: Processes are removed from
                            all bins
                            """.split()
                        ),
                        dest = "bin_list",
                        action = "append",
                        # type = "str"
                    )
    optional_group.add_option("-p","--process",
                        help = " ".join(
                            """
                            remove this process
                            """.split()
                        ),
                        dest = "removal_list",
                        action = "append",
                    )
    parser.add_option_group(optional_group)
    options, files = parser.parse_args()

    cardpath = options.datacard
    if not cardpath:
        parser.error("You need to provide the path to a datacard!")
    elif not os.path.exists(cardpath):
        parser.error("Could not find datacard in '{}'".format(cardpath))
    
    if options.bin_list is None or len(options.bin_list) == 0:
        options.bin_list = [".*"]
    l = options.removal_list
    final_list = []
    for p in l:
        final_list += p.split(",")
    options.removal_list = list(set(final_list))
    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(**vars(options))