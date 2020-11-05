import os
import numpy as np
import ROOT
import json
ROOT.gROOT.SetBatch(True)

results_json = "HIG-18-030_HIG18030_v01_results_unblinded.json"

from optparse import OptionParser, OptionGroup
ROOT.PyConfig.IgnoreCommandLineOptions = True

# Which result? Options: "17", "16p17"
result_version = "STXS" 
#result_version = "16p17" 

fontsize = 0.04

def parse_results(mu, upper, lower, upper_stat, lower_stat,\
                    order, significance):
    
    lines = []
    fitresult_template = "{val:+.2f}  {up:+.2f}/{down:+.2f}"
    line = """{parameter} & {bestfit} & {statonly} & {signi}\\\\"""
    counter = 0
    for name in order:
        if name == "LINE":
            lines.append("\\hline")
            continue
        bestfit_text = fitresult_template.format(
                val = mu[counter],
                up = upper[counter],
                down = lower[counter]
            )
        stat_only_text = fitresult_template.format(
                val = mu[counter],
                up = upper_stat[counter],
                down = lower_stat[counter]
            )
        signi_text = str(round(significance[counter], 1)) \
                        if isinstance(significance[counter], float) \
                            else significance[counter]
        name = name.replace("#", "\\")
        if any(x in name for x in "[ ]".split()):
            name = "${}$".format(name)
        lines.append(line.format(
            parameter = name.replace("_", "\\_"),
            bestfit = bestfit_text,
            statonly = stat_only_text,
            signi = signi_text
        ))
        counter += 1
    return lines

def load_values(result_dict, result_set, value_keyword, order):
    values = []
    for name in order:
        subdict = result_dict.get(name, {})
        set_dict = subdict.get(result_set, {})
        val = None
        if not isinstance(set_dict, dict):
            val = set_dict
        else:
            val = set_dict.get(value_keyword, None)
        if val:
            print("For result '{}', saving value {} ({}/{})".\
                format(name, val, result_set, value_keyword))
            values.append(val)
    return np.array(values)


def create_table(mu, upper, lower, upper_stat, lower_stat,\
                    entry_names, significance, outname):

    header = """\\begin{tabular}{lccc}
    \\hline\\hline
    Parameter & Stat+Syst & Stat-Only & Significance \\\\
    \\hline"""
    
    footer = """\\hline\\hline
    \\end{tabular}"""

    lines = [header]
    lines += parse_results(mu = mu, upper = upper, lower = lower,
                            upper_stat = upper_stat, lower_stat = lower_stat,\
                            order = entry_names, significance = significance)
    lines.append(footer)
    outpath = outname + ".tex"
    print("writing table to {}".format(outpath))
    with open(outpath, "w") as f:
        f.write("\n".join(lines))

def bestfit( **kwargs ):

    results_json = kwargs.get("results_json", "")

    if results_json == "" or not os.path.exists(results_json):
        raise ImportError("json file '{}' does not exist!".format(results_json))
    with open( results_json, "r" ) as in_file:
        res = json.load(in_file)

    values = res.get("results", {})
    order = res.get("order")
    if not order:
        order = values.keys()
    
    mu = load_values(   result_dict = values, 
                        result_set = "bestfit", 
                        value_keyword = "value", 
                        order = order)
    print(mu)
    upper = load_values(   result_dict = values, 
                        result_set = "bestfit", 
                        value_keyword = "up", 
                        order = order)
    lower = load_values(   result_dict = values, 
                        result_set = "bestfit", 
                        value_keyword = "down", 
                        order = order)
    print(mu)
    upper_stat = load_values(   result_dict = values, 
                        result_set = "stat_only", 
                        value_keyword = "up", 
                        order = order)
    lower_stat = load_values(   result_dict = values, 
                        result_set = "stat_only", 
                        value_keyword = "down", 
                        order = order)
    significance = load_values(   result_dict = values, 
                        result_set = "significance", 
                        value_keyword = None, 
                        order = order)

    
    assert(len(upper) == len(upper_stat))
    assert(len(lower) == len(lower_stat))
    assert(len(mu) == len(upper))
    assert(len(significance) == len(mu))
    assert(len(upper) == len(lower))
    
    upper_syst = np.sqrt(upper**2 - upper_stat**2)
    lower_syst = -np.sqrt(lower**2 - lower_stat**2)
    print(upper)
    print(upper_stat)
    print(upper_syst)
    print("="*130)
    print(lower)
    print(lower_stat)
    print(lower_syst)
    include_signi = kwargs.get("include_signi", False)
    outname = kwargs.get("outname", "test")


    entry_names = [x for x in order if x in values.keys() or x == "LINE"]

    create_plot(mu = mu, upper = upper, lower = lower,
                upper_stat = upper_stat, lower_stat = lower_stat,
                upper_syst = upper_syst, lower_syst = lower_syst, 
                entry_names = entry_names, outname = outname,
                include_signi = include_signi, style = kwargs)

    skip_table = kwargs.get("skip_table", False)

    if not skip_table:
        create_table(mu = mu, upper = upper, lower = lower,
                upper_stat = upper_stat, lower_stat = lower_stat,
                entry_names = entry_names, outname = outname,
                significance = significance)

def create_plot(mu, upper, lower, upper_stat, lower_stat,\
    upper_syst, lower_syst , entry_names, outname, style, include_signi = False):

    nchannels = mu.size
    print(nchannels)

    # calculate coordinates
    stepsize = style.get("stepsize", 2)
    coordinates = [ 1.5*i for i in range(1, nchannels*stepsize, stepsize)]
    channels = np.array(list(reversed(coordinates)))
    print(channels)
    zero = np.zeros(nchannels)

    xmin = np.min(mu - np.abs(lower))
    xmax = np.max(mu + np.abs(upper))
    print(xmin)
    print(xmax)

    c,h = draw_canvas_histo(    nchannels = nchannels, 
                                xmin = xmin-4, xmax = xmax+12, 
                                title = "#hat{#mu} = #hat{#sigma}/#sigma_{SM}",
                                positions = channels,
                                entry_names = entry_names ,
                                lumilabel = style.get("lumilabel", ""))

    # line at SM expectation of mu = 1
    l = ROOT.TLine()
    l.SetLineStyle( 2 )
    l.DrawLine( 1.0, 0, 1.0, 3*nchannels+0.5 )

    print(mu)
    gmu_tot = ROOT.TGraphAsymmErrors( nchannels, mu, channels, np.abs(lower), np.abs(upper), zero, zero )
    gmu_tot.SetMarkerStyle( 1 )
    gmu_tot.SetMarkerSize( 1 )
    gmu_tot.SetMarkerColor( 4 )
    gmu_tot.SetLineColor( 4 )
    gmu_tot.SetLineWidth( 2 )
    gmu_tot.Draw( "p" )
    gmu_tot.Print("range")

    gmu = ROOT.TGraphAsymmErrors( nchannels, mu, channels, np.abs(lower_stat), np.abs(upper_stat), zero, zero )
    gmu.SetMarkerStyle( 21 )
    gmu.SetMarkerSize( 1.5 )
    gmu.SetMarkerColor( 1 )
    gmu.SetLineColor( 2 )
    gmu.SetLineWidth( 2 )
    gmu.Draw( "pe1same" )

    leg = ROOT.TLatex()
    leg.SetTextFont( 42 )
    leg.SetTextSize( 0.035 )
    leg.SetTextAlign( 11 )
    headers = "#mu       #color[4]{tot}      #color[2]{stat}    syst".split()
    print(headers)
    latex_parts = ["{value: ^{width}}".format(value = x, width = str(len(x)+6)) for x in headers]
    print(latex_parts)
    print(" ".join(latex_parts))
    if include_signi:
        latex_parts += "       "
    leg.DrawLatex( 4.2, 3.1*nchannels, "".join(latex_parts))

    for ich,channel in enumerate(channels):
        res = ROOT.TLatex()
        res.SetTextFont( 42 )
        res.SetTextSize( 0.045 )
        res.SetTextAlign( 31 )
        uncertainty_template = "{{}}^{{{:+.2f}}}_{{{:-.2f}}}"
        uncertainties = uncertainty_template.format(upper[ich],lower[ich])
        latex_parts = ["{:+.2f} #color[4]{{ {: ^16} }}".\
                        format(mu[ich],uncertainties)]
        uncertainties = uncertainty_template.\
                        format(upper_stat[ich],lower_stat[ich])
        latex_parts += ["#color[2]{{ {: ^16} }}".\
                        format(uncertainties)]
        uncertainties = uncertainty_template.\
                        format(upper_syst[ich],lower_syst[ich])
        latex_parts += ["{: ^16}".\
                        format(uncertainties)]
        if include_signi:
            latex_parts += ["{:.1f} #sigma".format(significance[ich])]
        
        res.DrawLatex( xmax+11.5, channel-0.2, " ".join(latex_parts))

  
    
    #draw_disclaimer()

    c.RedrawAxis()    
    c.Modified()
    c.Update()
    exts = ["pdf", "png"]
    for ext in exts:
        c.SaveAs(".".join([outname, ext]), ext)

def draw_canvas_histo( nchannels, xmin, xmax, title, entry_names, positions, \
    lumilabel):
    c = ROOT.TCanvas( "c", "Canvas",800,750)
    c.Draw()
    
    #h = ROOT.TH2F( "h", "", 10, xmin, xmax, 3*nchannels+2, 0, 3*nchannels+2 )
    h = ROOT.TH2F( "h", "", 10, xmin, xmax, int(3.5*nchannels), 0, int(3.5*nchannels) )
    h.Draw()
    h.SetStats( 0 )
    h.SetXTitle( title )

    yaxis = h.GetYaxis()
    yaxis.SetLabelSize( 0.065 )
    n_entry = 0
    l = ROOT.TLine()
    l.SetLineStyle(1)
    print(entry_names)
    for name in entry_names:
        if n_entry > nchannels:
            raise ValueError("Number of entries is larger than \
                number of channels!")
        if name == "LINE":
            if not n_entry == 0:
                y_pos = (positions[n_entry-1] - positions[n_entry])/2.
                y_pos += positions[n_entry]
                print("drawing line at y = {}".format(y_pos))
                l.DrawLine(xmin, y_pos, xmax, y_pos)
            continue
        nbin = yaxis.FindBin(positions[n_entry])
        print("Setting label for bin {} to '{}'".format(nbin, name))
        yaxis.SetBinLabel(nbin, name)
        n_entry += 1


    pub = ROOT.TLatex()
    pub.SetNDC()
    pub.SetTextFont( 42 )
    pub.SetTextSize( 0.05 )
    pub.SetTextAlign( 13 )
    pub.DrawLatex( ROOT.gStyle.GetPadLeftMargin()+0.03,
                   1.-ROOT.gStyle.GetPadTopMargin()-0.033,
                   "#bf{CMS}" )
                #    "#bf{CMS} #it{Preliminary}")

    lumi = ROOT.TLatex()
    lumi.SetNDC()
    lumi.SetTextFont( 42 )
    lumi.SetTextSize( 0.035 )
    lumi.SetTextAlign( 31 )
    lumi.DrawLatex( 1-ROOT.gStyle.GetPadRightMargin(), 0.965, "{} fb^{{-1}} (13 TeV)".format(lumilabel) )

    return c,h


def my_style():
    
    ROOT.gStyle.SetTitleOffset( 1.5, "xy" )
    ROOT.gStyle.SetTitleFont( 62, "bla" )

    ROOT.gStyle.SetFrameLineWidth(2)
    ROOT.gStyle.SetPadLeftMargin(0.26)
    ROOT.gStyle.SetPadBottomMargin(0.14)
    ROOT.gStyle.SetPadTopMargin(0.05)
    ROOT.gStyle.SetPadRightMargin(0.02)

    ROOT.gStyle.SetTitleColor(1,"XYZ")
    ROOT.gStyle.SetLabelColor(1,"XYZ")
    ROOT.gStyle.SetLabelFont(42,"XYZ")
    ROOT.gStyle.SetLabelOffset(0.007,"XYZ")
    ROOT.gStyle.SetLabelSize(0.038,"XYZ")
    ROOT.gStyle.SetTitleFont(42,"XYZ")
    ROOT.gStyle.SetTitleSize(0.05,"XYZ")
    ROOT.gStyle.SetTitleXOffset(1.3)
    ROOT.gStyle.SetTitleYOffset(1.3)

    ROOT.gStyle.SetStatX( 0.88 )
    ROOT.gStyle.SetStatY( 0.87 )
    ROOT.gStyle.SetNdivisions( 505 )
    ROOT.gStyle.SetTickLength(0.04,"XZ")
    ROOT.gStyle.SetTickLength(0,"Y")
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetEndErrorSize(6)

    ROOT.gStyle.SetCanvasColor(-1) 
    ROOT.gStyle.SetPadColor(-1) 
    ROOT.gStyle.SetFrameFillColor(-1) 
    ROOT.gStyle.SetTitleFillColor(-1) 
    ROOT.gStyle.SetFillColor(-1) 
    ROOT.gStyle.SetFillStyle(4000) 
    ROOT.gStyle.SetStatStyle(0) 
    ROOT.gStyle.SetTitleStyle(0) 
    ROOT.gStyle.SetCanvasBorderSize(0) 
    ROOT.gStyle.SetFrameBorderSize(0) 
    ROOT.gStyle.SetLegendBorderSize(0) 
    ROOT.gStyle.SetStatBorderSize(0) 
    ROOT.gStyle.SetTitleBorderSize(0) 
    

def parse_arguments():
    usage = """
    Script to generate mu summary plots. Required input is a json file
    containing the fit results for syst+stat and stat-only.
    Additionally, you can provide a list 'order' in which these keys 
    are to be displayed. The file should be structured as follows:
    {
        "results": {
            NAME1: {
                "bestfit": {
                    "down": val, 
                    "up": val, 
                    "value": val
                }, 
                "stat_only": {
                    "down": val, 
                    "up": val, 
                    "value": val
                }
            },
            ...
        },
        "order": [
            NAME1,
            NAME2,
            NAME3,
            ...
        ]
    }
    The key 'NAME' will be used in the plot. 
    python %prog [options]
    """
    parser = OptionParser(usage = usage)

    required_group = OptionGroup(parser, "Required options")
    required_group.add_option("-j", "--jsonfile",
                        help = " ".join("""
                        path to the json file containing the values to plot
                        """.split()),
                        dest = "results_json",
                        metavar = "path/to/file.json",
                        type = "str"
                    )
    required_group.add_option("-o", "--outname",
                        help = " ".join("""
                            name of the output file
                        """.split()),
                        dest = "outname",
                        metavar = "path/to/outfile",
                        type = "str"
                    )
    parser.add_option_group(required_group)
    
    style_group = OptionGroup(parser, "Style Options")
    style_group.add_option("-s", "--stepsize",
                        help = " ".join("""
                            change this number to adjust the space between
                            the entries. The distance between entries is 
                            calculated with 
                            '1.5*i for i in range(0, nentires, stepsize)'
                            Default: 2
                        """.split()),
                        dest = "stepsize",
                        default = 2,
                        type = "int"
                    )
    style_group.add_option("-f", "--fontsize",
                        help = " ".join("""
                            use this font size in the plot.
                            Default: 0.04
                        """.split()),
                        dest = "fontsize",
                        default = 0.04,
                        type = "float"
                    )
    style_group.add_option("-l", "--lumi-label",
                        help = " ".join("""
                            use this string as lumi label.
                            Output will look 'LUMILABEL fb^-1 (13 TeV)
                            Default: 137.1
                        """.split()),
                        dest = "lumilabel",
                        default = "137.1",
                        type = "str"
                    )
    style_group.add_option("--significance",
                        help = " ".join("""
                            add the signficance to each row.
                            Default is false
                        """.split()),
                        dest = "include_signi",
                        action = "store_true",
                        default = False,
                    )

    parser.add_option_group(style_group)

    options, args = parser.parse_args()
    global fontsize
    fontsize = options.fontsize

    return options, args

if __name__ == '__main__':
    options, args = parse_arguments()
    my_style()
    #limits()
    bestfit( **vars(options) )
