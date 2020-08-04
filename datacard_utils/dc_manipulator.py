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
# manipulator_dir = os.path.join(thisdir, "manipulator_methods")
# if not manipulator_dir in sys.path:
#     sys.path.append(manipulator_dir)

from manipulator_methods.group_manipulator import GroupManipulator
from manipulator_methods.scale_higgs_mass import MassManipulator
from manipulator_methods.rebin_distributions import BinManipulator
from manipulator_methods.apply_validation import ValidationInterface

def freeze_nuisances(harvester):
    to_freeze = "kfactor_wjets kfactor_zjets CMS_ttHbb_bgscale_MCCR".split()
    systs = harvester.syst_name_set()
    for p in to_freeze:
        if p in systs:
            harvester.GetParameter(p).set_frozen(True)

def scale_higgs_mass(harvester, base_mass = 125):
    mass_scaler = MassManipulator()
    mass_scaler.apply = True
    mass_scaler.basemass = base_mass
    
    mass_scaler.ScaleMasses(harvester)

def main(**kwargs):

    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    
    rebin_scheme = kwargs.get("scheme", None)
    if rebin_scheme:
        bin_manipulator = BinManipulator()
        bin_manipulator.scheme = rebin_scheme
        harvester = bin_manipulator.rebin_shapes(harvester = harvester)
        
    apply_validation = kwargs.get("apply_validation")
    if apply_validation:
        val_interface = ValidationInterface()
        jsonpath = kwargs.get("validation_jsonpath")
        if not jsonpath:
            val_interface.generate_validation_output(cardpath)
        else:
            val_interface.jsonpath = jsonpath
        
        val_interface.apply_validation(harvester)
    
    
    group_manipulator = GroupManipulator()
    
    print(group_manipulator)
    group_manipulator.add_groups_to_harvester(harvester)
    
    freeze_nuisances(harvester)
    scale_higgs_mass(harvester)
    
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
    output_rootfile = os.path.join(outdir, output_rootfile)

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
    optional_group.add_option("-s", "--rebin-scheme",
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
                        # type = "str"
                    )
    optional_group.add_option("--apply-validation",
                        help = " ".join(
                            """
                            apply results obtained by ValidateDatacards.py
                            """.split()
                        ),
                        dest = "apply_validation",
                        action = "store_true",
                        default = False
                        # type = "str"
                    )
    optional_group.add_option("--jsonpath",
                        help = " ".join(
                            """
                            use this .json file as output of ValidateDatacards.py.
                            If not provided, the output is generated automatically
                            """.split()
                        ),
                        dest = "validation_jsonpath",
                        type = "str"
                    )
    parser.add_option_group(optional_group)
    options, files = parser.parse_args()

    cardpath = options.datacard
    if not cardpath:
        parser.error("You need to provide the path to a datacard!")
    elif not os.path.exists(cardpath):
        parser.error("Could not find datacard in '{}'".format(cardpath))
    
    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(**vars(options))