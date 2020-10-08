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
# manipulator_dir = os.path.join(thisdir, "manipulator_methods")
# if not manipulator_dir in sys.path:
#     sys.path.append(manipulator_dir)

from manipulator_methods.group_manipulator import GroupManipulator
from manipulator_methods.scale_higgs_mass import MassManipulator
from manipulator_methods.rebin_distributions import BinManipulator
from manipulator_methods.apply_validation import ValidationInterface
from manipulator_methods.nuisance_manipulator import NuisanceManipulator

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

def remove_minor_JEC(harvester):
    processes = """ttbarZ ttbarW zjets wjets diboson tHq_hbb tHW_hbb 
                tHW tHq ttbarGamma VH_hbb""".split()
    
    params = """CMS_res_j*
        CMS_scaleAbsolute_j
        CMS_scaleAbsolute_j_*
        CMS_scaleBBEC1_j
        CMS_scaleBBEC1_j_*
        CMS_scaleEC2_j
        CMS_scaleEC2_j_*
        CMS_scaleFlavorQCD_j
        CMS_scaleHF_j
        CMS_scaleHF_j_*
        CMS_scaleRelativeBal_j
        CMS_scaleRelativeSample_j_*""".split()
    
    np_manipulator = NuisanceManipulator()
    bins = harvester.bin_set()
    if any(x.endswith("ttbbCR") for x in bins):
        print("This is the ttbbCR channel!")
        ttbbCR = [x for x in bins if x.endswith("ttbbCR")]
        to_remove = {}
        ttbbCR_processes = """ttbarZ ttbarW wjets tHq_hbb tHW_hbb 
                tHW tHq ttbarGamma VH_hbb""".split()
        for p in params:
            to_remove[p] = ttbbCR_processes
        np_manipulator.to_remove = to_remove
        np_manipulator.remove_nuisances_from_procs(harvester = harvester,
                                                bins = ttbbCR)
        bins = [x for x in bins if not x in ttbbCR]
    if not len(bins)== 0:
        to_remove = {}
        for p in params:
            to_remove[p] = processes
        np_manipulator.to_remove = to_remove

        np_manipulator.remove_nuisances_from_procs(harvester = harvester,
                                                    bins = bins)

def do_validation(harvester, cardpath, jsonpath):
    val_interface = ValidationInterface()
    val_interface.remove_small_signals = False
    if not jsonpath:
        val_interface.generate_validation_output(cardpath)
    else:
        val_interface.jsonpath = jsonpath
    
    val_interface.apply_validation(harvester)

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
    
    freeze_nuisances(harvester)
    scale_higgs_mass(harvester)

    remove_minor_jec = kwargs.get("remove_minor_jec", False)
    if remove_minor_jec:
        remove_minor_JEC(harvester)

    apply_validation = kwargs.get("apply_validation")
    if apply_validation:
        jsonpath = kwargs.get("validation_jsonpath")

        do_validation(  harvester = harvester,
                        cardpath = cardpath,
                        jsonpath = jsonpath )
    
    
    group_manipulator = GroupManipulator()
    
    print(group_manipulator)
    group_manipulator.add_groups_to_harvester(harvester)
       
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
    optional_group.add_option("--remove-minor-jec",
                        help = " ".join(
                            """
                            remove JEC uncertainties from minor backgrounds.
                            Default: False
                            Minor backgrounds are:
                            "ttbarZ ttbarW zjets wjets diboson tHq_hbb 
                            tHW_hbb ttbarGamma VH_hbb"
                            """.split()
                        ),
                        dest = "remove_minor_jec",
                        action = "store_true",
                        default = False
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