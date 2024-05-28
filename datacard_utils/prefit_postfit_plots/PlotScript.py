#################################################################################################
# Utility to visualize process templates and uncertainties                                      #
# Project first started by Lea Reuter (KIT), Jan van der Linden (KIT) and Philip Keicher (KIT)  #
#################################################################################################

import sys
import os
import optparse
import importlib 
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

debug=0

#get bool information out of parser string
def stringtobool(variable):
    if isinstance(variable, bool):
       return variable
    if variable.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif variable.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# get plotting style information parser>config>default for bool type
def getParserConfigDefaultBool(parser,config,plotoptions,defaultbool):
    if not parser is None:
        print "%s using parser specification: %s" % (config,parser)
        return stringtobool(parser)
    elif config in plotoptions:
        print "%s using config specification: %s" % (config,plotoptions[config])
        return stringtobool(plotoptions[config])
    else:
        print "%s using default specification: %s" % (config,defaultbool)
        return stringtobool(defaultbool)
# get plotting style information parser>config>default
def getParserConfigDefaultValue(parser,config,plotoptions,defaultvalue):
    if not parser is None:
        print "%s using parser specification: %s" % (config,parser)
        return parser
    elif config in plotoptions:
        print "%s using config specification: %s" % (config,plotoptions[config])
        return plotoptions[config]
    else:
        print "%s using default specification: %s" % (config,defaultvalue)
        return defaultvalue
"""
Enabling parser options
"""
#usage="usage=%prog [options] \n"
usage = "-"*30+"\n"
usage+= "Requirered Specifications:\n"
usage+= "Plotscript.py --rootfile=ROOTFILE --workdir=WORKDIRPATH \n"
usage+= "If no Plotconfig is avaliable use: \n"
usage+= "Plotscript.py -e PATH \n"
usage+= "For further adjustments refer to the option descriptions.\n"
usage = "-"*30+"\n"

parser = optparse.OptionParser(usage=usage)


"""
Required input 
"""
filesAndDirectories = optparse.OptionGroup(parser, "File and Directory Options")

filesAndDirectories.add_option("-r", "--rootfile", dest="Rootfile", 
        help="REQUIRED: ROOTFILE including the entries to be plotted to create the plots", metavar="/path/to/rootfile")
filesAndDirectories.add_option("-w", "--workdir", dest="workdir",
         help="REQUIRED: OUTPUT PATH to workdir", metavar="/path/to/workdir")
filesAndDirectories.add_option("--directory", dest="directory", default=None,
         help="PATH to pyroot plotscript directory, takes directory of PlotScript.py file if none is given",
         metavar="/path/to/directory")
filesAndDirectories.add_option("-p", "--plotconfig", dest="plotconfig", default="plotconfig",
        help="FILE of plot config, if none is given uses the plotconfig.py in the workdir", metavar="/path/to/file.py")
filesAndDirectories.add_option("--pdftag", dest="pdftag", default=None,
        help="adds the NAMETAG to the saved plot .pdf", metavar="something_NAMETAG.pdf")
filesAndDirectories.add_option("--pdfname", dest="pdfname", default=None,
        help="NAME of the saved plot .pdf", metavar="NAME.pdf")
filesAndDirectories.add_option("--systematicfile", dest="systfile", default=None,
        help="PATH to a systematic.csv type file with a configuration of systematics for each process")
parser.add_option_group(filesAndDirectories)

"""
Key Options for the parser, used to extract the information
of the root file
"""
keyOptions       = optparse.OptionGroup(parser, "Key Options")

keyOptions.add_option("-k","--nominalkey", dest="nominalKey", default="$PROCESS_$CHANNEL",
        help="KEY of the systematics histograms", type = "str")
keyOptions.add_option("-s","--systematickey", dest="systematicKey", default="$PROCESS_$CHANNEL_$SYSTEMATIC",
        help="KEY of the nominal histograms", type = "str")
keyOptions.add_option("-d","--data", dest="data", default=None, type = "str",
        help="NAME of the data in the root file, used to replace the process identifier ($PROCESS) in the nominal key to get the data sample", metavar="datakeyreplace")
keyOptions.add_option("-c","--channelname", dest="channelName", type = "str",
        help="NAME of the channel in the root file, used to replace the channel identifier ($CHANNEL) in the nominal and systematic key")

parser.add_option_group(keyOptions)

"""
Plot Options to change the style of the plot,
activate ratio plot, normalize plot, make shape plots,
set logarithmic style or plot combine outputs
"""
plotOptions      = optparse.OptionGroup(parser, "Plot Options")

plotOptions.add_option("--normalize", dest="normalize",  default=None,
        help="normalizes plot")
plotOptions.add_option("--shape", dest="shape",  default=None,
        help="drawing shape plot, default normalize and no data")
plotOptions.add_option("--combineflag", dest="combineflag", default=None,
        help="NAME of the combine plot,  use for combine plots, use shapes_prefit for prefit and shapes_fit_s for post fit, ATTENTION only uses total signal and does not split signal processes,")
plotOptions.add_option("--drawFromHarvester", dest="drawFromHarvester", default = False,
        action = "store_true", help = "use output of 'PostFitShapesFromWorkspace' in CombineHarvester package as input")
plotOptions.add_option("--ratio", dest="ratio",  default=None,
        help="make ratio plot", metavar="ratio")
plotOptions.add_option("--logarithmic", dest="logarithmic", default=None,
        help="enable logarithmic plots")
plotOptions.add_option("--combineDatacard", dest = "datacard", default=None,
        help="PATH to datacard file rootfile path and channel name for correct binning of prefit/postfit plots")

plotOptions.add_option("--statErr", dest="addStatErrorband", default = None,
        help="add statistics errorband")
plotOptions.add_option("--skipErrorbands", dest = "skipErrorbands", default = False, action = "store_true", 
        help = "don't draw error bands (not recommended)")
plotOptions.add_option("--multisignal", dest = "multisignal", default = False, action = "store_true", 
        help = "plot multiple signals")
plotOptions.add_option("--divideByBinWidth", dest = "divideByBinWidth", default = False, action = "store_true", 
        help = "divide content by bin width")
plotOptions.add_option("--dontScaleSignal", dest = "dontScaleSignal", default = False, action = "store_true", 
        help = "dont Scale Signals")


plotOptions.add_option("--plot-blind", dest = "plot_blind", default = False, action = "store_true", 
        help = "do not draw the data points")
plotOptions.add_option("--hide-signal", dest = "hide_signal", default = False, action = "store_true", 
        help = "do not draw the total signal template")

plotOptions.add_option("--stackPrefitSignal", dest="stack_prefit_signal", default = False, action = "store_true",
        help = "include prefit signal to the stack")

parser.add_option_group(plotOptions)

"""
Aesthetic options
"""

styleOptions     = optparse.OptionGroup(parser, "Aesthetic Style Options")

styleOptions.add_option("--selectionlabel", dest="selectionlabel", default=None,
        help='label of the selection (e.g. "6 jets, \geq 3 b-tags"), printed in the upper left part of the plot')
styleOptions.add_option("--datalabel", dest="datalabel", default=None,
        help="label of the data in the legend")
styleOptions.add_option("--signallabel", dest="signallabel", default=None,
        help="Option only for COMBINE Plots: label of the signal in the legend")
styleOptions.add_option("--signalcolor", dest="signalcolor", default=None,
        help="Option only for COMBINE Plots: Color of the total signal contribution. Default: {}".format(ROOT.kBlue))
styleOptions.add_option("--signalscaling", dest="signalscaling", default=None,
        help="scale factor of the signal processes, -1 to scale with background integral")
styleOptions.add_option("--lumilabel", dest="lumilabel", default=None,
        help="print luminosity label on canvas")
styleOptions.add_option("--yLabel", dest="yLabel", default=None,
        help="axis label of y-axis")
styleOptions.add_option("--xLabel", dest="xLabel", default=None,
        help="axis label of x-axis (inferred from histogram if None)")
styleOptions.add_option("--manualBinLabels", dest="manualBinLabels", default=None,
        help="List of labels to use for bin edges, e.g. 'bin1,bin2,bin3,bin4,bin5' for 4 bins. Error is raised if number of bins does not match number of labels.")
styleOptions.add_option("--unit", dest="unit", default=None,
        help="Unit to display on the x-axis. If 'divideByBinWidth' is used, add [1/UNIT] to y-axis.")#
plotOptions.add_option("--yDenominatorLabel", dest = "yDenominatorLabel", default = "bin width", type=str, 
        help = "If divideByBinWidth is used, this is the label of the denominator in the ratio plot. Default: bin width")
styleOptions.add_option("--cmslabel", dest="cmslabel", default=None,
        help="print CMS label on canvas")
styleOptions.add_option("--splitlegend", dest="splitlegend",  default=None,
        help="splits the legend in two")
styleOptions.add_option("--sortedprocesses", dest="sortedprocesses", default=None,
        help="List for the order of Processes to be stacked, starts with first, if processes are not specified in this list but included in the background, they get added at the end by their event yield. (For shapes only important for legend order)")
styleOptions.add_option("--ratio-lower-bound", dest="ratio_lower_bound", default = 0.5, type = "float",
        help= "set lower bound for the ratio plot range. Defaults to 0.5")
styleOptions.add_option("--ratio-upper-bound", dest="ratio_upper_bound", default = 1.5, type = "float",
        help= "set upper bound for the ratio plot range. Defaults to 1.5")
styleOptions.add_option("--onlyMainDivisionsXaxis", dest="onlyMainDivisionsXaxis", default=False,
        help= "draw only main divisions on x-axis, e.g. for NJets plots. Default False.")
styleOptions.add_option("--yMin",dest="yMinUser", default=None, type = "float",
        help="force range of y axis to start here. If None, default values are used.")
styleOptions.add_option("--yMax",dest="yMaxUser", default=None, type = "float",
        help="force range of y axis to end here. If None, default values are used.")

parser.add_option_group(styleOptions)

"""
Creates an exemplary Plot Config to be edited,
exits the PlotScript afterwards
"""
createPlotconfig    = optparse.OptionGroup(parser, "Creates an exemplary Plotconfig to edit")

createPlotconfig.add_option("-e", "--examplePlotconfig", dest="examplePlotconfig", 
        default=False, action="store_true", help="creates exemplary Plotconfig")
createPlotconfig.add_option("-o", "--ouputPlotconfig", dest="outputPlotconfig", default=False,
        help="OUTPUTPATH where exemplary Plotconfig is created (else using current directory)")

parser.add_option_group(createPlotconfig)

"""
get all options
"""
(options, args) = parser.parse_args()
"""
check if requirered options are there (except when creating an empty Plotconfing)
"""
if not options.examplePlotconfig:
    if not options.Rootfile:
        parser.error("Rootfile not given")
    if not options.workdir:
        parser.error("Workdir not given!")

if options.manualBinLabels:
    options.manualBinLabels = options.manualBinLabels.split(",")

# Define directories used to import stuff
tooldir   = options.directory
if not tooldir:
    tooldir = os.path.dirname(os.path.abspath(__file__))

plotconfig  = options.plotconfig
workdir     = options.workdir

divideByBinWidth = options.divideByBinWidth
"""
import plot class
"""
sys.path.append(tooldir)
Plots       = importlib.import_module("Plots")

"""
import systematics class if needed
"""
systClass = None
if not options.systfile is None:
    if not os.path.exists(options.systfile):
        sys.exit("path to systematic.csv {} does not exist".format(options.systfile))
    Systematics = importlib.import_module("Systematics")
    systClass = Systematics.Systematics(options.systfile)
    print("loading systematic.csv for systematic setup")

"""
creates emtpy Plotconfig
"""
if options.examplePlotconfig:
    if options.outputPlotconfig:
        outputpath = options.outputPlotconfig
    else:
        outputpath = os.getcwd()
    Plots.createExamplePlotconfig(outputpath=outputpath)
    sys.exit("Created exemplary Plotconfig!")

# checks if paths given exist
if not os.path.exists(options.Rootfile):
    sys.exit("ERROR: rootfile does not exist!")
elif not os.path.exists(plotconfig):
    sys.exit("ERROR: plotconfig does not exist!")

"""
start loading plotconfig
"""

print '''
# ========================================================
# loading config
# ========================================================
    '''
if os.path.abspath(plotconfig):
    plotconfigpath,plotconfigfile   = os.path.split(plotconfig)
    plotconfigfile                  = plotconfigfile.replace('.py','')
    sys.path.append(plotconfigpath)
    pltcfg                          = importlib.import_module(plotconfigfile)
else:
    sys.path.append(workdir)
    plotconfigfile                  = plotconfig
    pltcfg                          = importlib.import_module(plotconfigfile)
print "using plotconfig: %s" % (plotconfigfile)

samples         = pltcfg.samples
try:
    plottingsamples = pltcfg.plottingsamples
except ImportError as e:
    print("WARNING: could not load 'plottingsamples'")
    print(e)
    plottingsamples = {}

systematics     = pltcfg.systematics
plotoptions     = pltcfg.plotoptions

"""
start loading  histograms
"""

print '''
# ========================================================
# loading histograms and creating Errorbands
# ========================================================
    '''
"""
manage keys for root file
"""
# Define placeholders for the keys of the histograms
procIden    = "$PROCESS"
chIden      = "$CHANNEL"
sysIden     = "$SYSTEMATIC"
combineIden = "$FLAG"


combineflag             = getParserConfigDefaultValue(parser=options.combineflag,config="combineflag",
                                            plotoptions=plotoptions,defaultvalue=None)
options.nominalKey      = getParserConfigDefaultValue(parser = options.nominalKey, config = "nominalKey",
                                            plotoptions=plotoptions,defaultvalue="$PROCESS_$CHANNEL")
options.systematicKey   = getParserConfigDefaultValue(parser = options.systematicKey, config = "systematicKey",
                                            plotoptions=plotoptions,defaultvalue="$PROCESS_$CHANNEL_$SYSTEMATIC")

binEdges                = None
outputName              = None
xLabel                  = ""
if combineflag:
    options.nominalKey  = "$FLAG/$CHANNEL/$PROCESS"
    #options.data        = getParserConfigDefaultValue(parser=options.data,config="data",
    #                                        plotoptions=plotoptions,defaultvalue=False)
    options.data        = "data"
    if options.drawFromHarvester:
        flag = "prefit" if combineflag == "shapes_prefit" else "postfit"
        options.nominalKey = "$CHANNEL_{FLAG}/$PROCESS".format(FLAG = flag)

        options.data = "data_obs"
    options.nominalKey  = options.nominalKey.replace(combineIden, combineflag)
    print("datacard: '{}'".format(options.datacard))
    print("type: '{}'".format(type(options.datacard)))
    if not any(options.datacard == x for x in ["None", "", None]):
        if not os.path.exists(options.datacard):
            print("ERROR: could not load datacard from '{}'".format(options.datacard))
        datacard_dir = os.path.dirname(os.path.abspath(options.datacard))
        with open(options.datacard, "r") as card:
            lines = card.readlines()
        lines = [l for l in lines if l.startswith("shapes")]
        channelLine = False
        for l in lines:
            line = l.split(" ")
            if options.channelName in line:
                channelLine = line
                break
        if channelLine is None: sys.exit("no channel {} found in datacard".format(options.channelName))
        channelLine = [elem for elem in channelLine if not elem == ""]
        binFileName = channelLine[3]
        binFileName = binFileName if os.path.isabs(binFileName) else os.path.join(datacard_dir, binFileName)
        binKey = channelLine[4].replace("$PROCESS","data_obs")
        binKey = binKey.replace("$CHANNEL", options.channelName)
        outputName = binKey.replace("data_obs_","")
        
        binFile = ROOT.TFile(binFileName)
        print("loading " + binKey)
        binHist = binFile.Get(binKey)
        xLabel = binHist.GetTitle()
        binEdges = []
        for i in range(binHist.GetNbinsX()+1):
            binEdges.append( binHist.GetBinLowEdge(i+1) )

# Hard coded bin edges can be put here. To do: add an option from command line.
#binEdges = [4.5,5.5,6.5,7.5,8.5,9.5]
# build keys
if chIden in options.nominalKey:
    print("inserting channel name '{}' into nominal template".format(options.channelName))
    nominalKey      = options.nominalKey.replace(chIden, options.channelName)
else:
    nominalKey      = options.nominalKey

if chIden in options.nominalKey:
    systematicKey   = options.systematicKey.replace(chIden, options.channelName)
else:
    systematicKey   = options.systematicKey


PlotList    = {}
# load ROOT File
rootfilename    = options.Rootfile
rootFile        = ROOT.TFile(rootfilename, "readonly") 


addStatErrorband = getParserConfigDefaultValue(
                    parser = options.addStatErrorband, config = "statErrorband",
                    plotoptions = plotoptions, defaultvalue = False)

# load samples
print "start loading  samples" 
multisignal = options.multisignal

for sample in samples:
    print(sample)
    color   = samples[sample]["info"]['color']
    typ     = samples[sample]["info"]['typ']
    label   = samples[sample]["info"]['label']
    entry   = None
    if samples[sample]['plot'] == False:
        continue
    if combineflag:
        if typ=="signal" and not multisignal:
            continue
        elif typ == "signal":
            if combineflag=="shapes_fit_s":
                if options.hide_signal: continue

                entry = Plots.getHistogramAndErrorband(rootFile=rootFile,sample=sample,
                                                color=color,typ="bkg",label=label,
                                                nominalKey=nominalKey,procIden=procIden,
                                                binEdges=binEdges,newTitle=xLabel)
            else:
                entry = Plots.getHistogramAndErrorband(rootFile=rootFile,sample=sample,
                                                color=color,typ=typ,label=label,
                                                nominalKey=nominalKey,procIden=procIden,
                                                binEdges=binEdges,newTitle=xLabel)                
        else:
            entry = Plots.getHistogramAndErrorband(rootFile=rootFile,sample=sample,
                                                        color=color,typ=typ,label=label,
                                                        nominalKey=nominalKey,procIden=procIden,
                                                        binEdges=binEdges,newTitle=xLabel)
    else:
        entry = Plots.buildHistogramAndErrorBand(rootFile=rootFile,sample=sample,
                                                        color=color,typ=typ,label=label,
                                                        systematics=systematics,
                                                        nominalKey=nominalKey,procIden=procIden,
                                                        systematicKey=systematicKey,sysIden=sysIden,
                                                        systClass=systClass,
                                                        addStatErrorband=addStatErrorband)

    PlotList[sample] = entry

"""
Combine Histograms and errorbands for combined plot channels
"""
# rootFile.ReOpen("UPDATE")
for sample in plottingsamples:
    color       = plottingsamples[sample]['color']
    typ         = plottingsamples[sample]['typ']
    if combineflag:
        if typ=="signal" and not multisignal:
            continue
        elif typ == "signal":
            if combineflag=="shapes_fit_s":
                if options.hide_signal: continue

                label       = plottingsamples[sample]['label']
                addsamples  = plottingsamples[sample].get('addSamples', [])
                print(PlotList)
                PlotList = Plots.addSamples(sample=sample,color=color,typ="bkg",label=label,
                                                addsamples=addsamples,PlotList=PlotList,combineflag=combineflag)
            else:
                label       = plottingsamples[sample]['label']
                addsamples  = plottingsamples[sample].get('addSamples', [])
                print(PlotList)
                PlotList = Plots.addSamples(sample=sample,color=color,typ="signal",label=label,
                                        addsamples=addsamples,PlotList=PlotList,combineflag=combineflag)
        elif typ == "bkg":
            label       = plottingsamples[sample]['label']
            addsamples  = plottingsamples[sample].get('addSamples', [])
            print(PlotList)
            PlotList = Plots.addSamples(sample=sample,color=color,typ="bkg",label=label,   
                                        addsamples=addsamples,PlotList=PlotList,combineflag=combineflag)

        entry = PlotList.get(sample, "ERROR")
    if not entry == "ERROR":
        addedHist = PlotList[sample].hist
        if isinstance(addedHist, ROOT.TH1F):
            addedHist.Print()
            addedHist.SetName(label+"_"+addedHist.GetName()) 
            addedHist.Print()
        else:
            PlotList[sample] = "ERROR"
    else:
        PlotList[sample] = "ERROR"
    # rootFile.Write(addedHist.GetName())
# rootFile.ReOpen("readonly")
"""
Get errorband and signalhist in case of combine output file,
else no signal
"""
stack_prefit_signal = options.stack_prefit_signal
background = None
manualBinLabels = getParserConfigDefaultValue(parser=options.manualBinLabels,config="manualBinLabels",
                                            plotoptions=plotoptions, defaultvalue=None)
if combineflag:
    str_total = "total" if not options.drawFromHarvester else "TotalProcs"
    str_total_bkg = "total_background" if not options.drawFromHarvester\
                     else "TotalBkg"
    str_total_sig = "total_signal" if not options.drawFromHarvester\
                     else "TotalSig"
    totalsignalkey  = nominalKey.replace(procIden, str_total_sig)
    totalsignal     = rootFile.Get(totalsignalkey)
    signal_for_shape= rootFile.Get(totalsignalkey).Clone() # duplicate for line signal in pre-fit plot
    if not binEdges is None:
        totalsignal = Plots.updateBinEdges(totalsignal, binEdges)
        signal_for_shape = Plots.updateBinEdges(signal_for_shape, binEdges)

    signallabel   = getParserConfigDefaultValue(parser=options.signallabel,config="signallabel",
                                            plotoptions=plotoptions,defaultvalue="signal")
    signalcolor   = getParserConfigDefaultValue(parser=options.signalcolor,config="signalcolor",
                                            plotoptions=plotoptions,defaultvalue=ROOT.kBlue)
    """
    add signal to stack plot if already fitted (post fit),
    else check the option stack_prefit_signal. If false, prefit signal is not added to the stack, otherwise it is.
    In any case, the signal is shown as a line in prefit plots.
    """
    if combineflag=="shapes_fit_s":
        bkgKey = nominalKey.replace(procIden, str_total)
        if not multisignal:
            PlotList["total_signal"] = Plots.Plot(totalsignal,"total_signal",label=signallabel,
                                        typ="bkg", OverUnderFlowInc=True, color = signalcolor)
        options.ratio = "#frac{data}{total MC}"
    else:
        if not stack_prefit_signal:
            bkgKey = nominalKey.replace(procIden, str_total_bkg)
            if not multisignal:
                PlotList["signal"] = Plots.Plot(signal_for_shape,"signal",label=signallabel,
                                                typ="signal", OverUnderFlowInc=True, color = signalcolor)
        else:
            #add prefit signal to stack, and show as line too
            bkgKey = nominalKey.replace(procIden, str_total)
            if not multisignal:
                PlotList["total_signal"] = Plots.Plot(totalsignal,"total_signal",label=signallabel,
                                           typ="bkg", OverUnderFlowInc=True, color = signalcolor)
                PlotList["signal"] = Plots.Plot(signal_for_shape,"signal",label=signallabel,
                                           typ="signal", OverUnderFlowInc=True, color = signalcolor)
            options.ratio = "#frac{data}{total MC}"

    # from total background or total background+signal prediction histogram in mlfit file, get the error band
    if not xLabel == "" and not multisignal:
        PlotList["total_signal"].hist.SetTitle(xLabel)
    background = rootFile.Get(bkgKey)

    if not binEdges is None:
        background = Plots.updateBinEdges(background, binEdges)

    if divideByBinWidth:
        background.Scale(1., "width")
    if options.skipErrorbands:
        errorband = None
    else:
        errorband = Plots.GetErrorGraph(background)

else:
    errorband = None

# update labels for x axis if they are provided
if manualBinLabels:
    for p in PlotList.values():
        if isinstance(p, str):
            continue
        p.hist = Plots.updateBinLabels(p.hist, manualBinLabels)

"""
load data if avaliable and move under and overflow bin
"""

data        = getParserConfigDefaultValue(parser=options.data,config="data",
                                            plotoptions=plotoptions,defaultvalue=False)
datalabel   = getParserConfigDefaultValue(parser=options.datalabel,config="datalabel",
                                            plotoptions=plotoptions,defaultvalue="data")
if data:
    print("loading data")
    dataKey     = nominalKey.replace(procIden, data)
    dataHist    = rootFile.Get(dataKey)
    print("    type of data hist is: "+str(type(dataHist)) )
    if isinstance(dataHist, ROOT.TH1):
        dataHist.SetStats(False)
        if not binEdges is None:
            dataHist = Plots.updateBinEdges(dataHist, binEdges)
        
        Plots.moveOverUnderFlow(dataHist)
        print "using data: %s" % (dataKey)
    # data in combine in TGraphAsymmErrors, get TH1 out of it
    elif isinstance(dataHist, ROOT.TGraphAsymmErrors):
        n_bins   = Plots.FindNewBinNumber(background)
        dataHist = Plots.GetHistoFromTGraphAE(dataHist, data, n_bins, binEdges)
        #Plots.moveOverUnderFlow(dataHist)
        dataHist.SetStats(False)
        # if divideByBinWidth:
        #     dataHist.Scale(1., "width")
    else:
        print "ATTENTION: Not using data!"
        dataHist=None
else:
        print "ATTENTION: Not using data!"
        dataHist=None

if manualBinLabels and dataHist:
    dataHist = Plots.updateBinLabels(dataHist, manualBinLabels)
print '''
# ========================================================
# plotting histograms and Errorbands
# ========================================================
    '''

#get plotting style information, prioritized by parser>config>default
signalscaling   = getParserConfigDefaultValue(parser=options.signalscaling,config="signalscaling",
                                            plotoptions=plotoptions,defaultvalue=-1)
ratio           = getParserConfigDefaultValue(parser=options.ratio,config="ratio",
                                            plotoptions=plotoptions,defaultvalue="#frac{data}{MC Background}")
lumilabel       = getParserConfigDefaultValue(parser=options.lumilabel,config="lumiLabel",
                                            plotoptions=plotoptions,defaultvalue=False)
cmslabel        = getParserConfigDefaultValue(parser=options.cmslabel,config="cmslabel",
                                            plotoptions=plotoptions,defaultvalue=False)
yLabel          = getParserConfigDefaultValue(parser=options.yLabel,config="yLabel",
                                            plotoptions=plotoptions,defaultvalue="Events expected")
xLabel          = getParserConfigDefaultValue(parser=options.xLabel,config="xLabel",
                                            plotoptions=plotoptions,defaultvalue=None)
unit          = getParserConfigDefaultValue(parser=options.unit,config="unit",
                                            plotoptions=plotoptions,defaultvalue=None)
logarithmic     = getParserConfigDefaultBool(parser=options.logarithmic,config="logarithmic",
                                            plotoptions=plotoptions,defaultbool=False)
splitlegend     = getParserConfigDefaultBool(parser=options.splitlegend,config="splitLegend",
                                            plotoptions=plotoptions,defaultbool=False)
normalize       = getParserConfigDefaultBool(parser=options.normalize,config="normalize",
                                            plotoptions=plotoptions,defaultbool=False)
shape           = getParserConfigDefaultBool(parser=options.shape,config="shape",
                                            plotoptions=plotoptions,defaultbool=False)
yDenominatorLabel = getParserConfigDefaultValue(parser=options.yDenominatorLabel,config="yDenominatorLabel",
                                            plotoptions=plotoptions, defaultvalue="bin width")


if shape:
    dataHist        = None
    ratio           = False
    normalize       = True
if options.plot_blind:
    dataHist = None
if options.hide_signal:
    print("Will hide the total signal contribution")
    PlotList["total_signal"] = "ERROR"
if options.sortedprocesses:     
    sortedProcesses = [x.strip() for x in options.sortedprocesses.split(",")]
else:
    sortedProcesses = pltcfg.sortedprocesses

"""

"""
if divideByBinWidth:
    yLabel = yLabel+" /({})".format(yDenominatorLabel)
    for p in PlotList:
        if isinstance(PlotList[p], str):
            continue
        if isinstance(PlotList[p].hist, ROOT.TH1F):
            PlotList[p].hist.Scale(1.,"width")
    if dataHist:
        dataHist.Scale(1., "width")

if unit:
    xLabel = xLabel+" ({})".format(unit)
    if divideByBinWidth:
        yLabel = yLabel+" (1/{})".format(unit)
print("="*130)
print("ratio: {}".format(ratio))
print("="*130)
DrawHistogramObject = Plots.DrawHistograms(PlotList,options.channelName,
                                data=dataHist, datalabel = datalabel,
                                ratio=ratio, 
                                signalscaling=int(signalscaling),
                                errorband=errorband, background=background,
                                logoption=logarithmic,
                                normalize=normalize,splitlegend=splitlegend,
                                combineflag=combineflag,shape=shape,
                                sortedProcesses=sortedProcesses,
                                yLabel=yLabel, xLabel = xLabel, dontScaleSignal=options.dontScaleSignal,
                                divideByBinWidth = divideByBinWidth, onlyMainDivisionsXaxis=options.onlyMainDivisionsXaxis,
                                yMinUser=options.yMinUser, yMaxUser=options.yMaxUser,
                            )
                                


DrawHistogramObject.ratio_lower_bound = options.ratio_lower_bound
DrawHistogramObject.ratio_upper_bound = options.ratio_upper_bound

DrawHistogramObject.drawHistsOnCanvas()

DrawHistogramObject.builtLegend()
# add lumi or private work label to plot
if cmslabel:
    DrawHistogramObject.printCMSLabel(cmslabel=cmslabel)
if lumilabel:
    DrawHistogramObject.printLumi(lumi = lumilabel)

#add selection label to plot
if options.selectionlabel:
    DrawHistogramObject.printChannelLabel(channelLabel = options.selectionlabel)
plotpath = workdir+"/outputPlots/"
if not os.path.exists(plotpath):
        os.makedirs(plotpath)

"""
safe options
"""
pdftag           = getParserConfigDefaultValue(parser=options.pdftag,config="pdftag",
                                            plotoptions=plotoptions,defaultvalue=False)
if combineflag:
    pdftag = "_".join([pdftag, combineflag]) if pdftag else combineflag
if options.pdfname:
    path = os.path.join(plotpath, options.pdfname)
elif not outputName is None:
    path = os.path.join(plotpath, outputName)
else:
    path = os.path.join(plotpath, options.channelName)


if pdftag:
    path += "_"+str(pdftag)

if shape:
    path += "_shape"

if logarithmic:
    path +="_log.pdf"
else:
    path += ".pdf"
print(normalize)
DrawHistogramObject.saveCanvas(path=path)

