# samples named in the rootfile
plottingsamples = {
    "ttH_hbb" : {
        "info" : {
            "label" : "t#bar{t}H, H to b#bar{b}",   # text that will be displayed in the plot legend for this process 
            "color": ROOT.kCyan,    # color of the process in the plot. You can use both kCOLOR or the number attributed to the enum keyword
            "typ": "signal"     # defines type of process. Signal are not part of the stack and are drawn as lines
            },
        "plot" : True   # decides is process is drawn in the first place or not
    },
    "ttH_hgg" : {
        "info" : {
            "label" : "t#bar{t}H, H to #gamma#gamma",   # text that will be displayed in the plot legend for this process 
            "color": ROOT.kCyan,    # color of the process in the plot. You can use both kCOLOR or the number attributed to the enum keyword
            "typ": "signal"     # defines type of process. Signal are not part of the stack and are drawn as lines
            },
        "plot" : True   # decides is process is drawn in the first place or not
    },
    "ttbb" : {
        "info" : {
            "label" : "t#bar{t}+b#bar{b}",
            "color": ROOT.kRed+3,
            "typ": "bkg"
            },
        "plot" : True
    },
    "ttbarZ" : {
        "info" : {
            "label" : 't#bar{t}+Z',
            "color": 432,
            "typ": "bkg"
            },
        "plot" : False
    }
}

# combined samples. This allows to merge process for a plot
plottingsamples = {
    "ttH" : {
        "color": ROOT.kCyan, 
        "addSamples": ["ttH_hbb", "ttH_hgg"], 
        "typ": "signal", 
        "label": "t#bar{t}H"
    }
}

# systematics to be plotted. Uncertainties will be used for the uncertainty band in the plot, i.e. merged
systematics = [
    "CMS_ttHbb_PU",
    "CMS_eff_e_2018",
    "CMS_scale_j_2018"
]

# order of the stack processes, descending from top to bottom
sortedprocesses=["ttH","ttbb"]

# options for the plotting style
plotinfo = {
    "signalScaling"     : -1,   # factor with which the signal processes will be scaled. Choose -1 to normalize signal processes to background stack
    "datalabel"         : "data", # name of data displayed in legend
    "data"              : "data_obs", # name of data in the input root file
    "lumiLabel"         : "41.5",     # string in upper right corner next to '(13 TeV)'
    
    "cmslabel"          : "private Work",   # text in cursive in upper left corner next to 'CMS'
    "normalize"         : False,    # normalize all processes to unity
    "ratio"             : '#frac{data}{MC Background}', # label for y axis of ratio plot
    "logarithmic"       : False,    # draw y axis logarithmic
    "splitLegend"       : True,     # split the legend into two columns
    "shape"             : False,    # normalize to first histogram
    
    "statErrorband"     : True,     # draw statistical uncertainty band in a separate error band (additional to systematics)
    "nominalKey"        : "$PROCESS__$CHANNEL", # name template for histograms in .root file. Keywords will be replaced
    "systematicKey"     : "$PROCESS__$CHANNEL__$SYSTEMATIC",  # name template for systematic variations in .root file. Keywords will be replaced

    # use for combine plots, use 'shapes_prefit' for prefit OR 'shapes_fit_s' for post fit
    # only uses total signal and does not split signal processes
    # 
    # "combineflag"     : "shapes_prefit"/"shapes_fit_s",
    # "signallabel"     : "Signal"  # label in legend for signal
}
    