import os
import sys
import json
import re
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

from optparse import OptionParser
from itertools import cycle
from tqdm import tqdm

color_wheel = [
    ROOT.kRed,
    ROOT.kBlue,
    ROOT.kSpring+2,
    ROOT.kBlack
]


def create_color_dict(processes):
    """
    function to create fixed mapping of processes and colors. If the list
    of processes is longer than the internal list *color_wheel*, the colors
    are cycled using :py:func:`itertools.cycle`. Raises an error if no
    processes could be found.
    """
    # check whether there are any processes to map
    if len(processes) == 0:
        raise ValueError("Could not load any processes!")
    
    # do the mapping
    return {p: color for p, color in zip(sorted(processes), cycle(color_wheel))}


def matchup_channel_list(input_list, filter_list):
    """
    function to match-up an input list with a list of filters.
    The filters can include regex, so we need to loop through the list
    *filter_list* and apply the selection. Final output is the list of the
    set of channels in *input_list* that match the criteria in *filter_list*
    """
    # create final set with filtered values
    filtered_list = set()
    
    # loop through all regular expression in *filter_list* and evaluate
    # the regex
    for reg in filter_list:
        r = re.compile(reg)
        filtered_list |= set(filter(r.match, input_list))

    # return the set of filtered channels as list
    return sorted(list(filtered_list))

def setup_default_histogram(name, bin_labels, color, line_style=1):
    """
    function to create a histogram with *nbins* as the number of bins and
    with a style specified by *color* and *line_style*
    """
    nbins = len(bin_labels)

    h = ROOT.TH1F(name, "", nbins, 0, nbins)
    h.SetLineColor(color)
    h.SetMarkerColor(color)
    h.SetLineStyle(line_style)
    h.SetStats(False)
    for i, label in enumerate(bin_labels, 1):
        h.GetXaxis().SetBinLabel(i, label)
    return h

def create_histogram(value_dict, channels, process, color):
    """
    function to create histograms for the up/down variations for a given 
    process *process* with a color *color*. The length of the list *channels*
    is used for the number of bins. 
    Returns the histograms for the up and down variation as well as a string
    for the legend. 
    """
    # initialize ROOT histograms. The name is 'PROCESS__DIRECTION', where
    # 'PROCESS' is the process name and 'DIRECTION' is up or down
    hname_template = "__".join([process, "{}"])
    hname_up = hname_template.format("up")
    h_up = setup_default_histogram(
        name=hname_up, 
        bin_labels=channels, 
        color=color
    )
    h_down = setup_default_histogram(
        name=hname_template.format("down"), 
        bin_labels=channels, 
        color=color, 
        line_style=2
    )

    pbar_channels = tqdm(enumerate(channels))
    for i, chan in pbar_channels:
        pbar_channels.set_description("setting up channel '{}'".format(chan))
        values = value_dict[chan].get(process)
        if not isinstance(values, list):
            continue
        
        # unpack values for easier access
        up, down = tuple(values)
        h_up.SetBinContent(i, up)
        h_down.SetBinContent(i, down)
    
    # return a dictionary
    return {
        "{} (up)".format(process): h_up,
        "{} (down)".format(process): h_down
    }



def create_comparison_plot(
    value_dict,
    channels,
    color_dict,
    outname,
    exts=["pdf", "png"]
):
    """
    function to create a comparison plot for the lnN factors in *value_dict*.
    Only entries that are in the list *channels* and in the list of keys of
    *color_dict* are considered. The function creates histograms with 
    n bins, where n is the length of *channels*. Each bin displays the 
    up/down lnN factors for the processes in *color_dict*.
    Finally, the plot is saved with the name *outname* and the extensions
    in *exts*.
    """

    # create new ROOT Canvas
    c = ROOT.TCanvas()

    # dictionary to store histograms and there legend entry
    histo_dict = dict()

    # loop through the processes that we want to draw and create a histogram
    pbar_process = tqdm(color_dict.items())
    for process, color in pbar_process:
        pbar_process.set_description("Setting up histograms for '{}'".format(process))
        histo_dict.update(create_histogram(
            value_dict=value_dict,
            channels = channels,
            process = process,
            color = color,
        ))
    
    # create TLegend for histograms
    legend = ROOT.TLegend(0.6,0.7,0.9,0.9)

    # now draw all
    drawopt = "HIST" 
    for leg, hist in sorted(histo_dict.items(), key=lambda x: x[0]):
        hist.GetYaxis().SetRangeUser(0.5, 1.5)

        hist.Draw(drawopt)
        legend.AddEntry(hist, leg, "l")
        if not drawopt.endswith("Same"):
            drawopt += "Same"
    
    # draw a line at 1 to get a feeling for the directions in the plot
    line=ROOT.TLine(0, 1, len(channels), 1)
    line.SetLineStyle(3)
    line.SetLineColor(ROOT.kBlack)
    line.Draw("same")

    # finally, draw legend
    legend.Draw("Same")

    # save canvas with different extension
    for ext in exts:
        c.SaveAs(".".join([outname, ext]))



def create_comparison(fpath, color_dict, outdir, channels=[".*"]):
    """
    function to create comparison plots from the information contained in
    the summary .json file *fpath*. The function creates a histograms
    with a bin for each channel in *channels*. In each bin, the lnN values
    from the summary .json file are plotted for the individual processes
    """

    # open .json file
    input = {}
    with open(fpath) as f:
        input = json.load(f)
    
    # get correct input for lnN factors
    lnN_dict = input["lnN"]

    # the top-level keys are the uncertainty names
    available_uncertainties = list(lnN_dict.keys())

    # create nice progress bar for uncertainties
    pbar_unc = tqdm(available_uncertainties)
    
    # loop through the uncertainties and create the comparison plots
    for unc in pbar_unc:
        pbar_unc.set_description("Summarizing uncertainty '{}'".format(unc))

        # load information for this uncertainty
        unc_dict = lnN_dict[unc]

        # match-up list of available channels with list of channels that 
        # we want to actually plot (specified in *channels*)
        available_channels = list(unc_dict.keys())
        current_channels = matchup_channel_list(
            input_list=available_channels,
            filter_list=channels
        )

        # construct name for output plots
        outname = "comparison__{}".format(unc)
        outname = os.path.join(outdir, outname)

        # construct the plot for the list of interesting channels and processes
        create_comparison_plot(
            value_dict = unc_dict,
            channels = current_channels,
            color_dict = color_dict,
            outname = outname,
        )


def main(*files, **kwargs):
    # setup fixed mapping of processes an colors
    processes = kwargs.get("processes", [])
    color_dict = create_color_dict(processes)

    # load path to output directory
    outdir = kwargs.get("output_dir", ".")
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for f in files:
        if not os.path.exists(f):
            print("file '{}' does not exist, skipping".format(f))
        create_comparison(
            fpath=f,
            color_dict=color_dict,
            outdir=outdir,
            channels=[".*"]
        )


def parse_arguments():
    usage = "python %prog [options] path/to/summary_files.json"
    parser = OptionParser(usage=usage)

    parser.add_option("-p", "--process",
        help=" ".join("""
            Include this process in the comparison plot.
            Can be called multiple times
        """.split()),
        action="append",
        dest="processes",
    )

    parser.add_option("-o", "--output-dir",
        help=" ".join("""
            Save output in this directory. Defaults to current directory '.'
        """.split()),
        dest="output_dir",
        type="str",
        metavar="path/to/output_dir",
        default=".",
    )

    options, files = parser.parse_args()
    return files, options


if __name__ == '__main__':
    files, options = parse_arguments()
    main(*files, **vars(options))