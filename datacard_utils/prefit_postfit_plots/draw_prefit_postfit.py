################################################################
# wrapper to call PlotScript.py for different channels         #
################################################################

import os
import sys
import json
from optparse import OptionParser
from subprocess import call

thisdir = os.path.dirname(os.path.realpath(__file__))

cmd_base_parts = "python {scriptpath} -p {plotconfigpath}".split()
cmd_base_parts += "-w . --selectionlabel {label}".split()
cmd_base_parts += "--combineflag {flag} -r {rootfile}".split()
cmd_base_parts += "--channelname {channel}".split()
cmd_base_parts += "--combineDatacard {datacard}".split()
cmd_base_parts += "--pdfname {pdfname}".split()
cmd_base_parts += '--xLabel "ANN Discriminant"'.split()
cmd_base_parts += ["--plot-blind"]
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
    
    options, files = parser.parse_args()
    if not os.path.exists(options.labelconfig):
        parser.error("Could not find config in '{}'".format(options.labelconfig))
    
    if not os.path.exists(options.plotconfig):
        parser.error("Could not find plot config in '{}'".format(options.labelconfig))
    return options, files

def generate_plots(file, options):
    # dictionary containing the information from config
    # keys are channel names in source.root file
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
    for channel in labels:
        top = labels[channel].get("top", "")
        bottom = labels[channel].get("bottom", "")
        final_channel = channel if prefix == "" \
                            else "_".join([prefix, channel])
        for flag in flags:
            # pdfname = "{}_{}.pdf".format(channel, flag)
            final_bottom = " ".join([bottom, flags[flag]])
            label = label_base.format(top = top, bottom = final_bottom)
            cmd = cmd_base.format( channel = final_channel,
                                    label = label,
                                    flag = flag,
                                    pdfname = final_channel,
                                    **base_options)
            if options.lumiLabel:
                cmd += ' --lumilabel "{}"'.format(options.lumiLabel)
            if options.drawFromHarvester:
                cmd += " --drawFromHarvester"
            if options.multisignal:
                cmd += " --multisignal"
            if options.divideByBinWidth:
                cmd += " --divideByBinWidth"
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
