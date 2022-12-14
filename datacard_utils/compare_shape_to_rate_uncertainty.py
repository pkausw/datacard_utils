from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import ROOT
from tqdm import tqdm
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
    # print((json.dumps(cardpaths, indent = 4)))
    # exit()
    return cardpaths

def setup_histo_style(hist, color, line_style=1, line_width=3):
    """
    simple function to setup style of histograms. Current things that
    can be set: line color, line style, line width
    """

    hist.SetLineColor(color)
    hist.SetMarkerColor(color)
    hist.SetLineStyle(line_style)
    hist.SetLineWidth(line_width)
    hist.SetStats(False)

def reset_bin_errors(hist):
    nbins = hist.GetNbinsX()
    for i in range(1, nbins+1):
        hist.SetBinError(i, 0)

def create_shape_comparison(
    nominal_shape,
    uncertainty,
    compatible_list,
    outname,
    threshold = 0.05
):
    """
    function to create shape comparison plots. The plots are created for the
    sum of all processes in the harvester instance *harvester*. First, the
    varied templates are loaded. Afterwards, the integral for the up and down
    variation are calculated. The nominal shapes are weighted with these values
    to create the baseline for the comparison with a flat rate.

    Finally, the KS score with the baseline for the flat rate change w.r.t.
    the corresponding varied template is calculated. The plot contain all
    four histograms, as well as the KS score
    """

    canvas = helper.getRatioCanvas()

    # first, get the integral from the nominal template
    nom_int = nominal_shape.Integral()

    hists = []
    ratios = []
    legend = ROOT.TLegend(0.6,0.7,0.9,0.9)
    colors = [ROOT.kRed, ROOT.kBlue]

    setup_histo_style(nominal_shape, ROOT.kBlack)
    # draw nominal shape
    nominal_shape.Draw("HISTE")

    # draw nominal ratio, i.e. line at 1
    nom_ratio = nominal_shape.Clone("nominal_ratio")
    nom_ratio.Divide(nominal_shape)
    
    canvas.cd(2)
    y_axis = nom_ratio.GetYaxis()
    y_axis.SetRangeUser(0.8,1.2)
    y_axis.SetTitle("#frac{Variation}{Nominal}")
    y_axis.CenterTitle(True)
    y_axis.SetLabelSize(y_axis.GetLabelSize()*2.2)
    y_axis.SetTitleSize(y_axis.GetTitleSize()*2)
    y_axis.SetNdivisions(505)
    nom_ratio.SetTitle("")
    nom_ratio.Draw("HIST")
    compatible_with_rate = True
    # add nominal shape to legend
    legend.AddEntry(nominal_shape, "Nominal", "l")

    # make sure we start in the upper part of the canvas
    canvas.cd(1)

    # loop over the variations. First, load the varied templates and the scale
    # of the variation. Then restore the original varied template and construct
    # a template corresponding to a flat rate change of the nominal template.
    # Finally, calculate the KS score and put everything on the canvas
    for var, col in zip(["up", "down"], colors):

        if var == "up":
            histfunc = uncertainty.ShapeUAsTH1F
            valfunc = uncertainty.value_u
        elif var == "down":
            histfunc = uncertainty.ShapeDAsTH1F
            valfunc = uncertainty.value_d

        # load varied shape and the scale of the uncertainty
        # note: the shape is normalized to one and the scale of the
        # uncertainty is the fraction of the integral of the original
        # variation over the nominal integral
        var_shape = histfunc()
        var_value = valfunc()

        # setup style for this varied shape
        setup_histo_style(var_shape, col)

        # restore original varied template
        var_shape.Scale(var_value*nom_int)
        newname = "clone_{}_{}".format(var_shape.GetName(), var)
        # print("creating new histogram '{}'".format(newname))
        hists.append(var_shape.Clone(newname))
        var_shape = hists[-1]
        var_shape.Draw("SameHISTE")

        # save restored shape for ratio plot
        # hists.append(
        #     var_shape.Clone("clone_{}_{}".format(var_shape.GetName(), var))
        # )

        #create flat rate
        hists.append(nominal_shape.Clone("flat_rate_{}".format(var)))
        flat_rate = hists[-1]
        flat_rate.Scale(var_value)
        reset_bin_errors(flat_rate)
        setup_histo_style(flat_rate, col, 2)

        # calculate KS Score
        ks_score = var_shape.KolmogorovTest(flat_rate)

        # if KS score is below the threshold, mark this uncertainty as
        # incompatible with a flat rate change

        if ks_score < threshold:
            compatible_with_rate = False

        # draw the histograms
        flat_rate.Draw("SameHISTE")

        # create entry in legend
        entry = "Variation {} (Scale: {:.2f})".format(var, var_value)
        entry_ks = "Flat rate, KS Score: {:.2f}".format(ks_score)
        print(entry)
        print(entry_ks)

        legend.AddEntry(var_shape, entry, "l")
        legend.AddEntry(flat_rate, entry_ks, "l")

        hists.append(var_shape.Clone("clone_{}_{}".format(var_shape.GetName(), var)))

    # draw legend on canvas
    legend.Draw("Same")

    # build ratio plots
    canvas.cd(2)
    
    # loop through all saved histograms and build the ratio to the nominal
    for h in hists:
        ratios.append(h.Clone("ratio_{}".format(h.GetName())))
        ratios[-1].Divide(nominal_shape)
        ratios[-1].Draw("SameHISTE")
    
    #save the plots
    for ext in "pdf png".split():
        final_name = "{}.{}".format(outname,ext)
        # print("saving {}".format(final_name))
        canvas.SaveAs(final_name)
    
    # reset canvas for next systematic
    canvas.Clear()
    if compatible_with_rate:
        compatible_list.append(uncertainty.name())

def update_compatible_dict(
    compatible_dict, 
    uncertainties, 
    processes, 
    bin_name
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
    # print(json.dumps(compatible_dict, indent=4))
    print("updating comparison json")
    pbar_unc = tqdm(uncertainties)
    for unc in pbar_unc:
        pbar_unc.set_description("updating uncertainty '{}'".format(unc))
        # check if this uncertainty is already recorded. If yes, add the current 
        # list of processes. If not, create a new entry
        toplevel = compatible_dict.get(unc)
        if isinstance(toplevel, dict):
            
            # try to load the entry for the current bin name
            # if this succeeds, there is already list of processes
            # which we want to extend. If not, we simply add the current list
            # of processes
            binlevel = toplevel.get(bin_name)
            if isinstance(binlevel, list):
                # print("found existing list of processes, will combine")
                # print(binlevel)
                # print(processes)
                compatible_dict[unc][bin_name] = list(set(binlevel + processes))
            else:
                # print("adding new list of processes for bin name '{}'".format(bin_name))
                # print(processes)
                toplevel[bin_name] = processes
        else:
            # print("adding new uncertainty '{}'".format(unc))
            compatible_dict[unc] = dict()
            compatible_dict[unc][bin_name] = processes



def do_shape_comparisons(
    harvester,
    processes,
    uncertainties,
    outdir,
    outname,
    compatible_dict,
):
    """
    function to manage shape comparison plots. The function loops through all
    bins in the harvester instance and creates the shape comparisons for
    each process in the list of processes (*processes*) and each uncertainty in
    *uncertainties*.
    """

    pbar_bins = tqdm(harvester.bin_set())
    for b in pbar_bins:
        bin_harvester = harvester.cp().bin([b])
        pbar_bins.set_description("doing bin {}".format(b))
        pbar_procs = tqdm(processes)
        for proc in pbar_procs:
            # print("hello")
            pbar_procs.set_description("doing processes {}".format(proc))
            # slice harvester instance to processes that match *proc* 
            process_harvester = bin_harvester.cp().process([proc])
            process_list = process_harvester.process_set()
            # load nominal shape
            nominal_shape = process_harvester.GetShape()

            # set to safe names of uncertainties that are compatible with a 
            # flat rate change
            compatible_uncertainties = list()

            #create the comparison for each uncertainty
            pbar_unc = tqdm(uncertainties)
            for unc in pbar_unc:
                # print("unc hello")
                pbar_unc.set_description("doing uncertainty '{}'".format(unc))
                parts = [outname, b, helper.treat_special_chars(proc), '{}']
                final_outname = os.path.join(outdir, "__".join(parts))
                process_harvester.cp().syst_type(["shape"]).syst_name([unc]).ForEachSyst(
                    lambda syst: create_shape_comparison(
                            nominal_shape = nominal_shape,
                            uncertainty = syst,
                            compatible_list = compatible_uncertainties,
                            outname = final_outname.format(syst.name())
                        )
                )
            
            # update the dictionary with the parameters that are compatible 
            # with a flat rate change
            update_compatible_dict(
                compatible_dict=compatible_dict,
                uncertainties=compatible_uncertainties,
                processes=process_list,
                bin_name=b
            )
            

def start_comparison(filepath, **kwargs):
    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    harvester.SetFlag("workspaces-use-clone", True)
    harvester.SetFlag("filters-use-regex", True)

    # groups = kwargs.get("input_groups", [])
    
    # harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    # cardpaths = load_datacards(groups, harvester)
    harvester.ParseDatacard(filepath)
    outname = kwargs.get("outname")
    outdir = kwargs.get("outdir")
    compatible_dict = kwargs.get("compatible_dict", {})

    # load information about processes and uncertainties
    processes = kwargs.get("processes", [])
    uncertainties = kwargs.get("uncertainties", [])

    # do actual shape comparison
    do_shape_comparisons(
        harvester = harvester,
        processes = processes,
        uncertainties = uncertainties,
        outdir = outdir,
        outname=outname,
        compatible_dict=compatible_dict
    )

def write_output_file(final_dict, json_outname, outdir):
        
    # construct output path for json file
    json_outname = os.path.join(outdir, json_outname)
    if not json_outname.endswith(".json"): json_outname += ".json"

    # print("will save compatibility json here: '{}'".format(json_outname))
    with open(json_outname, "w") as f:
        json.dump(final_dict, f, indent = 4, separators = (',', ': '))

def main(*files, **kwargs):
    # setup directory for outputs
    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    # first, create dictionary that saves the parameters that are
    # compatible with a flat rate change using a KS score
    compatible_dict = {}

    # now loop through all files (the datacards) and do the comparison
    for f in files:
        if not os.path.exists(f):
            print("File '{}' does not exist, skipping")
            continue
        start_comparison(f, compatible_dict = compatible_dict, **kwargs)

    # if there were any uncertainties that are compatible with a flat rate
    # change, safe them in the correct format. This requires an additional
    # layer in the dictionary, 'smallShapeEff'
    comparison_outname = kwargs.get("json_outname", "compatible")
    if len(compatible_dict) > 0:

        write_output_file(final_dict = {"smallShapeEff": compatible_dict}, 
                            json_outname = comparison_outname, 
                            outdir = outdir
        )
    else:
        print("comparison json does not contain any entries")

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
    optional_group.add_option("-n", "--outname",
                        help = " ".join(
                            """
                            prefix to use in the naming of the final plots.
                            The format of the plot names is 
                            'PREFIX__CHANNEL__PROCESS__SYSTNAME.pdf'
                            Default for PREFIX is 'comparison'
                            """.split()
                        ),
                        dest = "outname",
                        type = "str",
                        default = "comparison"
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
