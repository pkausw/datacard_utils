import math
import numpy as np
import ROOT


class Process:
    def __init__(self, name, type, templates=[]):
        self.name = name
        self.templates = templates if len(templates)>0 else [name]
        
        self.is_data             = False
        self.is_signal           = False
        self.is_background       = False
        self.is_total_background = False
        self.is_total_processes  = False
        if type == "data":
            self.is_data = True
        elif type == "signal":
            self.is_signal = True
        elif type == "background":
            self.is_background = True
        elif type == "total background":
            self.is_total_background = True
        elif type == "total processes":
            self.is_total_processes = True
        else:
            raise RuntimeError(f"Unknown Process type {type}")

    def str(self):
        return f"{self.name} ({str(self.templates)})"


class Category:
    def __init__(self, channel, jettag, node):
        self.channel = channel
        self.jettag  = jettag
        self.node    = node
        self.bins    = []

    def str(self):
        return f"({self.channel} {self.jettag} {self.node})"


class Translator:
    """Category --> histogram name"""

    def __init__(self, analysis_cfg):
        self.year = analysis_cfg["year"]
        self.fit = analysis_cfg["fit"]
        self.is_stxs = analysis_cfg["stxs"]

    def jettag_str(self, channel, jettag):
        jettags = {
            "FH" : {
                "9j4t" : "j9_t4",
                "8j4t" : "j8_t4",
                "7j4t" : "j7_t4",
            },
            "SL" : {
                "6j4t" : "ge6j_ge4t",
                "5j4t" : "5j_ge4t",
            },
            "DL" : {
                "4j3t" : "4j3b",
                "3j3t" : "3j3b"
            }
        }
        if channel in jettags:
            if jettag in jettags[channel]:
                return jettags[channel][jettag]
        raise RuntimeError(f"Unknown jet-tag category {jettag} in channel {channel}")

    def node_str(self, channel, node):
        nodes = {
            "FH" : {
                ""        : "", # no further splitting of FH jet-tag categories
                "STXS1"   : "STXS_0_",
                "STXS2"   : "STXS_1_",
                "STXS3"   : "STXS_2_",
                "STXS4"   : "STXS_3_",
                "STXS5"   : "STXS_4_",
            },
            "SL" : {
                "ttH+ttb(b)" : "ttH_ttmb_ratioObservable",
                "STXS1"   : "classification_ttH_ttmb_vs_slike_times_ttHbb_STXS_0",
                "STXS2"   : "classification_ttH_ttmb_vs_slike_times_ttHbb_STXS_1",
                "STXS3"   : "classification_ttH_ttmb_vs_slike_times_ttHbb_STXS_2",
                "STXS4"   : "classification_ttH_ttmb_vs_slike_times_ttHbb_STXS_3",
                "STXS5"   : "classification_ttH_ttmb_vs_slike_times_ttHbb_STXS_4",
                "tt2b"    : "tt2b_node",
                "ttC"     : "ttcc_node",
                "ttLF"    : "ttlf_node",
                "tHq"     : "tHq_node",
                "tHW"     : "tHW_node",
            },
            "DL" : {
                "ttH+ttB" : "DNN_ttHbb_ratioObservable",
                "STXS1"   : "DNN_ttHbb_STXSbin1",
                "STXS2"   : "DNN_ttHbb_STXSbin2",
                "STXS3"   : "DNN_ttHbb_STXSbin3",
                "STXS4"   : "DNN_ttHbb_STXSbin4",
                "STXS5"   : "DNN_ttHbb_STXSbin5",
                "ttC"     : "DNN_ttcc",
                "ttLF"    : "DNN_ttlf",
                ""        : "ttHbb" # no further splitting of DL3j3t category
            }
        }
        if channel in nodes:
            if node in nodes[channel]:
                return nodes[channel][node]
        raise RuntimeError(f"Unknown node {node} in channel {channel}")
            
    def category_str(self, category):
        channel = category.channel
        jettag  = category.jettag
        node    = category.node
        if channel == "FH":
            return "fh_{node}{jettag}_DNN_Node0".format(
                        jettag=self.jettag_str(channel,jettag),
                        node=self.node_str(channel,node)
                    )
        if channel == "SL":
            return "ljets_{jettag}_{node}".format(
                        jettag=self.jettag_str(channel,jettag),
                        node=self.node_str(channel,node)
                    )
        if channel == "DL":
            return "{dl}_{jettag}_{node}".format(
                        dl=("dl" if self.is_stxs else "ttH_hbb_13TeV_dl"),
                        jettag=self.jettag_str(channel,jettag),
                        node=self.node_str(channel,node)
                    )
        raise RuntimeError(f"Unknown category: channel {channel} / jet-tag {jettag} / node {node}")

    def dir_name(self, category):
        return "ttH_{year}_{cat}_{fit}".format(
            year = self.year,
            cat = self.category_str(category),
            fit = self.fit
        )


class Style:
    """Encapsulate colors, line styles, text labels, etc."""

    def __init__(self):
        self.node_tex_names = {
            "ttLF"    : "ttLF",
            "ttC"     : "ttC",
            "tt2b"    : "tt+2b",
            "tHq"     : "tHq",
            "tHW"     : "tHW",
            "ttH+ttb(b)" : "ttH / tt+b(b)",
            "ttH+ttB" : "ttH / ttB",
            "STXS1"   : "1",
            "STXS2"   : "2",
            "STXS3"   : "3",
            "STXS4"   : "4",
            "STXS5"   : "5",
        }

        self.processes = { # label, color, line style, line width
            "data" : [ "Data",             1, 1, 1 ],
            "ttH"  : [ "t#bar{t}H",      601, 1, 1 ],
            "ttH1" : [ "t#bar{t}H 1",    604, 1, 1 ],
            "ttH2" : [ "t#bar{t}H 2",    604, 3, 1 ],
            "ttH3" : [ "t#bar{t}H 3",      2, 1, 1 ],
            "ttH4" : [ "t#bar{t}H 4",      2, 3, 1 ],
            "ttH5" : [ "t#bar{t}H 5",    418, 1, 1 ],
            "tHq"  : [ "tHq",            606, 1, 1 ],
            "tHW"  : [ "tHW",            603, 1, 1 ],
            "QCD"  : [ "QCD",            418, 1, 1 ],
            "ttB"  : [ "t#bar{t}B",      635, 1, 1 ],
            "ttC"  : [ "t#bar{t}C",      633, 1, 1 ],
            "ttLF" : [ "t#bar{t}LF",     625, 1, 1 ],
            "st"   : [ "t",              616, 1, 1 ],
            "Vjet" : [ "V+jets",          18, 1, 1 ],
            "VV"   : [ "VV",             862, 1, 1 ],
            "ttV"  : [ "t#bar{t}V",      ROOT.kCyan-7, 1, 1 ],
            "ttG"  : [ "t#bar{t}#gamma", ROOT.kGreen+1, 1, 1 ],
            "VHbb" : [ "VH(bb)",         ROOT.kViolet+7, 1, 1 ],
            # for auxiliary histograms
            "B"    : [ "", 1, 1, 1 ],
            "S+B"  : [ "", 1, 1, 1 ],
        }

    
    def process_color(self, process):
        name = process.name if isinstance(process, Process) else process
        if name in self.processes:
            return self.processes[name][1]
        raise RuntimeError(f"Style: no color defined for process {name}")

    def process_linestyle(self, process):
        name = process.name if isinstance(process, Process) else process
        if name in self.processes:
            return self.processes[name][2]
        raise RuntimeError(f"Style: no line style defined for process {name}")

    def process_linewidth(self, process):
        name = process.name if isinstance(process, Process) else process
        if name in self.processes:
            return self.processes[name][3]
        raise RuntimeError(f"Style: no line width defined for process {name}")
    
    def process_tex_name(self, process):
        name = process.name if isinstance(process, Process) else process
        if name in self.processes:
            return self.processes[name][0]
        raise RuntimeError(f"Style: no TeX name defined for process {name}")

    
    def node_tex_name(self, node):
        if node in self.node_tex_names:
            return self.node_tex_names[node]
        raise RuntimeError(f"Style: no TeX name defined for node {node}")

    
    def jettag_tex_name(self, jettag):
        # Parse number of jets
        jet = jettag.split("j")[0]
        if jet in ["4", "6", "9"]:
            jet = f"#geq{jet}"
        elif jet in ["3", "5", "7", "8"]:
            jet = f"{jet}"
        else:
            raise RuntimeError(f"Style: no jet category {jettag}:jet defined")

        return f"{jet} jets"

    
    def marker_style(self):
        return 20

    
    def marker_size(self):
        return 0.7



def read_histogram(file_name, hist_name):
    """Read histogram from file"""
    # https://codereview.stackexchange.com/questions/158004/reading-and-processing-histograms-stored-in-root-files
    tf = ROOT.TFile.Open(file_name)
    if not tf:
        raise RuntimeError(f"File {file_name} does not exist")
    hist = tf.Get(hist_name)
    if not hist:
        raise RuntimeError(f"Histogram {hist_name} does not exist")
    hist.SetDirectory(0)
    tf.Close()

    return hist


def get_binning(analysis_cfg):
    """
    Extract the total number of bins and bin ranges per category

    The number of bins and ranges are extracted from data_obs.
    Function sets the bin ranges in the categories (overwrites
    bin range in categories!) and returns the total number of bins

    Return
    ------
    int
        Total number of bins in histogram (concatenated over all
        categories)
    """

    t = Translator(analysis_cfg)
    nbins_total = 0
    for category in analysis_cfg["categories"]:
        h_name = t.dir_name(category)+"/data_obs"
        h = read_histogram(analysis_cfg["file_name"], h_name)
        nbins = h.GetNbinsX()
        category.bins = [ nbins_total+1+b for b in range(nbins) ]
        nbins_total += nbins

    return nbins_total


def get_histogram(process, nbins, analysis_cfg):
    """
    Create new histogram for one process

    The histogram concatenates the original histograms per category.
    Function returns the new histogram

    Return
    ------
    TH1D
        Histogram for this process (concatenated original templates over
        all categories)
    """
    
    # Create new histogram with nbins
    # Will be the concatenation of all original histograms
    name = analysis_cfg["year"]+"_"+process.name+"_"+str(np.random.rand())
    hout = ROOT.TH1F(name, "", nbins, 0, nbins)

    # Loop over all templates that contribute to this process
    # Can be more than one if processes are grouped together, e.g.
    # ttV = ttW+ttZ
    t = Translator(analysis_cfg)
    for template in process.templates:
        template_exists = False

        # Loop over all categories and concatenate original histograms
        for category in analysis_cfg["categories"]:
            try:
                # Get original template from file
                hin_name = t.dir_name(category)+"/"+template
                hin = read_histogram(analysis_cfg["file_name"], hin_name)
                template_exists = True
                
                # Add bin contents+errors to hout at the correct position
                # Loop over bins of original template
                for i in range(hin.GetNbinsX()):
                    
                    # Get content and error of bin in original template
                    bin_hin   = 1+i
                    value_hin = hin.GetBinContent(bin_hin)
                    error_hin = hin.GetBinError(bin_hin)
                    
                    # Content already in hout (in case several templates
                    # contribute to this process, e.g. ttV=ttW+ttZ)
                    bin_hout   = category.bins[i]
                    value_hout = hout.GetBinContent(bin_hout)
                    error_hout = hout.GetBinError(bin_hout)
                    
                    # Set new bin content
                    hout.SetBinContent(bin_hout, value_hout+value_hin )

                    # Set new bin error
                    # Assume errors are uncorrelated between the added-up
                    # templates/processes. Not correct in all cases, but
                    # should not matter because we only care about the errors
                    # in data_obs and total_procs, which are single templates
                    hout.SetBinError(bin_hout, math.sqrt(error_hout**2+error_hin**2) )
                    
            except RuntimeError:
                # OK if template does not exist in this category
                # (can happen for small processes)
                # Bins will have content 0 in hout
                pass
            
        if not template_exists:
            # Not OK if template does not exist in any of the categories
            raise RuntimeError(f"Template {template} found in none of the categories")

    return hout


def set_Poisson_errors(hist):
    new_hist = ROOT.TH1D(hist.GetName()+"_poissonerrors","",hist.GetNbinsX(),0,hist.GetNbinsX())
    new_hist.Sumw2(ROOT.kFALSE)
    new_hist.SetBinErrorOption(ROOT.TH1.kPoisson)
    for b in range(1,hist.GetNbinsX()+1):
        # Fill new histogram based on bin content of hist
        # Need to do it this way, via Fill, so that errors are computed correctly
        # (rounding necessary in case Asimov data used)
        for _ in range( int( round(hist.GetBinContent(b)) ) ):
            new_hist.Fill( hist.GetBinCenter(b) )

    return new_hist


def get_histograms(analysis_cfg):
    """Return map of { process : histogram }"""
    nbins = get_binning(analysis_cfg)
    hists = {}
    for process in analysis_cfg["processes"]:
        hist = get_histogram(process, nbins, analysis_cfg)
        if process.is_data:
            hist = set_Poisson_errors(hist)
        set_style(hist, process)
        hists[process.name] = hist

    return hists


def set_style(hist, process):
    color = style.process_color(process)
    if process.is_data:
        hist.SetMarkerStyle( style.marker_style() )
        hist.SetMarkerSize( style.marker_size() )
    if process.is_background:
        hist.SetFillColor( color )
    if process.is_total_background:
        hist.SetLineStyle(1)
    hist.SetMarkerColor( color )
    hist.SetLineColor( color )

    linestyle = style.process_linestyle(process)
    hist.SetLineStyle(linestyle)

    linewidth = style.process_linewidth(process)
    hist.SetLineWidth(linewidth)


def get_annotations(analysis_cfg, y_scale, pad_position):
    """Return the separator lines and labels for channels, categories, nodes"""

    # Store bin position and which boundaries are crossed
    channel_info  = [] # list of tuples (position, label)
    jettag_info   = [] # list of tuples (position, label)
    node_info     = [] # list of tuples (position, [label] ), 2nd element is a list, for multi-node labels in case of adjacent 1-bin nodes
    line_info     = [] # list of tuples (position, boundary type)

    # Iterate through all categories and identfiy boundary bins
    categories = analysis_cfg["categories"]
    for i in range(len(categories)):

        # the current channel, jettag categor, node
        channel = categories[i].channel
        jettag  = categories[i].jettag
        node    = categories[i].node
        # the x position of the lower bin boundary
        # bins have width 1, such that bin-1 is lower boundary
        x_pos = x_NDC(categories[i].bins[0]-1)

        if i==0:
            # the first bin starts a new channel, jettag category, and node
            # don't want a line here since it would overlap with y axis
            channel_info.append( (x_pos, channel) )
            jettag_info.append( (x_pos, jettag) )
            node_info.append( (x_pos, [node]) ) # elements are a list, for multi-node labels in case of adjacent 1-bin nodes
                      
        else:
            # identify if this is a boundary
            is_channel_boundary = ( channel != channel_info[-1][1] )
            is_jettag_boundary  = ( jettag != jettag_info[-1][1] )
            is_node_boundary    = ( node != node_info[-1][1][-1] )
        
            if is_channel_boundary:
                # add channel label and line info for this new channel
                channel_info.append( (x_pos, channel) )
                line_info.append( (x_pos, "channel" ) )
            if is_jettag_boundary:
                # add jettag label for this new category
                jettag_info.append( (x_pos, jettag) )
                if not is_channel_boundary:
                    # add jettag line if not already channel boundary
                    line_info.append( (x_pos, "jettag") )
            if is_node_boundary:
                if len(categories[i].bins)==1 and len(categories[i-1].bins)==1:
                    # if this node and also the previous have only 1 bin, 
                    # this is at least the 2nd in a row of adjacent 1-bin nodes
                    # --> append node label to list of node labels for this
                    # group of 1-bin nodes
                    node_info[-1][1].append( node )
                    # --> use a shorter vertical line to fit multi-node label
                    line_info.append( (x_pos, "node_1-bin") )
                else:
                    # otherwise, add a regular nodes label
                    node_info.append( (x_pos, [node]) )
                    if not (is_channel_boundary or is_jettag_boundary):
                        # add regular node line if not already bin or jettag
                        # boundary
                        line_info.append( (x_pos, "node") )

    # create vertical lines separating the channels, jettag
    # categories, and nodes
    lines = []
    # Iterate over all line infos
    y1_ndc = ROOT.gPad.GetBottomMargin() if pad_position=="bottom" else 0
    for info in line_info:
        
        # line height and style depend on whether it separates
        # channels, jettag categories, or nodes, or is for the ratio
        if info[1]=="channel":
            y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()
            line_style = 1
            line_color = ROOT.kBlack
        if info[1]=="jettag":
            y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.24*(1.+0.5*(y_scale-1.))
            line_style = 1
            line_color = ROOT.kBlack
        if info[1]=="node":
            y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.40
            line_style = 2
            line_color = ROOT.kBlack
        if info[1]=="node_1-bin":
            y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.36
            line_style = 2
            line_color = ROOT.kBlack
        if not pad_position=="top":
            y2_ndc = 1

        l = get_vertical_line(info[0], y1_ndc, y2_ndc)
        l.SetLineStyle(line_style)
        l.SetLineColor(line_color)
        lines.append(l)

    # create channel, jettag category, node labels
    labels = []

    # if for the top pad
    if pad_position=="top":
        # create channel labels
        # also include b-tag label, since same selection in a channel
        y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.06*y_scale
        for i,info in enumerate(channel_info):
            x = info[0]+0.005 if i > 0 else info[0]+0.015
            btags = "#geq3" if info[1]=="DL" else "#geq4"
            labels.append(
                get_label(
                    x=x, y=y2_ndc,
                    txt=f"{info[1]}", size=0.06*y_scale
                )
            )
            labels[-1].SetTextFont(62)
            labels.append(
                get_label(
                    x=x, y=y2_ndc-0.15,
                    txt=f"{btags} b-tags", size=0.05*y_scale
                )
            )
            
        # create jettag category labels
        y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.24*(1.+0.5*(y_scale-1.))
        for i,info in enumerate(jettag_info):
            x = info[0]+0.005 if i > 0 else info[0]+0.015
            labels.append(
                get_label(
                    x=x, y=y2_ndc,
                    txt=style.jettag_tex_name(info[1]),
                    size=0.05*y_scale, align=13
                )
            )
            if analysis_cfg["stxs"]:
                # create STXS bin label
                labels.append(
                    get_label(
                        x=x, y=y2_ndc-0.07,
                        txt="p_{T}^{H} bin",
                        size=0.05*y_scale, align=13
                    )
                )
            
        # create node labels
        for i,info in enumerate(node_info):
            if not info[1][0]=="":
                x = info[0]+0.005 if i > 0 else info[0]+0.015
                if len(info[1])>1:
                    y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.32
                    txt = f"{style.node_tex_name(info[1][0])}"
                    for i in range(1,len(info[1])):
                        txt += f", {style.node_tex_name(info[1][i])}"
                    txt += " cats."
                    labels.append(
                        get_label(
                            x=x, y=y2_ndc,
                            txt=txt, size=0.043*y_scale, align=13
                        )
                    )
                else:
                    y2_ndc = 1.-ROOT.gStyle.GetPadTopMargin()-0.37
                    txt = f"{style.node_tex_name(info[1][0])}"
                    if analysis_cfg["stxs"]: # for STXS plot
                        labels.append(
                            get_label(
                                x=x, y=y2_ndc-0.045,
                                txt=txt, size=0.043*y_scale, align=13
                            )
                        )
                    else: # for inclusive plot
                        if i==len(node_info)-1:
                            # Hack for DL(43) category: need to shift
                            # label a bit to the right
                            x += 0.007
                        labels.append(
                            get_label(
                                x=x, y=y2_ndc,
                                txt=txt, size=0.043*y_scale, align=13
                            )
                        )
                        labels.append(
                            get_label(
                                x=x, y=y2_ndc-0.04,
                                txt="cat.", size=0.043*y_scale, align=13
                            )
                        )
            
        
    return lines, labels


def create_cms_label(plot_cfg, y_scale):
    """Return CMS label"""

    # Coordinates of bottom-left corner
    x = ROOT.gStyle.GetPadLeftMargin() 
    y = 1.-ROOT.gStyle.GetPadTopMargin()+0.02
    # Create label
    txt="#bf{CMS} #it{Internal}"
    if plot_cfg["publication"]=="paper":
        txt="#bf{CMS}"
    if plot_cfg["publication"]=="preliminary":
        txt="#bf{CMS} #it{Preliminary}"
    l = get_label(x, y, txt=txt, size=0.09*y_scale, align=11)

    return l


def create_lumi_label(year, y_scale):
    """Return lumi label"""

    # Coordinates of bottom-left corner
    x = 1.-ROOT.gStyle.GetPadRightMargin()
    y = 1.-ROOT.gStyle.GetPadTopMargin()+0.02

    # Create lumi label for year
    lumi = ""
    if year == "2016":
        lumi = "36.3"
    if year == "2017":
        lumi = "41.5"
    if year == "2018":
        lumi = "59.7"

    # Create label
    l = get_label(x, y, txt=f"{lumi} fb^{{-1}} (13 TeV)", size=0.06*y_scale, align=31)

    return l


def create_fit_label(fit, y_scale):
    """Prefit or Postfit"""
    
    # Coordinates of bottom-left corner
    x = 1.-ROOT.gStyle.GetPadRightMargin()-0.07
    y = 1.-ROOT.gStyle.GetPadTopMargin()-0.085*y_scale

    # Create label
    if fit=="prefit":
        txt = "Prefit"
    if fit=="postfit":
        txt = "Postfit"
        x -= 0.01
    l = get_label(x, y, txt=txt, size=0.07*y_scale, align=11)

    return l


def get_vertical_line(x,y1,y2):
    """Return vertical TLine in NDC coordinates"""
    l = ROOT.TLine(x, y1, x, y2)
    l.SetNDC(True)
    l.SetLineStyle(1)
    l.SetLineColor(ROOT.kBlack)
    return l

def get_label(x, y, txt="", size=0.05, color=ROOT.kBlack, align=12):
    """Return TLatex in NDC coordinates (left-centre)"""
    l = ROOT.TLatex(x, y, txt)
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextColor(color)
    l.SetTextAlign(align)
    l.SetTextSize(size)
    return l

def create_legend(analysis_cfg, y_scale):
    x0 = 0.39
    x1 = 0.765
    y1 = 1.-ROOT.gStyle.GetPadTopMargin()-0.05
    y0 = y1-0.17*y_scale
    # adjust for STXS plots
    if analysis_cfg["stxs"]:
        x0 -= 0.20
        x1 -= 0.20
    
    l = ROOT.TLegend(x0,y0,x1,y1);
    l.SetNColumns(5)
    l.SetBorderSize(0)
    l.SetFillColor(0)
    l.SetFillStyle(0)
    l.SetTextFont(42)
    l.SetTextSize(0.05*y_scale)
    return l


def bin_lowx(b):
    """Return x value of lower edge of bin b"""

    # So far, just a hacked implementation
    # Works for the specific data_obs binning from 0-Nbins
    # with bin width 1
    return b-1

def x_NDC(x):
    # needed to retrieve correct coordinates from gPad
    ROOT.gPad.Update()
    return (x - ROOT.gPad.GetX1()) / (ROOT.gPad.GetX2()-ROOT.gPad.GetX1())

def y_NDC(y):
    # needed to retrieve correct coordinates from gPad
    ROOT.gPad.Update()
    return (y - ROOT.gPad.GetY1()) / (ROOT.gPad.GetY2()-ROOT.gPad.GetY1())


def set_gstyle(additional_signal_pad=False):
    ROOT.gStyle.Reset()

    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetEndErrorSize(0)
    ROOT.gStyle.SetOptStat(0)

    # For the canvas
    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)

    # For the frame
    ROOT.gStyle.SetFrameFillStyle(0)
    ROOT.gStyle.SetFrameLineWidth(1)
    ROOT.gStyle.SetPadLeftMargin(0.07) 
    ROOT.gStyle.SetPadRightMargin(0.01)
    if additional_signal_pad:
        ROOT.gStyle.SetPadTopMargin(0.12)
        ROOT.gStyle.SetPadBottomMargin(0.4)
    else:
        ROOT.gStyle.SetPadTopMargin(0.10)
        ROOT.gStyle.SetPadBottomMargin(0.37)

    # For the axis
    ROOT.gStyle.SetAxisColor(1,"XYZ")
    ROOT.gStyle.SetTickLength(0.03,"XYZ")
    ROOT.gStyle.SetNdivisions(510,"XYZ")
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetStripDecimals(False)
  
    # For the axis labels
    ROOT.gStyle.SetLabelColor(1,"XYZ")
    ROOT.gStyle.SetLabelFont(43,"XYZ") # ?3 font: size is given in pixel
    ROOT.gStyle.SetLabelSize(14,"XYZ") # label size in pixel
    ROOT.gStyle.SetLabelOffset(0.03,"X")

    # For the axis titles
    ROOT.gStyle.SetTitleColor(1,"XYZ")
    ROOT.gStyle.SetTitleFont(43,"XYZ") # ?3 font: size is given in pixel
    ROOT.gStyle.SetTitleSize(17,"XYZ") # title size in pixel
    ROOT.gStyle.SetTitleXOffset(1.2)
    ROOT.gStyle.SetTitleYOffset(1.6)

    
def get_error_band(hist, for_ratio=False):
    
    band = ROOT.TGraphAsymmErrors(hist.GetNbinsX())

    # Loop over all bins and copy bin content and error
    # as point value and error of TGraph
    for i in range(hist.GetNbinsX()):

        # x position at bin center
        bin = 1+i
        x = i+0.5

        # Bin content and errors
        value = hist.GetBinContent(bin)
        errdn = hist.GetBinErrorLow(bin)
        errup = hist.GetBinErrorUp(bin)
        
        # If error band for ratio, need to devide by central value
        if for_ratio:
            if value > 0:
                errdn = errdn/value
                errup = errup/value
            else:
                errdn = 0.
                errup = 0.
            value = 1.
            
        # Set point's central value and errors
        band.SetPoint(i, x, value)
        band.SetPointError(i, 0.5, 0.5, errdn, errup )

    # Set style for error band
    band.SetMarkerStyle( 0 )
    band.SetFillStyle( 1001 )
    band.SetFillColorAlpha( ROOT.kBlue, 0.20 )
    band.SetLineColorAlpha( ROOT.kBlue, 0.20 )

    #band.SetFillStyle( 3244 )
    #band.SetFillColor( ROOT.kBlack )
    
    return band

        

def get_ratios(data, denominator, signals=[]):
    r_data = ROOT.TGraphAsymmErrors(data.GetNbinsX()) 
    for i in range(data.GetNbinsX()):
        bin = 1+i
        x = i+0.5
        ref = denominator.GetBinContent(bin)
        if ref > 0:
            r_data.SetPoint(i, x, data.GetBinContent(bin)/ref)
            r_data.SetPointError(i, 0., 0., data.GetBinErrorLow(bin)/ref, data.GetBinErrorUp(bin)/ref)
    r_data.SetMarkerStyle( data.GetMarkerStyle() )
    r_data.SetMarkerColor( data.GetMarkerColor() )
    r_data.SetMarkerSize( data.GetMarkerSize() )

    r_sigs = []
    for sig in signals:
        name = str(np.random.rand())
        h = sig.Clone(name)
        h.Add(denominator)
        h.Divide(denominator)
        r_sigs.append(h)

    for s, sig in enumerate(signals):
        r_sigs[s].SetFillStyle( 0 )
        r_sigs[s].SetLineColor( sig.GetLineColor() )
        r_sigs[s].SetLineWidth( sig.GetLineWidth() )
        r_sigs[s].SetLineStyle( sig.GetLineStyle() )

    return r_data, r_sigs


def add_histos(histos):
    name = str(np.random.rand())
    h_added = histos[0].Clone(name)
    for h in histos[1:]:
        h_added.Add(h)

    return h_added
    

def create_canvas(additional_signal_pad=False):
    
    name = str(np.random.rand())
    c = ROOT.TCanvas(name,"",800,400)

    if additional_signal_pad:
        c.Divide(1,3)
        # top canvas for histograms
        c.GetPad(1).SetPad(0.0, 0.44, 1.0, 1.0)
        c.GetPad(1).SetBottomMargin(0) 
        # midle canvas for signals
        c.GetPad(2).SetPad(0.0, 0.28, 1.0, 0.44)
        c.GetPad(2).SetTopMargin(0)
        c.GetPad(2).SetBottomMargin(0) 
        # bottom canvas for ratios
        c.GetPad(3).SetPad(0.0, 0.0, 1.0, 0.28)
        c.GetPad(3).SetTopMargin(0)
    else:
        c.Divide(1,2)
        # top canvas for histograms
        c.GetPad(1).SetPad(0.0, 0.3, 1.0, 1.0)
        c.GetPad(1).SetBottomMargin(0) 
        # bottom canvas for ratios
        c.GetPad(2).SetPad(0.0, 0.0, 1.0, 0.3)
        c.GetPad(2).SetTopMargin(0)

    c.cd()
    
    return c 


def make_frame_histos(nbins):
    name = str(np.random.rand())
    frame = ROOT.TH1D(name,"",nbins,0,nbins)
    frame.GetYaxis().SetNdivisions(510)
    frame.GetYaxis().SetRangeUser(1.1E-1,5E6)
    frame.GetYaxis().SetTitle("Events")

    return frame


def make_frame_ratios(nbins, ratio_type, year):
    name = str(np.random.rand())
    frame = ROOT.TH1D(name,"",nbins,0,nbins)
    for bin in range(1,nbins+1):
        frame.SetBinContent(bin,1)
        frame.SetBinError(bin,0)
    frame.SetLineColor(ROOT.kBlack)
    frame.SetLineStyle(2)
    frame.GetYaxis().SetNdivisions(505)
    frame.GetXaxis().SetTitle(f"{year} discriminant bins")
    frame.GetYaxis().SetRangeUser(0.56,1.44)
    if ratio_type=="ratio_to_bkg":
        frame.GetYaxis().SetTitle("Events/bkg")
    else:
        frame.GetYaxis().SetTitle("Events/(S+B)")

    return frame


def make_frame_signal_pad(nbins):
    name = str(np.random.rand())
    frame = ROOT.TH1D(name,"",nbins,0,nbins)
    frame.SetLineColor(ROOT.kBlack)
    frame.GetYaxis().SetNdivisions(505)
    frame.GetYaxis().SetRangeUser(1.1E-2,18)
    frame.GetYaxis().SetTitle("Signal")
    
    # for log scale: the global offset value is interpreted
    # differently depending on log/linear scale... Jesus Christ
    # https://sft.its.cern.ch/jira/browse/ROOT-7433
    frame.GetYaxis().SetLabelOffset(-0.008)

    return frame


def make_frames(nbins, ratio_type, year, additional_signal_pad=False):
    """Return frames for top and bottom canvas"""

    frame_histos = make_frame_histos(nbins)
    frame_ratios = make_frame_ratios(nbins, ratio_type, year)
    frame_signal = make_frame_signal_pad(nbins)

    # set tick length
    # this is totally crazy how it works:
    # https://root-forum.cern.ch/t/inconsistent-tick-length/18563/9
    # set values here by trial and error for now
    base_length = 0.01
    scale_xy = 3.
    frame_histos.GetYaxis().SetTickLength(base_length)
    frame_histos.GetXaxis().SetTickLength(base_length*scale_xy)
    frame_ratios.GetYaxis().SetTickLength(base_length*1.5)
    frame_ratios.GetXaxis().SetTickLength(base_length*scale_xy*2.5)

    if additional_signal_pad:
        scale_xy = 4.
        frame_histos.GetYaxis().SetTickLength(base_length)
        frame_histos.GetXaxis().SetTickLength(base_length*scale_xy)
        frame_signal.GetYaxis().SetTickLength(base_length*0.9)
        frame_signal.GetXaxis().SetTickLength(base_length*scale_xy*4.0)
        frame_ratios.GetYaxis().SetTickLength(base_length*1.5)
        frame_ratios.GetXaxis().SetTickLength(base_length*scale_xy*2.0)

    
    return frame_histos, frame_ratios, frame_signal
    


def make_plot(analysis_cfg, plot_cfg):
    
    histos = get_histograms(analysis_cfg)

    bkgsig_stack = ROOT.THStack("bkg_stack","")
    signals = []
    legend_entries = []
    for process in analysis_cfg["processes"]:
        h = histos[process.name]
        if process.is_data:
            data = h
        if process.is_signal:
            signals.append(h)
            legend_entries.append( (h, style.process_tex_name(process), "L") )
        if process.is_total_background:
            tot_bkg = h
        if process.is_total_processes:
            tot_procs = h
        if process.is_background:
            bkgsig_stack.Add(h)
            legend_entries.append( (h, style.process_tex_name(process), "F") )
    for s in signals:
        s_filled = s.Clone()
        s_filled.SetFillColor(s.GetLineColor())
        bkgsig_stack.Add(s_filled)
    tot_sig = add_histos(signals)
    tot_sig.SetLineColor( style.process_color("ttH") )
    tot_sig.SetLineStyle( style.process_linestyle("ttH") )
        
    if plot_cfg["ratio"]=="ratio_to_bkg":
        if plot_cfg["additional_signal_pad"]:
            ratio_data, ratio_signals = get_ratios(data, tot_bkg, [tot_sig])
        else:
            ratio_data, ratio_signals = get_ratios(data, tot_bkg, signals)
    else:
        ratio_data, ratio_signals = get_ratios(data, tot_procs)

    # create error bands
    error_histo = get_error_band(tot_procs)
    error_ratio = get_error_band(tot_procs, for_ratio=True)
            
    frame_histos, frame_ratios, frame_signal = make_frames(data.GetNbinsX(), plot_cfg["ratio"], analysis_cfg["year"], plot_cfg["additional_signal_pad"])

    y_scale = 1.0
    if plot_cfg["additional_signal_pad"]:
        y_scale = 1.25
    
    can = create_canvas(plot_cfg["additional_signal_pad"])
    can.cd(1)
    frame_histos.Draw()
    bkgsig_stack.Draw("HISTsame")
    error_histo.Draw("2same")
    tot_procs.Draw("HISTsame")
    if not plot_cfg["additional_signal_pad"]:
        for s in signals:
            s.Draw("HISTsame")
    data.Draw("PEsame")

    legend = create_legend(analysis_cfg, y_scale)
    for i in reversed(legend_entries):
        legend.AddEntry(i[0], i[1], i[2])
    legend.AddEntry(data, "Data", "PE")
    legend.AddEntry(error_histo, "Syst", "F")
    legend.Draw()

    lines_categories_1, labels_categories_1 = get_annotations(analysis_cfg, y_scale=y_scale, pad_position="top")
    for line in lines_categories_1:
        line.Draw()
    for label in labels_categories_1:
        label.Draw()
    label_cms = create_cms_label(plot_cfg, y_scale)
    label_cms.Draw()
    label_lumi = create_lumi_label(analysis_cfg["year"], y_scale)
    label_lumi.Draw()
    label_fit = create_fit_label(analysis_cfg["fit"], y_scale)
    label_fit.Draw()
    ROOT.gPad.SetLogy(True)
    ROOT.gPad.RedrawAxis()

    can.cd(2)
    if plot_cfg["additional_signal_pad"]:
        frame_signal.Draw()
        for s in signals:
            s.Draw("HISTsame")
        lines_categories_2, labels_categories_2 = get_annotations(analysis_cfg, y_scale=y_scale, pad_position="middle")
        for line in lines_categories_2:
            line.Draw()
        ROOT.gPad.SetLogy(True)
        ROOT.gPad.RedrawAxis()
        can.cd(3)
        
    frame_ratios.Draw()
    error_ratio.Draw("2same")
    frame_ratios.Draw("HISTsame")
    for s in ratio_signals:
        s.Draw("HISTsame")
    frame_ratios.Draw("HISTsame")
    ratio_data.Draw("PE0same")
    lines_categories_3, labels_categories_3 = get_annotations(analysis_cfg, y_scale=y_scale, pad_position="bottom")
    for line in lines_categories_3:
        line.Draw()
    ROOT.gPad.SetLogy(False)
    ROOT.gPad.RedrawAxis()

    out_name = "{pre}_{year}_{fit}_{ratio}".format(
        pre=plot_cfg["out_name_prefix"],
        year=analysis_cfg["year"],
        fit=analysis_cfg["fit"],
        ratio=plot_cfg["ratio"]
        )
    can.SaveAs(f"{out_name}.pdf")
    

    
def print_setup(analysis_cfg):
    print("=========== SETUP ===========")

    print("PROCESSES")
    print("  Data:")
    for proc in [ p for p in analysis_cfg["processes"] if p.is_data ]:
        print(f"    {proc.str()}")
    print("  Background:")
    for proc in [ p for p in analysis_cfg["processes"] if p.is_background ]:
        print(f"    {proc.str()}")
    print("  Signal:")
    for proc in [ p for p in analysis_cfg["processes"] if p.is_signal ]:
        print(f"    {proc.str()}")

    print("\nCATEGORIES")
    for c in analysis_cfg["categories"]:
        print(f"  {c.str()}")
        
    print("-----------------------------")




if __name__ == '__main__':

    processes_incl = [
        # data
        Process(name="data", type="data",       templates=["data_obs"]),

        # signal ttH incl fit
        Process(name="ttH",  type="signal",     templates=["TotalSig"]),
        
        # backgrounds, first is lowest in stack
        Process(name="tHq",  type="background", templates=["tHq"]),
        Process(name="tHW",  type="background", templates=["tHW"]),
        Process(name="VV",   type="background", templates=["diboson"]),
        Process(name="ttG",  type="background", templates=["ttbarGamma"]),
        Process(name="Vjet", type="background", templates=["wjets", "zjets"]),
        Process(name="ttV",  type="background", templates=["ttbarW", "ttbarZ"]),
        Process(name="st",   type="background", templates=["singlet"]),
        Process(name="ttLF", type="background", templates=["ttlf"]),
        Process(name="ttC",  type="background", templates=["ttcc"]),
        Process(name="ttB",  type="background", templates=["ttbb"]),
        Process(name="QCD",  type="background", templates=["multijet"]),
        
        # total backgrounds and total backgrounds+signal (for ratio)
        Process(name="B",   type="total background", templates=["TotalBkg"]),
        Process(name="S+B", type="total processes",  templates=["TotalProcs"]),
    ]

    processes_stxs = [
        # data
        Process(name="data", type="data",       templates=["data_obs"]),

        # signal ttH STXS fit
        Process(name="ttH5",  type="signal",     templates=["ttH_PTH_GT300"]),
        Process(name="ttH4",  type="signal",     templates=["ttH_PTH_200_300"]),
        Process(name="ttH3",  type="signal",     templates=["ttH_PTH_120_200"]),
        Process(name="ttH2",  type="signal",     templates=["ttH_PTH_60_120"]),
        Process(name="ttH1",  type="signal",     templates=["ttH_PTH_0_60"]),
        
        # backgrounds, first is lowest in stack
        Process(name="VV",   type="background", templates=["diboson"]),
        Process(name="ttG",  type="background", templates=["ttbarGamma"]),
        Process(name="Vjet", type="background", templates=["wjets", "zjets"]),
        Process(name="ttV",  type="background", templates=["ttbarW", "ttbarZ"]),
        Process(name="st",   type="background", templates=["singlet"]),
        Process(name="ttLF", type="background", templates=["ttlf"]),
        Process(name="ttC",  type="background", templates=["ttcc"]),
        Process(name="ttB",  type="background", templates=["ttbb"]),
        
        # total backgrounds and total backgrounds+signal (for ratio)
        Process(name="B",   type="total background", templates=["TotalBkg"]),
        Process(name="S+B", type="total processes",  templates=["TotalProcs"]),
    ]
    
    categories_incl = [
        Category(channel="FH", jettag="7j4t", node=""),
        Category(channel="FH", jettag="8j4t", node=""),
        Category(channel="FH", jettag="9j4t", node=""),
        
        Category(channel="SL", jettag="5j4t", node="ttLF"),
        Category(channel="SL", jettag="5j4t", node="ttC"),
        Category(channel="SL", jettag="5j4t", node="tt2b"),
        Category(channel="SL", jettag="5j4t", node="tHq"),
        Category(channel="SL", jettag="5j4t", node="tHW"),
        Category(channel="SL", jettag="5j4t", node="ttH+ttb(b)"),
        
        Category(channel="SL", jettag="6j4t", node="ttLF"),
        Category(channel="SL", jettag="6j4t", node="ttC"),
        Category(channel="SL", jettag="6j4t", node="tt2b"),
        Category(channel="SL", jettag="6j4t", node="tHq"),
        Category(channel="SL", jettag="6j4t", node="tHW"),
        Category(channel="SL", jettag="6j4t", node="ttH+ttb(b)"),
        
        Category(channel="DL", jettag="3j3t", node=""),
        
        Category(channel="DL", jettag="4j3t", node="ttLF"),
        Category(channel="DL", jettag="4j3t", node="ttC"),
        Category(channel="DL", jettag="4j3t", node="ttH+ttB"),
    ]
    
    categories_stxs = [
        Category(channel="SL", jettag="5j4t", node="STXS1"),
        Category(channel="SL", jettag="5j4t", node="STXS2"),
        Category(channel="SL", jettag="5j4t", node="STXS3"),
        Category(channel="SL", jettag="5j4t", node="STXS4"),
        Category(channel="SL", jettag="5j4t", node="STXS5"),
        
        Category(channel="SL", jettag="6j4t", node="STXS1"),
        Category(channel="SL", jettag="6j4t", node="STXS2"),
        Category(channel="SL", jettag="6j4t", node="STXS3"),
        Category(channel="SL", jettag="6j4t", node="STXS4"),
        Category(channel="SL", jettag="6j4t", node="STXS5"),
        
        Category(channel="DL", jettag="4j3t", node="STXS1"),
        Category(channel="DL", jettag="4j3t", node="STXS2"),
        Category(channel="DL", jettag="4j3t", node="STXS3"),
        Category(channel="DL", jettag="4j3t", node="STXS4"),
        Category(channel="DL", jettag="4j3t", node="STXS5"),
    ]


    analysis_cfg_incl = {
        "file_name" : "inputs_ttH_incl_v28p3/combined_shapes_DLFHSL_all_years_incl.root",
        "processes" : processes_incl,
        "categories" : categories_incl,
        "stxs" : False,
        "year" : "NOT SET",
        "fit" : "NOT SET"
    }

    analysis_cfg_stxs = {
        "file_name" : "inputs_ttH_stxs_v16p2/combined_shapes_DLFHSL_all_years_stxs.root",
        "processes" : processes_stxs,
        "categories" : categories_stxs,
        "stxs" : True,
        "year" : "NOT SET",
        "fit" : "NOT SET"
    }
    
    plot_cfg = {
        "additional_signal_pad" : False,
        "ratio" : "ratio_to_bkg",
        "out_name_prefix" : "NOT SET",
        #"publication" : "preliminary"
        "publication" : "paper"
    }


    plot_stxs = False
    

    if plot_stxs:
        analysis_cfg = analysis_cfg_stxs
        plot_cfg["out_name_prefix"] = "summary_stxs"
        plot_cfg["additional_signal_pad"] = True
    else:
        analysis_cfg = analysis_cfg_incl
        plot_cfg["out_name_prefix"] = "summary_incl"


    # global style object    
    style = Style()
    set_gstyle(plot_cfg["additional_signal_pad"])
    print_setup(analysis_cfg)
        
    for fit in ["prefit", "postfit"]:
        analysis_cfg["fit"] = fit
        for year in ["2016", "2017", "2018"]:
            analysis_cfg["year"] = year
            make_plot(analysis_cfg=analysis_cfg, plot_cfg=plot_cfg)
            
