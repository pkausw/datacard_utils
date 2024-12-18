from __future__ import absolute_import
from __future__ import print_function
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
from manipulator_methods.stxs_modifications import STXSModifications
from manipulator_methods.XS_interpretation import XSModifications
from manipulator_methods.fh_manipulations import FHmanipulations

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
    params = """CMS_res_j.*
        CMS_scale.*_j
        CMS_scale.*_j_.*
        """.split()
    
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

def do_validation(harvester, cardpaths, jsonpath, combine_channels=[]):
    val_interface = ValidationInterface()
    val_interface.remove_small_signals = True
    val_interface.remove_small_backgrounds = False
    val_interface.channels_to_combine = combine_channels
    harvester.SetFlag("filters-use-regex", True)
    # val_interface.verbosity = 80
    for era in cardpaths:
        cards = cardpaths[era]
        print("applying validation to paths")
        print(("\n".join(cards)))
        if not jsonpath:
            for cardpath in cardpaths[era]:
                val_interface.generate_validation_output(cardpath)
                val_interface.apply_validation(harvester, eras = [era])

        else:
            val_interface.jsonpath = jsonpath
            val_interface.apply_validation(harvester, eras = [era])


        print(("="*130))
        print("after validation interface")
        harvester.cp().era([era]).PrintProcs()
        print(("="*130))

def remove_minor_bkgs(harvester):
    val_interface = ValidationInterface()
    harvester.SetFlag("filters-use-regex", True)
    # val_interface.verbosity = 80
    era_set = harvester.era_set()
    if len(era_set) == 0:
        era_set = [".*"]
    channel_set = harvester.channel_set()
    if len(channel_set) == 0:
        channel_set = [".*"]
    for era in era_set:
        for channel in channel_set:
            bin_set = harvester.cp().era([era]).channel([channel]).bin_set()
            for b in bin_set:
                # drop minor processes for tHq
                print("pruning tHq")
                this_harvester = harvester.cp().era([era]).channel([channel]).bin([b])
                processes = this_harvester.cp()\
                                .process(["tHq.*"]).process_set()
                print(("pruning processes: {}".format(", ".join(processes))))
                val_interface.drop_small_processes(harvester = harvester,
                                                    era = [era],
                                                    chan = [channel],
                                                    bins = [b],
                                                    processes = processes)

                # drop minor processes for tHW
                print("pruning tHW")
                processes = this_harvester.cp()\
                                .process(["tHW.*"]).process_set()
                print(("pruning processes: {}".format(", ".join(processes))))
                val_interface.drop_small_processes(harvester = harvester,
                                                    era = [era],
                                                    chan = [channel],
                                                    bins = [b], 
                                                    processes = processes)

                # drop minor backgrounds, but protect tH processes
                # first, select all backgrounds that are not tH processes, 
                # then do check with this set of processes
                pure_bkg_harvester = this_harvester.cp()\
                                .backgrounds().process(["tH(q|W).*"], False)
                processes = pure_bkg_harvester.process_set()
                print(("pruning processes: {}".format(", ".join(processes))))
                # introduce special case for FH: subtraction for multijet estimation
                # doesn't work correctly if harvester is initialized with .txt file
                # Therefore, we need to subtract the CR templates by hand

                # introduce total yield
                tot_yield = None
                if any("FH" in x.upper() for x in [channel, b]):
                    print("Will check for FH hack!")
                    rate_data_CR = pure_bkg_harvester.cp().process(["data_CR"]).GetRate()
                    rate_other_CR = pure_bkg_harvester.cp().\
                                    process(["data_CR"], False).process([".*_CR"]).GetRate()
                    rate_sr = pure_bkg_harvester.cp().\
                                    process([".*_CR"], False).GetRate()
                    # if the yield of the MC templates in the CR is positive, 
                    # the minus sign is missing -> compute the yield by hand
                    if rate_other_CR > 0:
                        print("Calculating total yield manually")
                        print("\tyield(SR): {}".format(rate_sr))
                        print("\tyield(data CR): {}".format(rate_data_CR))
                        print("\tyield(other CR): {}".format(rate_other_CR))
                        tot_yield = rate_sr + rate_data_CR - rate_other_CR
                val_interface.drop_small_processes(harvester = harvester,
                                                    era = [era],
                                                    chan = [channel],
                                                    bins = [b],
                                                    processes = processes,
                                                    tot_yield = tot_yield)

                print(("="*130))
                print("after process pruning")
                harvester.cp().era([era]).PrintProcs()
                print(("="*130))

def load_datacards(groups, harvester):

    cardpaths = {}
    for group in groups:
        template, wildcard = group.split(":")
        cards = glob(wildcard)
        print(("template: {}".format(template)))
        for f in cards:
            print(("loading '{}'".format(f)))
            harvester.QuickParseDatacard(f, template)
            eras = harvester.era_set()
            for e in eras:
                if e in f:
                    if not e in cardpaths:
                        cardpaths[e] = []
                    print(("saving path '{}' for era '{}'".format(f, e)))
                    cardpaths[e].append(f)
    print((json.dumps(cardpaths, indent = 4)))
    # exit()
    return cardpaths

def write_harvester(harvester, cardname, outfile, group_manipulator):
    scale_higgs_mass(harvester)
    print(group_manipulator)
    group_manipulator.add_groups_to_harvester(harvester)
    print(("writing card '{}'".format(cardname)))
    # harvester.WriteDatacardWithFile(cardname, outfile)
    harvester.WriteDatacard(cardname, outfile)

def transpose_binning(harvester, binning_groups, unbind_eras=False):
    print(("will perform rebinning based on '{}'".format(binning_groups)))
    binning_harvester = ch.CombineHarvester()
    binning_harvester.SetFlag("allow-missing-shapes", False)
    binning_harvester.SetFlag("workspaces-use-clone", True)
    binning_harvester.SetFlag("filters-use-regex", True)
    p = load_datacards(binning_groups, binning_harvester)
    bin_manipulator = BinManipulator()
    eras = harvester.era_set()
    
    source_eras = binning_harvester.era_set()
    if unbind_eras and len(source_eras) != 1:
        raise RuntimeError(" ".join(
            """
            you unset the era lookup for transfering binnings between datacards,
            but the source includes multiple eras. This is not supported!
            """.split()))
    for e in eras:
        if not unbind_eras and not e in source_eras:
            print("Could not find era '{}' in source!")
            continue
        if not unbind_eras:
            current_binning_harvester = binning_harvester.cp().era([e])
        else:
            current_binning_harvester = binning_harvester
        source_bins = current_binning_harvester.bin_set()
        for s in source_bins:
            print(("checking bin '{}' for matches".format(s)))
            bins = harvester.cp().era([e]).bin([".*{}".format(s)]).bin_set()
            if len(bins) == 0:
                print(("WARNING: found no matches for bin {}".format(s)))
            else:
                source = current_binning_harvester.cp().bin([s])\
                                .backgrounds()
                h = source.GetShape()
                h.Print("Range")
                bin_manipulator.load_edges(h)
                for b in bins:
                    print(("Rebinning bin '{}'".format(b)))                  
                    print("applying this binning:")
                    print((bin_manipulator.bin_edges))
                    harvester.cp().bin([b]).era([e])\
                        .VariableRebin(bin_manipulator.bin_edges)
               
            
def write_datacards(harvester, outdir, prefix, rootfilename, era, \
                    group_manipulator, combine_cards = True,\
                    bgnorm_mode = "rateParams",
                    stxs_interface = None, xs_interface = None):
    
    common_manipulations = CommonManipulations()
    common_manipulations.bgnorm_mode = bgnorm_mode
    common_manipulations.apply_common_manipulations(harvester)
    # harvester.PrintSysts()
    if stxs_interface:
        stxs_interface.do_stxs_modifications(harvester)
    if xs_interface:
        xs_interface.do_xs_modifications(harvester)


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
            current_harvester = harvester.cp().channel([chan])
            cardname = os.path.join(card_dir, "combined_{}_{}.txt".format(chan, era))
            write_harvester(harvester = current_harvester,
                            cardname = cardname, outfile = outfile, 
                            group_manipulator = group_manipulator)
        
        if "SL" in channels and "DL" in channels:
            current_harvester = harvester.cp().channel("SL DL".split())
            cardname = os.path.join(card_dir, "combined_{}_{}.txt".format("DLSL", era))
            write_harvester(harvester = current_harvester,
                            cardname = cardname, outfile = outfile, 
                            group_manipulator = group_manipulator)

        cardname = os.path.join(card_dir, "combined_{}_{}.txt".format("full", era))
        write_harvester(harvester = harvester,
                            cardname = cardname, outfile = outfile, 
                            group_manipulator = group_manipulator)
    else:
        bins = harvester.bin_set()
        for b in bins:
            current_harvester = harvester.cp().bin([b])
            cardname = os.path.join(card_dir, "{}.txt".format(b))
            write_harvester(harvester = current_harvester,
                            cardname = cardname, outfile = outfile, 
                            group_manipulator = group_manipulator)

def invert_nuisance_directions(harvester, invertion_list):
    print(("inverting directions for list '{}'"\
                .format(", ".join([str(x) for x in invertion_list]))))
    
    harvester.cp().syst_name(invertion_list).PrintSysts()
    harvester.cp().syst_name(invertion_list).ForEachSyst(lambda x: x.SwapUpAndDown())
    harvester.cp().syst_name(invertion_list).PrintSysts()

def transfer_ue(target, transfer_from):
    source_harvester = ch.CombineHarvester()
    source_harvester.SetFlag("allow-missing-shapes", False)
    source_harvester.SetFlag("workspaces-use-clone", True)

    _ = load_datacards(transfer_from, source_harvester)
    eras = source_harvester.era_set()
    target_eras = target.era_set()
    if len(eras) != 1:
        raise NotImplementedError("Can only transfer UE uncertainty if one source era is given!")

    np_manipulator = NuisanceManipulator()

    # loop through the available source bins
    source_bins = source_harvester.bin_set()
    ue_wildcard = "CMS_ttHbb_UE.*"

    for b in source_bins:
        # load the processes for which UE is available in the source
        sub_source = source_harvester.cp().bin([b]).syst_name([ue_wildcard])
        np_manipulator.to_remove = {
            ue_wildcard: sub_source.process_set()
        }
        np_manipulator.remove_nuisances_from_procs(target, bins=[str(b)])

        for e in target_eras:
            for target_b in target.bin_set():
                sub_source.ForEachSyst(
                    lambda s: target.InsertSystematic(
                        np_manipulator.copy_and_rename(s, bin=target_b, era=e)
                    )
                )

def main(**kwargs):

    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    harvester.SetFlag("workspaces-use-clone", True)

    groups = kwargs.get("input_groups", [])
    
    # harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    cardpaths = load_datacards(groups, harvester)
    prefix = kwargs.get("prefix")
    outdir = kwargs.get("outdir")

    # harvester.PrintAll()

    make_tH_signal = kwargs.get("make_tH_signal", False)
    harvester.SetFlag("filters-use-regex", True)
    harvester.cp().process(["tH.*"])\
        .ForEachProc(lambda x: x.set_signal(make_tH_signal))
    harvester.cp().process(["tH.*"])\
        .ForEachSyst(lambda x: x.set_signal(make_tH_signal))
    
    transfer_ue_from = kwargs.get("transfer_ue_from", None)
    if transfer_ue_from:
        transfer_ue(target=harvester, transfer_from=transfer_ue_from)


    # binning related manipulations
    rebin_scheme = kwargs.get("scheme", None)
    check_mc = kwargs.get("check_mc", False)
    check_mc_data = kwargs.get("check_mc_data", False)
    binning_groups = kwargs.get("binning_groups", None)
    merge_n_bins = kwargs.get("merge_n_bins", None)
    unbind_binning_era = kwargs.get("unbind_binning_era", False)
    if binning_groups:
        transpose_binning(harvester, binning_groups, unbind_eras=unbind_binning_era)
    if rebin_scheme or check_mc or check_mc_data or merge_n_bins:
        bin_manipulator = BinManipulator()
        bin_manipulator.log_path = os.path.join(outdir, "rebin.log")
        if check_mc_data:
            bin_manipulator.threshold = "data"
            harvester = bin_manipulator.do_statistical_rebinning(harvester, processes = [".*"])
        if check_mc:
            threshold = kwargs.get("check_mc_threshold", 15)
            bin_manipulator.threshold = threshold
            harvester = bin_manipulator.do_statistical_rebinning(harvester)
        if rebin_scheme or merge_n_bins:
            bin_manipulator.scheme = rebin_scheme
            bin_manipulator.merge_n_bins = merge_n_bins
            harvester = bin_manipulator.rebin_shapes(harvester = harvester)
    
    remove_minor_jec = kwargs.get("remove_minor_jec", False)
    if remove_minor_jec:
        remove_minor_JEC(harvester)

    apply_validation = kwargs.get("apply_validation")
    prune_backgrounds = kwargs.get("remove_minor_bkgs", False)
    combine_channels = kwargs.get("combine_channels", [])
    if apply_validation:
        jsonpath = kwargs.get("validation_jsonpath")

        do_validation(  harvester = harvester,
                        cardpaths = cardpaths,
                        jsonpath = jsonpath,
                        combine_channels = combine_channels)
    if prune_backgrounds:
        remove_minor_bkgs(harvester)

    invert_directions = kwargs.get("invert_directions", [])

    if isinstance(invert_directions, list) and len(invert_directions) > 0:
        invert_nuisance_directions(harvester, invert_directions)
    
    print(("="*130))
    print("back in dc_manipulator::main")
    harvester.PrintProcs()

    if not os.path.exists(outdir):
        os.mkdir(outdir)
    output_rootfile = kwargs.get("output_rootpath")
    if output_rootfile is None:
        output_rootfile = "all_shapes.root"
    eras = harvester.era_set()
    combine_cards = kwargs.get("combine_cards", False)

    # check if the fix for the fh glusplit uncertainty needs to be applied
    fh_glusplit_fix = kwargs.get("fh_glusplit_fix", False)
    if fh_glusplit_fix:
        fh_manipulator = FHmanipulations()
        fh_manipulator.apply_glusplit_scalefactors(harvester)
    
    group_manipulator = GroupManipulator()

    stxs = kwargs.get("stxs", False)
    stxs_interface = None
    if stxs:
        stxs_interface = STXSModifications()

    xs_measurement = kwargs.get("xs_measurement", False)
    xs_interface = None
    if xs_measurement:
        xs_interface = XSModifications()

    bgnorm_mode = kwargs.get("bgnorm_mode", "rateParams")
    if combine_cards:
        for e in eras:
            write_datacards(harvester = harvester.cp().era([e]), outdir = outdir, 
                            rootfilename = output_rootfile, prefix = prefix, era = e, 
                            group_manipulator = group_manipulator, bgnorm_mode = bgnorm_mode,
                            stxs_interface = stxs_interface, xs_interface = xs_interface)
        
        write_datacards(harvester = harvester, outdir = outdir, rootfilename = output_rootfile, 
                        prefix = prefix, era = "all_years", 
                            group_manipulator = group_manipulator,
                            bgnorm_mode = bgnorm_mode,
                            stxs_interface = stxs_interface, xs_interface = xs_interface)
    else:
        for e in eras:
            era_dir = os.path.join(outdir, e)
            if not os.path.exists(era_dir):
                os.mkdir(era_dir)
            write_datacards(harvester = harvester.cp().era([e]), outdir = era_dir, 
                            rootfilename = output_rootfile, prefix = prefix, era = e,
                            combine_cards = False, 
                            group_manipulator = group_manipulator,
                            bgnorm_mode = bgnorm_mode,
                            stxs_interface = stxs_interface,
                            xs_interface = xs_interface)


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
    binning_options = OptionGroup(parser, "Options regarding the binning of templates")
    binning_options.add_option("-s", "--rebin-scheme",
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

    binning_options.add_option("-b", "--binning",
                        help = " ".join(
                            """
                            define groups of inputs to load binning from. 
                            The format should be like
                            'SCHEME:wildcard/to/input/files*.txt'.
                            The binning will be transfered between bins of
                            the same era by default.
                            """.split()
                        ),
                        dest = "binning_groups",
                        metavar = "SCHEME:path/to/datacard",
                        type = "str",
                        action = "append"
                    )

    binning_options.add_option("--unbind-binning-era",
                        help = " ".join(
                            """
                            deactivate the assertion that the binning is
                            transfered for bins of the same era. In this case,
                            the source defined by option '-b, --binning' can 
                            only contain _one_ era! Defaults to False
                            """.split()
                        ),
                        dest = "unbind_binning_era",
                        action = "store_true",
                        default = False,
                    )

    binning_options.add_option("--check-mc-binning",
                        help = " ".join(
                            """
                            rebin the shapes in the different channels
                            according to the MC stats in each bin of the
                            total background distributions. Default is False
                            """.split()
                        ),
                        dest = "check_mc",
                        action = "store_true",
                        default = False
                    )
    binning_options.add_option("--binning-threshold",
                        help = " ".join(
                            """
                            Use this threshold when checking the binning
                            according to the MC stats of the individual bins.
                            Default: 15
                            """.split()
                        ),
                        dest = "check_mc_threshold",
                        type = "float",
                        default = 15
                    )
    binning_options.add_option("--check-mc-binning-data",
                        help = " ".join(
                            """
                            rebin the shapes in the different channels
                            according to the coverage of data in each bin of the
                            total background distributions. Default is False
                            """.split()
                        ),
                        dest = "check_mc_data",
                        action = "store_true",
                        default = False
                    )

    binning_options.add_option("-m", "--mergeLastNbins",
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
    text = "Options regarding the validation of datacards"
    validation_options = OptionGroup(parser, text)
    validation_options.add_option("--apply-validation",
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
    validation_options.add_option("--jsonpath",
                        help = " ".join(
                            """
                            use this .json file as output of ValidateDatacards.py.
                            If not provided, the output is generated automatically
                            """.split()
                        ),
                        dest = "validation_jsonpath",
                        type = "str"
                    )
    validation_options.add_option("--combine-channels",
                        help = " ".join(
                            """
                            combine these channels when ratifying shape uncertainties.
                            Syntax should be a regular expression that matches
                            the channels you want to combine in the calculation
                            of the lnN factors, e.g. 'ljets_ge6j_.*STXS(0|1).*'.
                            When called multiple times, each entry is treated
                            independently. Therefore, the corresponding regexes
                            **must** be orthogonal!
                            """.split()
                        ),
                        action="append",
                        dest = "combine_channels",
                    )
    text = "Options to modify the stat. model in general"
    model_manipulations = OptionGroup(parser, text)
    model_manipulations.add_option("--remove-minor-jec",
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
    model_manipulations.add_option("--invert-directions",
                        help = " ".join(
                            """
                            invert direction for this nuisance.
                            Inputs are regex expressions to selection
                            nuisance parameters.
                            Can be called multiple times
                            """.split()
                        ),
                        dest = "invert_directions",
                        action = "append"
                        )
    model_manipulations.add_option("--make-tH-signal",
                        help = " ".join(
                            """
                            set the tH process to signal processes.
                            Default: False
                            """.split()
                        ),
                        dest = "make_tH_signal",
                        action = "store_true",
                        default = False
                    )
    model_manipulations.add_option("--remove-minor-bkgs",
                        help = " ".join(
                            """
                            remove backgrounds which contribute less than
                            0.1% to the overall background yield.
                            Note that the tH processes are protected and
                            are not considered as background in this check.
                            Default: False
                            """.split()
                        ),
                        dest = "remove_minor_bkgs",
                        action = "store_true",
                        default = False
                    )

    model_manipulations.add_option("--bgnorm-mode",
                        help = " ".join(
                            """
                            Choose the kind of parameters you would like
                            to use for the bgnorm parameters for ttbb and ttcc.
                            Current choices: {}. Default: rateParams
                            """.format(CommonManipulations.bgnorm_mode_choices())\
                                .split()
                        ),
                        dest = "bgnorm_mode",
                        choices = CommonManipulations.bgnorm_mode_choices(),
                        default = "rateParams"
                    )
    model_manipulations.add_option("--stxs",
                        help = " ".join(
                            """
                            apply stxs-specific modifications.
                            Default: False
                            """.split()
                        ),
                        dest = "stxs",
                        action = "store_true",
                        default = False
                    )
    model_manipulations.add_option("--xs-interpretation",
                        help = " ".join(
                            """
                            apply modifications for xs interpretation.
                            Default: False
                            """.split()
                        ),
                        dest = "xs_measurement",
                        action = "store_true",
                        default = False
                    )
    
    model_manipulations.add_option("--apply-fh-glusplit-fix",
                        help = " ".join(
                            """
                            apply the scale factors for the glusplit uncertainty
                            in the FH CR regions.
                            Default: False
                            """.split()
                        ),
                        dest = "fh_glusplit_fix",
                        action = "store_true",
                        default = False
                    )
    model_manipulations.add_option("--transfer-ue-from",
                        help = " ".join(
                            """
                            transfor lnN factors for UE from these 
                            datacards. Input is similar wildcard to 
                            option '-i'. Should contain only *one* era
                            to avoid ambiguities.
                            """.split()
                        ),
                        dest="transfer_ue_from",
                        metavar = "SCHEME:path/to/datacard",
                        type = "str",
                        action = "append",
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
    parser.add_option_group(model_manipulations)
    parser.add_option_group(validation_options)
    parser.add_option_group(binning_options)
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
