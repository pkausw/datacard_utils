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
from glob import glob
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
from manipulator_methods.common_manipulations import CommonManipulations


def scale_higgs_mass(harvester, base_mass = 125):
    mass_scaler = MassManipulator()
    mass_scaler.apply = True
    mass_scaler.basemass = base_mass
    
    mass_scaler.ScaleMasses(harvester)

def remove_minor_JEC(harvester):
    processes = """ttbarZ ttbarW zjets wjets diboson 
                tHW tHq ttbarGamma VH_hbb""".split()
    for decay in "hbb hcc hzg hgluglu hgg hww htt hzz".split():
        for proc in "tHq tHW".split():
            processes.append("{}_{}".format(proc, decay))
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

def do_validation(harvester, cardpaths, jsonpath):
    val_interface = ValidationInterface()
    val_interface.remove_small_signals = True
    val_interface.verbosity = 80
    for era in cardpaths:
        cards = cardpaths[era]
        print("applying validation to paths")
        print("\n".join(cards))
        for cardpath in cardpaths[era]:
            if not jsonpath:
                val_interface.generate_validation_output(cardpath)
            else:
                val_interface.jsonpath = jsonpath
            
            val_interface.apply_validation(harvester, eras = [era])
            print("="*130)
            print("after validation interface")
            harvester.cp().era([era]).PrintProcs()
            print("="*130)


def load_datacards(groups, harvester):

    cardpaths = {}
    for group in groups:
        template, wildcard = group.split(":")
        cards = glob(wildcard)
        print("template: {}".format(template))
        for f in cards:
            print("loading '{}'".format(f))
            harvester.QuickParseDatacard(f, template)
            eras = harvester.era_set()
            for e in eras:
                if e in f:
                    if not e in cardpaths:
                        cardpaths[e] = []
                    print("saving path '{}' for era '{}'".format(f, e))
                    cardpaths[e].append(f)
    print(json.dumps(cardpaths, indent = 4))
    # exit()
    return cardpaths

def write_datacards(harvester, outdir, prefix, rootfilename, era, \
                    combine_cards = True):
    
    common_manipulations = CommonManipulations()
    common_manipulations.apply_common_manipulations(harvester)
    # harvester.PrintSysts()
    group_manipulator = GroupManipulator()
    
    print(group_manipulator)
    group_manipulator.add_groups_to_harvester(harvester)

    channels = harvester.channel_set()
    card_dir = os.path.join(outdir, "datacards")
    if not os.path.exists(card_dir):
        os.mkdir(card_dir)
    
    output_rootfile = "{}_{}".format(prefix, rootfilename) \
                        if prefix else rootfilename
    output_rootdir = os.path.join(outdir, "rootfiles")
    if not os.path.exists(output_rootdir):
        os.mkdir(output_rootdir)
    output_rootfile = os.path.join(output_rootdir, output_rootfile.replace(".root", "{}.root".format(era)))
    
    outfile = ROOT.TFile.Open(output_rootfile, "RECREATE")

    if combine_cards:
        for chan in channels:
            cardname = os.path.join(card_dir, "combined_{}_{}.txt".format(chan, era))
            harvester.cp().channel([chan]).WriteDatacard(cardname, outfile)
        
        if "SL" in channels and "DL" in channels:
            cardname = os.path.join(card_dir, "combined_{}_{}.txt".format("DLSL", era))
            harvester.cp().channel("SL DL".split()).WriteDatacard(cardname, outfile)

        cardname = os.path.join(card_dir, "combined_{}_{}.txt".format("full", era))
        harvester.cp().WriteDatacard(cardname, outfile)
    else:
        bins = harvester.bin_set()
        for b in bins:
            cardname = os.path.join(card_dir, "{}.txt".format(b))
            print("writing card for bin '{}' in dir '{}'".format(b, cardname))
            harvester.cp().bin([b]).WriteDatacard(cardname, outfile)
    
def main(**kwargs):

    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    harvester.SetFlag("workspaces-use-clone", True)

    groups = kwargs.get("input_groups", [])
    
    # harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    cardpaths = load_datacards(groups, harvester)

    # harvester.PrintAll()

    
    rebin_scheme = kwargs.get("scheme", None)
    if rebin_scheme:
        bin_manipulator = BinManipulator()
        bin_manipulator.scheme = rebin_scheme
        harvester = bin_manipulator.rebin_shapes(harvester = harvester)
    

    remove_minor_jec = kwargs.get("remove_minor_jec", False)
    if remove_minor_jec:
        remove_minor_JEC(harvester)

    apply_validation = kwargs.get("apply_validation")
    if apply_validation:
        jsonpath = kwargs.get("validation_jsonpath")

        do_validation(  harvester = harvester,
                        cardpaths = cardpaths,
                        jsonpath = jsonpath )
    
    print("="*130)
    print("back in dc_manipulator::main")
    harvester.PrintProcs()
    scale_higgs_mass(harvester)
    prefix = kwargs.get("prefix")
    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    output_rootfile = kwargs.get("output_rootpath")
    if output_rootfile is None:
        output_rootfile = "all_shapes.root"
    eras = harvester.era_set()
    combine_cards = kwargs.get("combine_cards", False)
    if combine_cards:
        for e in eras:
            write_datacards(harvester = harvester.cp().era([e]), outdir = outdir, 
                            rootfilename = output_rootfile, prefix = prefix, era = e)
        
        write_datacards(harvester = harvester, outdir = outdir, rootfilename = output_rootfile, 
                        prefix = prefix, era = "all_years")
    else:
        for e in eras:
            era_dir = os.path.join(outdir, e)
            if not os.path.exists(era_dir):
                os.mkdir(era_dir)
            write_datacards(harvester = harvester.cp().era([e]), outdir = era_dir, 
                            rootfilename = output_rootfile, prefix = prefix, era = e,
                            combine_cards = False)


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
    parser.add_option("-i", "--input",
                        help = " ".join(
                            """
                            define groups of inputs. The format should be like
                            'SCHEME:wildcard/to/input/files*.txt'
                            """.split()
                        ),
                        dest = "input_groups",
                        metavar = "SCHEME:path/to/datacard",
                        type = "str",
                        action = "append"
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
    optional_group.add_option("--combine-cards",
                        help = " ".join(
                            """
                            combine datacards across channels.
                            If False, the script will create
                            a datacard for each of the input
                            categories. Default: False
                            """.split()
                        ),
                        dest = "combine_cards",
                        action = "store_true",
                        default = False
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
    main(**vars(options))