################################################################
# wrapper to call PlotScript.py for different channels         #
################################################################

import os
import sys
import json
from optparse import OptionParser
from subprocess import call
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

thisdir = os.path.dirname(os.path.realpath(__file__))

cmd_base_parts = "python {scriptpath} -p {plotconfigpath}".split()
cmd_base_parts += "-w . --selectionlabel {label}".split()
cmd_base_parts += "--combineflag {flag} -r {rootfile}".split()
cmd_base_parts += "--channelname {channel}".split()
cmd_base_parts += "--combineDatacard {datacard}".split()
cmd_base_parts += "--pdfname {pdfname}".split()
cmd_base_parts += '--xLabel "{xtitle}"'.split()
#cmd_base_parts += "--skipErrorbands --pdftag noError".split()
# cmd_base_parts += "--dontScaleSignal".split()

cmd_base = " ".join(cmd_base_parts)

def parse_arguments():
    usage = """
    small utility to draw prefit/postfit plots using 'PlotScript.py'
    Inteded to draw from combine outputs but can be extended to draw
    from source root files (not implemented yet)
    python %prog [options]
    """
    parser = OptionParser(usage = usage)

    parser.add_option(  "-l", "--labelconfig",
                        help = " ".join("""
                            config containing the top and bottom lines
                            for labels to be printed on the plots. Will
                            be inserted in the 'splitlines' routine
                            """.split()),
                        dest = "labelconfig",
                        metavar = "path/to/config.json",
                        type = "str"
                    )
    parser.add_option(  "-p", "--plotconfig",
                        help = " ".join("""
                            path to plotconfig for PlotScript.py
                            """.split()),
                        dest = "plotconfig",
                        metavar = "path/to/config.py",
                        type = "str"
                    )

    parser.add_option(  "-s", "--sourcefile",
                        help = " ".join("""
                            input .root file to draw from
                            """.split()),
                        dest = "sourcefile",
                        metavar = "path/to/fitDiagnostics.root",
                        type = "str"
                    )

    parser.add_option(  "-d", "--datacard",
                        help = " ".join("""
                            path to datacard to load original binning
                            for plots.
                            """.split()),
                        dest = "datacard",
                        metavar = "path/to/datacard.txt",
                        type = "str"
                    )
    parser.add_option( "--lumiLabel",
                       help = "overwrite lumi label with this string",
                       dest = "lumiLabel",
                       type = "str"
                    )
    parser.add_option( "--drawFromHarvester", 
                        dest="drawFromHarvester", 
                        default = False,
                        action = "store_true", 
                        help = "use output of 'PostFitShapesFromWorkspace' in CombineHarvester package as input"
                    )
    parser.add_option( "--multisignal", 
                        dest="multisignal", 
                        default = False,
                        action = "store_true", 
                        help = "draw multiple signals"
                    )
    parser.add_option( "-u", "--unblind", 
                        dest="unblind", 
                        default = False,
                        action = "store_true", 
                        help = "unblind the distributions, i.e. draw points for observed data"
                    )
    parser.add_option( "--hide-signal", 
                        dest="hide_signal", 
                        default = False,
                        action = "store_true", 
                        help = "hide the signal in the post-fit distributions"
                    )
    parser.add_option("--divideByBinWidth", dest = "divideByBinWidth", default = False, action = "store_true", 
        help = "divide content by bin width")
    parser.add_option( "--prefix",
                        help = " ".join("""
                        prepend this prefix to the individual channel names
                        specified in the label config, e.g. ttH_2016 etc.
                        """.split()),
                        dest = "prefix",
                        type = "str",
                        default = ""
                    )
    parser.add_option( "--total",
                        help = " ".join("""
                        Draw the total (i.e. summed) distributions, which don't
                        follow the same naming scheme as the individual channels
                        per year. Note that the file name provided with option 's'
                        is presumed to be the actual channel name in this case. 
                        """.split()),
                        dest = "total",
                        action="store_true",
                        default = False,
                    )
    
    options, files = parser.parse_args()
    if not os.path.exists(options.labelconfig):
        parser.error("Could not find config in '{}'".format(options.labelconfig))
    
    if not os.path.exists(options.plotconfig):
        parser.error("Could not find plot config in '{}'".format(options.labelconfig))
    return options, files

def load_file_keys(file):
    rfile = ROOT.TFile.Open(file)
    if rfile.IsOpen() and not rfile.IsZombie() and not rfile.TestBit(ROOT.TFile.kRecovered):
        return [x.GetName() for x in rfile.GetListOfKeys() if x.IsFolder()]


def generate_plots(file, options):
    # dictionary containing the information from config
    # keys are channel names in source.root file

    # load keys to avoid running command for missing channels
    source_channel_list = load_file_keys(file)
    labels = {}
    configpath = options.labelconfig
    with open(configpath) as f:
        labels = json.load(f)
    
    base_options = {
        "scriptpath" : os.path.join(thisdir, "PlotScript.py"),
        "plotconfigpath" : options.plotconfig,
        "rootfile" : file,
        "datacard" : options.datacard
    }
    label_base = '"\splitline{{ {top} }}{{ {bottom} }}"'
    # dictionary with combineflags for PlotScript.py
    # keys are the combineflag names, items are the label
    # to be printed on the canvas
    flags = {
        "shapes_prefit": "prefit",
        "shapes_fit_s" : "postfit"
    }
    prefix = options.prefix

    # filter relevant channels for more efficiency
    relevant_channels = list()
    basename = os.path.basename(file)
    lambda_func = lambda x: True
    if options.total:
        lambda_func = lambda x: x in basename
    else:
        lambda_func = lambda x: x in source_channel_list
    relevant_channels = list(filter(lambda_func, labels.keys()))
    for channel in relevant_channels:
        final_channel = channel if prefix == "" \
                            else "_".join([prefix, channel])
        final_pdfname = final_channel
        if options.total:
            final_channel = "total"
            
        top = labels[channel].get("top", "")
        bottom = labels[channel].get("bottom", "")
        
        xtitle = labels[channel].get("xtitle", "ANN Discriminant")
        unit = labels[channel].get("unit")
        ratio_range = labels[channel].get("range", 0.18)
        for flag in flags:
            # pdfname = "{}_{}.pdf".format(channel, flag)
            final_bottom = " ".join([bottom, flags[flag]])
            label = label_base.format(top = top, bottom = final_bottom)
            cmd = cmd_base.format( channel = final_channel,
                                    label = label,
                                    flag = flag,
                                    pdfname = final_pdfname,
                                    xtitle = xtitle,
                                    **base_options)
            if unit:
                cmd += " --unit '{}'".format(unit)
            if not options.unblind:
                cmd += " --plot-blind"
            if options.lumiLabel:
                cmd += ' --lumilabel "{}"'.format(options.lumiLabel)
            if options.drawFromHarvester:
                cmd += " --drawFromHarvester"
            if options.multisignal:
                cmd += " --multisignal"
            if options.divideByBinWidth:
                cmd += " --divideByBinWidth"
            if flag == "shapes_fit_s":
                cmd += " --ratio-lower-bound {}".format(1-ratio_range)
                cmd += " --ratio-upper-bound {}".format(1+ratio_range)
                if options.hide_signal:
                    cmd += " --hide-signal"
            print(cmd)
            call([cmd], shell = True)

def main(options, files):
    for fpath in files:
        if not os.path.exists(fpath):
            print("ERROR: file '{}' doesn't exist! Skipping".format(fpath))
            continue
        generate_plots(file = fpath, options = options)

if __name__ == "__main__":
    opts, files = parse_arguments()
    files = [opts.sourcefile]
    main(opts, files)
