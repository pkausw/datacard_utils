from __future__ import absolute_import
from __future__ import print_function
import os
import sys
from turtle import update
import ROOT
import json
from tqdm import tqdm
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
base_dir = os.path.join(thisdir, "base")
if not base_dir in sys.path:
    sys.path.append(base_dir)

from helpfulFuncs import helpfulFuncs

helper = helpfulFuncs()


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

def update_compatible_dict(
    compatible_dict, 
    other_dict
):
    """
    function to update the dictionary for uncertainties compatible with a flat
    rate change recursively. Structure of the dictionary follows combine
    conventions and looks like this
    uncertainty: {
        bin: {
            list_of_processes
        }
    }
    """
    # loop through all uncertainties that are compatible with a flat rate
    # print(compatible_dict)
    # print(json.dumps(compatible_dict, indent=4))
    pbar_unc = tqdm(other_dict.keys())
    for unc in pbar_unc:
        pbar_unc.set_description("Looking for match for uncertainty '{}'".format(unc))

        # check if this uncertainty is already recorded. If yes, add the current 
        # list of processes. If not, create a new entry
        toplevel = compatible_dict.get(unc)
        if isinstance(toplevel, dict):
            # update the main dictionary. Each bin, i.e. channel name, 
            # should be unique. If a bin is already known, raise a KeyError
            pbar_bins = tqdm(other_dict[unc].keys())
            for b in pbar_bins:
                pbar_bins.set_description("Checking for instance of '{}'".format(b))
                if b in toplevel:
                    raise KeyError("Bin '{}' already known, something is wrong!".format(b))
                else:
                    compatible_dict[unc][b] = other_dict[unc][b]
        else:
            print("adding new uncertainty '{}'".format(unc))
            compatible_dict[unc] = other_dict.get(unc)
    return compatible_dict



def collect_information(
    harvester,
    processes,
    uncertainties,
    syst_types = ["lnN"],
    save_values = False
):
    """
    function to manage shape comparison plots. The function loops through all
    bins in the harvester instance and creates the shape comparisons for
    each process in the list of processes (*processes*) and each uncertainty in
    *uncertainties*.
    """

    info_dict = {}
    unc_harvester = harvester.cp().syst_type(syst_types).syst_name(uncertainties)
    this_uncertainties = unc_harvester.syst_name_set()
    pbar_unc = tqdm(this_uncertainties)
    for unc in pbar_unc:
        pbar_unc.set_description("Processing uncertainty {}".format(unc))
        bins = unc_harvester.cp().syst_type(syst_types).syst_name([unc]).bin_set()
        pbar_bin = tqdm(bins)
        unc_dict = {}
        for b in pbar_bin:
            pbar_bin.set_description("Processing channel {}".format(b))
            bin_harvester = unc_harvester.cp().syst_type(syst_types).syst_name([unc]).bin([b])
            
            # slice harvester instance to processes that match *proc* 
            process_harvester = bin_harvester.cp().process(processes)
            # set to safe names of uncertainties that are compatible with a 
            # flat rate change
            process_list = list() if not save_values else dict()

            #create the comparison for each uncertainty
        
            process_harvester.cp().ForEachSyst(
                lambda syst: process_list.append(syst.process())
                            if isinstance(process_list, list) else
                            process_list.update({syst.process(): [syst.value_u(), syst.value_d()]})
            )
            # from IPython import embed
            # embed()
            if len(process_list) > 0:
                unc_dict.update({b: process_list})
        if len(unc_dict) > 0:
            info_dict[unc] = unc_dict
    return info_dict

def find_differences_in_keys(dictionaries, reference, log, msg):
    keys = []
    for x in dictionaries:
        this_list = []
        if any(isinstance(x, t) for t in [list, set]):
            this_list = x
        else:
            this_list = x.keys()
        
        keys = list(set( keys + this_list))

    removed_keys = set(reference).symmetric_difference(set(keys))
    # from IPython import embed
    # embed()
    if not len(removed_keys) == 0:
        log.append(msg)
        log.append("\n".join(["\t{}".format(x) for x in sorted(removed_keys)]))
    else:
        log.append("{} None".format(msg))

def find_pruned_uncertainties(total_dict, uncertainties, processes, bins):
    log = []
    separator = "="*130
    log.append(separator)
    current_uncertainties = list(set(total_dict["shape"].keys() + total_dict["lnN"].keys()))

    find_differences_in_keys(
        [current_uncertainties],
        reference = uncertainties,
        log = log, 
        msg = "List of removed uncertainties:",
        
    )
    log.append(separator)
    pbar_shape = tqdm(current_uncertainties)
    for unc in pbar_shape:
        pbar_shape.set_description("Checking list of channels for uncertainty '{}'".format(unc))
        
        current_bins = list(
                        set(
                            total_dict["shape"].get(unc, {}).keys() + total_dict["lnN"].get(unc, {}).keys()
                            )
                        )
        find_differences_in_keys(
            [current_bins],
            reference = bins,
            log = log,
            msg = "Uncertainty '{}' was removed from following channels:".format(unc)
        )
        pbar_bins = tqdm(current_bins)
        for b in pbar_bins:
            pbar_bins.set_description("Checking processes in {}/{}".format(unc, b))
            # from IPython import embed
            # embed()
            find_differences_in_keys(
                [total_dict["shape"].get(unc, {}).get(b, []),
                total_dict["lnN"].get(unc, {}).get(b, [])],
                reference = processes,
                log = log,
                msg = "In bin '{}', uncertainy '{}' was removed from processes:".format(b, unc)
            )
    return log

    



def start_comparison(filepath, all_uncertainties, all_processes, all_bins, total_dict = {}, **kwargs):
    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    harvester.SetFlag("workspaces-use-clone", True)
    harvester.SetFlag("filters-use-regex", True)

    harvester.ParseDatacard(filepath)

    # load information about processes and uncertainties
    processes = kwargs.get("processes", [])
    print(processes)
    uncertainties = kwargs.get("uncertainties", [])

    # store information about processes, uncertainties and bins for later
    all_uncertainties = list(set(all_uncertainties + harvester.cp().syst_name(uncertainties).syst_name_set()))
    print(all_uncertainties)
    all_bins = list(set(all_bins + harvester.cp().bin_set()))
    all_processes = list(set(all_processes + harvester.cp().process(processes).process_set()))

    # collect information for different syst types
    shape_dict = collect_information(
            harvester = harvester,
            processes = processes,
            uncertainties = uncertainties,
            syst_types=["shape"]
        )
    print("="*130)
    print("update shape uncertainties with")
    total_dict["shape"] = update_compatible_dict(
                            total_dict.get("shape", {}), 
                            shape_dict
                        )
    
    lnN_dict = collect_information(
            harvester = harvester,
            processes = processes,
            uncertainties = uncertainties,
            syst_types=["lnN"],
            save_values=True
        )
    print("="*130)
    print("update lnN uncertainties")
    total_dict["lnN"] = update_compatible_dict(
                            total_dict.get("lnN", {}), 
                            lnN_dict
                        )
    return total_dict, all_uncertainties, all_bins, all_processes

def write_output_file(final_dict, outname, outdir, extension = "json"):
    
    # construct output path for file
    outname = os.path.join(outdir, outname)
    if not outname.endswith(extension): 
        outname = ".".join([outname, extension])

    print("will save file here: '{}'".format(outname))
    with open(outname, "w") as f:
        if extension == "json":
            json.dump(final_dict, f, indent = 4, separators = (',', ': '))
        else:
            f.write("\n".join(final_dict))

def main(*files, **kwargs):
    # setup directory for outputs
    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    # first, create dictionary that saves the parameters that are
    # compatible with a flat rate change using a KS score
    summary_dict = {}

    all_uncertainties = []
    all_processes = []
    all_bins = []
    # now loop through all files (the datacards) and do the comparison
    for f in files:
        if not os.path.exists(f):
            print("File '{}' does not exist, skipping")
            continue
        summary_dict, all_uncertainties, all_bins, all_processes = start_comparison(f, 
                                                                    all_uncertainties, 
                                                                    all_processes, 
                                                                    all_bins, 
                                                                    total_dict = summary_dict, 
                                                                    **kwargs)

    print("collected uncertainties")
    print(all_uncertainties)
    log_outname = kwargs.get("log_outname", "pruned_parameters")
    log = find_pruned_uncertainties(
            total_dict = summary_dict, 
            uncertainties = all_uncertainties, 
            processes = all_processes, 
            bins = all_bins)

    write_output_file(
        final_dict = log, 
        outname = log_outname, 
        outdir = outdir, 
        extension = "log" 
    )

    # if there were any uncertainties that are compatible with a flat rate
    # change, safe them in the correct format
    comparison_outname = kwargs.get("json_outname", "compatible")
    if len(summary_dict) > 0:
        write_output_file(final_dict = summary_dict, 
                            outname = comparison_outname, 
                            outdir = outdir
        )

def parse_arguments():
    usage = " ".join("""
    This tool compares shapes uncertainties with a 'flat' rate variation.
    First, the shapes are extracted from the datacard(s). Afterwards, the
    nominal shape for the respective (sum of) processes are scaled to match the
    integral of the varied templates. This is a 'flat' rate variation since
    this does not account for any shape effect introduced by the nuisance
    parameter.
    Finally, the flat rate variation is compared to the 'real' shape variation
    using a KS score. The script directly saves the list of uncertainties
    that are compatible with a flat rate change for further processing.

    This tool employs functions from the CombineHarvester package. 
    Please make sure that you have installed it!
    """.split())

    usage += """

    python %prog [options] path/to/datacards.txt
    """
    parser = OptionParser(usage = usage)

    parser.add_option("-p", "--process",
                        help = " ".join(
                            """
                            Do comparison for this (group of) processes.
                            Can be called multiple times.
                            Regex is allowed
                            """.split()
                        ),
                        dest = "processes",
                        type = "str",
                        action = "append"
                    )
    parser.add_option("-u", "--uncertainty",
                        help = " ".join(
                            """
                            Do comparison for this (group of) uncertainties.
                            Can be called multiple times.
                            Regex is allowed
                            """.split()
                        ),
                        dest = "uncertainties",
                        type = "str",
                        action = "append"
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

    optional_group.add_option("-j", "--json-outname",
                        help = " ".join(
                            """
                            output file name to use for .json file containing
                            the final list of uncertainties compatible with a 
                            flat rate change. Default: compatible_uncertainties
                            """.split()
                        ),
                        dest = "json_outname",
                        type = "str",
                        default = "compatible_uncertainties"
                    )
    
    
    parser.add_option_group(optional_group)
    options, files = parser.parse_args()
    
    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))
