import os
import numpy as np
import ROOT
import json
ROOT.gROOT.SetBatch(True)

from optparse import OptionParser, OptionGroup
ROOT.PyConfig.IgnoreCommandLineOptions = True

fontsize = 0.04

# Parse separators
def is_separator(str):
    return str == "LINE" or str.startswith("SEPARATOR")

def separator_level(str):
    return ( 2 if str.startswith("SEPARATOR2") else 1 )    

def separator_has_description(str):
    return ":" in str

def get_separator_description(str):
    if separator_has_description(str):
        return str.split(":")[1]
    else:
        return None


def get_table_rows_standard(fit_results, table_format):
    rows = []

    # table header
    if table_format == "tex":
        rows.append("\\begin{tabular}{lccc}")
        rows.append("\\hline\\hline")
        rows.append("Parameter & Stat+Syst & Stat-Only & Significance \\\\")
        rows.append("\\hline")
    elif table_format == "md":
        rows.append("| Parameter | Stat+Syst | Stat-Only | Significance |")
        rows.append("| --- | --- | --- | --- |")

    # table content
    row_template = "STARTLINE {parameter} COLSEP {bestfit} COLSEP {statonly} COLSEP {signi} ENDLINE"
    entry_template = "{val:+.2f}  {up:+.2f}/{dn:+.2f}"
    counter = 0
    for name in fit_results["names"]:
        if is_separator(name):
            if table_format == "tex":
                rows.append("\\hline")
            continue
        bestfit_text = entry_template.format(
                val = fit_results["mu"][counter],
                up = fit_results["up"][counter],
                dn = fit_results["dn"][counter]
            )
        stat_only_text = entry_template.format(
                val = fit_results["mu"][counter],
                up = fit_results["up_stat"][counter],
                dn = fit_results["dn_stat"][counter]
            )
        signi_text = str(round(fit_results["sigma"][counter], 1)) \
                        if isinstance(fit_results["sigma"][counter], float) \
                            else fit_results["sigma"][counter]

        if table_format == "tex":
            row_template = row_template.replace("STARTLINE", "")
            row_template = row_template.replace("COLSEP","&")
            row_template = row_template.replace("ENDLINE", "\\\\")
            name = name.replace("#", "\\")
            if any(x in name for x in "[ ]".split()):
                name = "${}$".format(name)
            name = name.replace("_", "\\_")
        elif table_format == "md":
            row_template = row_template.replace("STARTLINE", "|")
            row_template = row_template.replace("COLSEP","|")
            row_template = row_template.replace("ENDLINE", "|")

        rows.append(row_template.format(
            parameter = name,
            bestfit = bestfit_text,
            statonly = stat_only_text,
            signi = signi_text
        ))
        counter += 1

    if table_format == "tex":
        rows.append("\\hline\\hline")
        rows.append("\\end{tabular}")

    return rows


def get_table_rows_paper(fit_results):
    rows = []

    has_sigma_exp = "sigma_exp" in fit_results.keys()

    # table header
    rows.append("\\begin{tabular}{lrc}")
    rows.append("  \\hline")
    rows.append("  & $\\hat{\\mu}\\,\\pm\\text{tot}\\,(\\pm\\text{stat}\\,\\,\\pm\\text{syst})$ & significance \\\\")
    if has_sigma_exp:
        rows[-1] = rows[-1].replace("significance","significance obs (exp)")
    rows.append("  \\hline")

    # table content
    row_template = "  {label} & ${bestfit:+.2f} ^{{{up:+.2f}}}_{{{dn:+.2f}}} \\;\\left( ^{{{up_stat:+.2f}}}_{{{dn_stat:+.2f}}} \\,\\, ^{{{up_syst:+.2f}}}_{{{dn_syst:+.2f}}} \\right)$ & ${signi:.1f}\\,\\sigma "
    if has_sigma_exp:
        row_template += "\\;\\left( {signi_asimov:.1f}\\,\\sigma \\right) "
    row_template += "$ \\\\"

    counter = 0
    for i,name in enumerate(fit_results["names"]):
        if is_separator(name):
            if i > 0:
                rows[-1] += "[\\cmsTabSkip]"
            if separator_has_description(name):
                text = get_separator_description(name)
                # rows.append(f"  {text} & & \\\\")
                rows.append("  {} & & \\\\".format(text))
            continue

        # clean label for tex
        label = fit_results["labels"].get(name, name)
        label = label.replace("#", "\\")
        label = label.replace("_", "\\_")

        if has_sigma_exp:
            rows.append(row_template.format(
                label = label,
                bestfit = fit_results["mu"][counter],
                up = fit_results["up"][counter],
                dn = fit_results["dn"][counter],
                up_stat = fit_results["up_stat"][counter],
                dn_stat = fit_results["dn_stat"][counter],
                up_syst = fit_results["up_syst"][counter],
                dn_syst = fit_results["dn_syst"][counter],
                signi = fit_results["sigma"][counter],
                signi_asimov = fit_results["sigma_exp"][counter]
            ))
        else:
            rows.append(row_template.format(
                label = label,
                bestfit = fit_results["mu"][counter],
                up = fit_results["up"][counter],
                dn = fit_results["dn"][counter],
                up_stat = fit_results["up_stat"][counter],
                dn_stat = fit_results["dn_stat"][counter],
                up_syst = fit_results["up_syst"][counter],
                dn_syst = fit_results["dn_syst"][counter],
                signi = fit_results["sigma"][counter]
            ))

        counter += 1

    # table footer
    rows.append("  \\hline")
    rows.append("\\end{tabular}")

    return rows


def load_values(result_dict, result_set, value_keyword, order, default = "--"):
    values = []
    for name in order:
        if is_separator(name): continue
        subdict = result_dict.get(name, {})
        if len(subdict) == 0: continue
        if not result_set in subdict.keys():
            return None
        set_dict = subdict.get(result_set, {})
        val = None
        if not isinstance(set_dict, dict):
            val = set_dict
        else:
            val = set_dict.get(value_keyword, default)
        if not val is None:
            print("For result '{}', saving value {} ({}/{})".\
                format(name, val, result_set, value_keyword))
            values.append(val)
    return np.array(values)


def create_table(fit_results, outname, table_format = "tex"):

    rows = []
    if table_format == "paper":
        rows += get_table_rows_paper(fit_results=fit_results)
    else:
        rows += get_table_rows_standard(fit_results=fit_results, table_format=table_format)

    file_ending = "tex" if table_format in ["tex","paper"] else table_format
    outpath = outname
    if not outpath.endswith(file_ending):
        outpath = ".".join([outpath,file_ending])
    print("writing table to {}".format(outpath))
    with open(outpath, "w") as f:
        f.write("\n".join(rows))


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
    labels = res.get("labels")
    if not labels:
        labels = { x:x for x in values.keys() }

    mu = load_values(   result_dict = values,
                        result_set = "bestfit",
                        value_keyword = "value",
                        order = order)
    print(mu)
    expected = load_values(   result_dict = values,
                        result_set = "expected",
                        value_keyword = "value",
                        order = order, default = 1)
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
    significance_expected = load_values(   result_dict = values,
                        result_set = "significance_expected",
                        value_keyword = None,
                        order = order)

    assert(len(mu) == len(upper))
    assert(len(upper) == len(lower))
    if upper_stat is not None:
        assert(len(upper) == len(upper_stat))
    else:
        upper_stat = np.full(len(mu),0.)
    if lower_stat is not None:
        assert(len(lower) == len(lower_stat))
    else:
        lower_stat = np.full(len(mu),0.)
    if expected is not None:
        assert(len(expected) == len(mu))
    else:
        expected = np.full(len(mu),1.)
    if significance is not None:
        assert(len(significance) == len(mu))
    else:
        significance = np.full(len(mu),0.)
    if significance_expected is not None:
        assert(len(significance_expected) == len(significance))

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
    display_style = kwargs.get("display_style")

    entry_names = [x for x in order if x in values.keys() or is_separator(x)]

    fit_results = {
        "names" : entry_names,
        "labels" : labels,
        "expected" : expected,
        "mu" : mu,
        "up" : upper,
        "dn" : lower,
        "up_stat" : upper_stat,
        "dn_stat" : lower_stat,
        "up_syst" : upper_syst,
        "dn_syst" : lower_syst,
        "sigma" : significance,
    }
    if significance_expected is not None:
        fit_results["sigma_exp"] = significance_expected


    create_plot(fit_results, outname=outname,
                include_signi=include_signi, style=kwargs, display_style=display_style)

    skip_table = kwargs.get("skip_table", False)
    table_format = kwargs.get("table_format", "tex")
    if not skip_table:
        create_table(fit_results=fit_results, outname=outname, table_format=table_format)

def create_plot(fit_results, outname, style, include_signi = False, display_style = "poi"):

    nchannels = fit_results["mu"].size
    print(nchannels)

    # calculate coordinates
    stepsize = style.get("stepsize", 2)
    coordinates = [ 1.5*i for i in range(1, nchannels*stepsize, stepsize)]
    channels = np.array(list(reversed(coordinates)))
    print(channels)
    zero = np.zeros(nchannels)

    xmin = np.min(fit_results["mu"] - np.abs(fit_results["dn"]))
    xmax = np.max(fit_results["mu"] + np.abs(fit_results["up"]))
    xmax = max(xmax, 10)
    print(xmin)
    print(xmax)
    title = "#hat{#mu} = #hat{#sigma}/#sigma_{SM}"
    if display_style == "XS":
        title = "#sigma in fb"
    upper_stretch = 1.2 if not display_style == "XS" else 1.2*2.5
    c,h = draw_canvas_histo(    nchannels = nchannels,
                                xmin = abs(xmin)*(-1.2), xmax = xmax*upper_stretch,
                                title = title,
                                positions = channels,
                                entry_names = fit_results["names"],
                                labels = fit_results["labels"],
                                lumilabel = style.get("lumilabel", ""))

    # line at SM expectation (default = 1)
    lines = []
    for i, exp_val in enumerate(reversed(fit_results["expected"]), 1):
        lines.append(ROOT.TLine())
        l = lines[-1]
        l.SetLineStyle( 2 )
        l.DrawLine( exp_val, 3*(i-1), exp_val, 3*i)

    print(fit_results["mu"])
    gmu_tot = ROOT.TGraphAsymmErrors( nchannels, fit_results["mu"], channels, np.abs(fit_results["dn"]), np.abs(fit_results["up"]), zero, zero )
    gmu_tot.SetMarkerStyle( 1 )
    gmu_tot.SetMarkerSize( 1 )
    gmu_tot.SetMarkerColor( 4 )
    gmu_tot.SetLineColor( 4 )
    gmu_tot.SetLineWidth( 2 )
    gmu_tot.Draw( "p" )
    gmu_tot.Print("range")

    gmu = ROOT.TGraphAsymmErrors( nchannels, fit_results["mu"], channels, np.abs(fit_results["dn_stat"]), np.abs(fit_results["up_stat"]), zero, zero )
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
    if display_style == "XS":
        headers = "#sigma       #color[4]{tot}      #color[2]{stat}    syst".split()
    print(headers)
    width = 10
    latex_parts = ["{value: ^{width}}".format(value = x, width = width) for x in headers]
    print(latex_parts)
    final_header = (" "*6).join(latex_parts)
    print(final_header)
    if include_signi:
        latex_parts += "       "

    uncertainty_template = "{{}}^{{{:+.2f}}}_{{{:-.2f}}}"
    if display_style == "XS":
        uncertainty_template = "{{}}^{{{:+.2f} %}}_{{{:-.2f} %}}"

    leg.SetNDC()
    leg.DrawLatex( 0.5, 0.87, final_header)
    upper_stretch = 1.05 if not display_style == "XS" else 1.05*2.5
    body_position = xmax*upper_stretch

    for ich,channel in enumerate(channels):
        res = ROOT.TLatex()
        res.SetTextFont( 42 )
        res.SetTextSize( 0.045 )
        res.SetTextAlign( 31 )
        uncertainties = uncertainty_template.format(fit_results["up"][ich],fit_results["dn"][ich])
        latex_parts = ["{val:.2f} #color[4]{{ {uncertainties: ^{width}} }}".\
                        format(val = fit_results["mu"][ich],uncertainties = uncertainties, width = width)]
        uncertainties = uncertainty_template.\
                        format(fit_results["up_stat"][ich],fit_results["dn_stat"][ich])
        latex_parts += ["#color[2]{{ {uncertainties: ^{width}} }}".\
                        format(uncertainties = uncertainties, width = width)]
        uncertainties = uncertainty_template.\
                        format(fit_results["up_syst"][ich],fit_results["dn_syst"][ich])
        latex_parts += ["{uncertainties: ^{width}}".\
                        format(uncertainties = uncertainties, width = width)]
        if include_signi:
            latex_parts += ["{:.1f} #sigma".format(fit_results["sigma"][ich])]

        res.DrawLatex( body_position, channel-0.2, " ".join(latex_parts))



    #draw_disclaimer()

    c.RedrawAxis()
    c.Modified()
    c.Update()
    exts = ["pdf", "png"]
    for ext in exts:
        c.SaveAs(".".join([outname, ext]), ext)

def draw_canvas_histo( nchannels, xmin, xmax, title, entry_names, labels, positions, \
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
    line1 = ROOT.TLine()
    line1.SetLineStyle(1)
    line1.SetLineWidth(2)
    line2 = ROOT.TLine()
    line2.SetLineStyle(1)
    print(entry_names)
    for name in entry_names:
        if n_entry > nchannels:
            raise ValueError("Number of entries is larger than \
                number of channels!")
        if is_separator(name):
            if not n_entry == 0:
                y_pos = (positions[n_entry-1] - positions[n_entry])/2.
                y_pos += positions[n_entry]
                if separator_level(name) == 1:
                    print("drawing line (level 1) at y = {}".format(y_pos))
                    line1.DrawLine(xmin, y_pos, xmax, y_pos)
                if separator_level(name) == 2:
                    print("drawing line (level 2) at y = {}".format(y_pos))
                    line2.DrawLine(xmin, y_pos, xmax, y_pos)
            continue
        nbin = yaxis.FindBin(positions[n_entry])
        label_clearname = labels.get(name, name)
        print("Setting label for bin {} to '{}'".format(nbin,label_clearname))
        yaxis.SetBinLabel(nbin,label_clearname)
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

    if lumilabel and not lumilabel == "":
        lumi = ROOT.TLatex()
        lumi.SetNDC()
        lumi.SetTextFont( 42 )
        lumi.SetTextSize( 0.035 )
        lumi.SetTextAlign( 31 )
        lumival = float(lumilabel)
        lumistr = "{:.1f} fb^{{-1}} (13 TeV)".format(lumival)
        if lumival > 100:
            lumistr = "{:.0f} fb^{{-1}} (13 TeV)".format(lumival)
        lumi.DrawLatex( 1-ROOT.gStyle.GetPadRightMargin(), 0.965, lumistr )

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

    style_group.add_option("-t", "--table-format",
                        help = " ".join("""
                            output format for results table.
                            Current choices: tex, md, paper.
                            Defaults to tex
                        """.split()),
                        dest = "table_format",
                        choices = "tex md paper".split(),
                        default = "tex"
                    )
    style_group.add_option("--display-style",
                        help = " ".join("""
                            Choose display style for plot.
                            Current choices: [poi, XS].
                            Choose 'poi' if you want to display
                            signal strengths.
                            If 'XS' is chosen, the uncertainties are
                            displayed with a percentage sign and
                            the x title is adjusted.
                            Defaults to 'poi'
                        """.split()),
                        dest = "display_style",
                        choices = "poi XS".split(),
                        default = "poi"
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
