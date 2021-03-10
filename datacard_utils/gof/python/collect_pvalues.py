import os
import sys
import json
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import pandas as pd
import numpy as np

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.join(thisdir, "..", "..", "base")
if not basedir in sys.path:
    sys.path.append(basedir)
from batchConfig import batchConfig
from helperClass import helperClass
from glob import glob
from optparse import OptionParser
from subprocess import call

ROOT.gStyle.SetOptStat(0)

default_bins = 100
missing = []
def parse_arguments():
    usage = """
    usage: %prog [options] path/to/directories/with/GOF
    """

    parser = OptionParser(usage=usage)

    parser.add_option(  "-c", "--config",
                        help="""config file containing 
                                -   the key with which variable names are 
                                    separated in file names
                                -   the identifier for the GOF with data
                                -   the directory with the GOF results with data
                                -   the identifier for GOF with toys
                                -   the directory with the GOF results with toys
                            """,
                        type = "str",
                        dest = "config",
                        default = "default/path"
                    )
    parser.add_option(  "-m", "--mode",
                        help = "create 1D or 2D histograms with p-values",
                        metavar = "1D, 2D",
                        choices = ["1D", "2D"],
                        dest = "mode"
                    )
    parser.add_option(  "-o", "--outputname",
                        help = "name of output .pdf file (default: pmatrix_1D)",
                        dest = "outname",
                        default = "pmatrix"
                    )
    parser.add_option(  "-n", "--nbins",
                        help = "number of bins to be used for distributions of test statistics for respective observables",
                        dest = "nbins",
                        type = "int",
                        default = 100
                    )
    parser.add_option(  "--skipDistributions",
                        help = "do not print the distributions of the test statistic for the respective variables (default: False)",
                        dest = "skip_distr",
                        action = "store_true",
                        default = False
                    )
    parser.add_option(  "--exclude", "-e",
                        metavar = "path/to/file/with/excluded/variables",
                        help = "exclude these variables",
                        dest = "exclude_file"
                    )
    parser.add_option( "--translation","-t",
                        metavar = "path/to/csv/file/with/translated/variablenames",
                        help = "file with clear variable names, requires two comma separated colums 'variable' and 'displayname'",
                        dest = "translationFile",
                        default = None)
    parser.add_option( "--format","-f",
                        help = " ".join(
                            """
                            format of the output table. Current choices are
                            txt, tex, markdown. Default: txt
                            """.split()
                        ),
                        dest = "format",
                        default = "txt",
                        choices=["txt", "tex", "markdown", "md"])

    (options, args) = parser.parse_args()
    if not os.path.exists(options.config):
        parser.error("Path to config is invalid!")
    if not options.exclude_file is None and not os.path.exists(options.exclude_file):
        parser.error("Path '%s' does not exist!" % options.exclude_file)
    args = [a for a in args if not ( a.endswith(".pdf") or a.endswith(".txt") or a.endswith(".root") or a.endswith(".png") )]
    global default_bins
    default_bins = options.nbins
    return options, args

def get_list_of_vars(dictionary, vallist=[], exclude_list = None):
    if isinstance(dictionary, dict):
        print dictionary
        keys = sorted(dictionary)
        print "vallist: ", vallist
        print "keys: ", keys
        if vallist is None:
            vallist = keys
        else:
            tmp = vallist + keys
            print "joint: ", tmp
            vallist = sorted(list(set(tmp)))
        
        print "new vallist: ", vallist
        for key in keys:
            vallist = get_list_of_vars(dictionary[key], vallist, exclude_list)
    if not exclude_list is None:
        print "-"*130
        print "CHECKING FOR EXCLUSIONS"
        print "-"*130
        vallist = [x for x in vallist if not any(x.endswith(e) for e in exclude_list)]
    return vallist

def setup_histogram_axis(pmatrix, varlist, translationFile = None):
    labelsize = 0.04
    is_TH2 = isinstance(pmatrix, ROOT.TH2)
    for i, var in enumerate(varlist):
        pmatrix.GetXaxis().SetBinLabel(i+1, cleanup_varname(var, translationFile))
        if is_TH2:
            pmatrix.GetYaxis().SetBinLabel(i+1, cleanup_varname(var, translationFile))
        elif i == 0:
            pmatrix.GetYaxis().SetTitle("p-value")

    pmatrix.GetXaxis().SetLabelSize(labelsize)
    pmatrix.LabelsOption("v")
    pmatrix.GetYaxis().SetLabelSize(labelsize)

def create_2D_matrix(dictionary, outname, exclude_list = None, out_format = "txt"):
    if len(dictionary) != 0:
        ROOT.gStyle.SetPaintTextFormat(".2f")
        outname += "_2D"
        ROOT.gStyle.SetOptStat(0)
        outfile = ROOT.TFile(outname + ".root", "RECREATE")
        varlist = get_list_of_vars(dictionary = dictionary, exclude_list = exclude_list)
        canvas = ROOT.TCanvas()
        print dictionary
        print varlist
        nvars = len(varlist)
        pmatrix = ROOT.TH2D("pmatrix", "", nvars, 0, nvars, nvars, 0, nvars)

        pmatrix.GetZaxis().SetTitle("p-value")
        setup_histogram_axis(pmatrix = pmatrix, varlist = varlist)    

        for v1 in dictionary:
            if not v1 in varlist: continue
            for v2 in dictionary[v1]:
                if not v2 in varlist: continue
                j = varlist.index(v1)+1
                i = varlist.index(v2)+1
                # print "getting", v1, v2, varlist.index(v1)+1, varlist.index(v2)+1, i, j
                # print varlist
                if j>i:
                    # print "switching i and j!"
                    # print "before:", i, j
                    tmp = i
                    i = j
                    j= tmp
                    # print "after:", i, j

                val = dictionary[v1][v2]
                print "setting bins ({0}, {1}) for vars ({2}, {3}) to {4}".format(i,j,v1,v2, val)
                if val <= 0.05:
                    print "-"*130
                    print "WARNING: PVAL FOR COMBINATION {0}/{1} IS {2}".format(v1, v2, val)
                    print "-"*130
                pmatrix.SetBinContent(i, j, val)
                pmatrix.SetBinContent(j, i, val)
        pmatrix.Write()
        pmatrix.Draw("colzTEXT")
        canvas.SetRightMargin(0.15)
        canvas.SetTopMargin(0.01)
        canvas.SetBottomMargin(0.55)
        canvas.SetLeftMargin(0.35)
        canvas.SaveAs(outname + ".pdf")
        canvas.SaveAs(outname + ".png")
        outfile.Close()
        write_pvals_to_file(pvals = dictionary,
                            filename = outname + ".txt",
                            mode = "2D", 
                            exclude_list = exclude_list,
                            out_format = out_format)
    else:
        print "ERROR: Did not receive anything to draw!"  

def cleanup_varname(name, translationFile = None):
    orig_name = name
    name = name.replace("_hdecay","")
    # name = name.replace("ge4j_ge3t_","")
    # name = name.replace("ge4j_3t_","")
    # name = name.replace("ge4j_ge4t_","")
    # name = name.replace("ge6j_ge3t_","")
    # name = name.replace("4j_ge3t_","")
    # name = name.replace("le5j_ge3t_","")
    # name = name.replace("5j_ge3t_","")
    # name = name.replace("ljets_","")
    
    if not translationFile is None:
        
        name = name.replace("_0","[0]")
        name = name.replace("_1","[1]")
        name = name.replace("_2","[2]")
        name = name.replace("_3","[3]")
        name = name.replace("_4","[4]")
        name = name.replace("_5","[5]")
        try:
            name = translationFile.loc[name, "displayname"]
            name = name.replace("\\","#")
        except:
            print("Could not translate variable name '{}'".format(orig_name))
    return name

def create_1D_matrix(dictionary, outname, exclude_list = None, translationFile = None,\
                        out_format = "txt"):
    if len(dictionary) != 0:
        ROOT.gStyle.SetOptStat(0)
        outname += "_1D"

        outfile = ROOT.TFile(outname+".root", "RECREATE")
        #sort list of varnames according to pvalues
        varlist = [x[0] for x in sorted(dictionary.items(), key = lambda x: x[1], reverse = True)]
        canvas = ROOT.TCanvas()
        print dictionary
        print varlist
        if exclude_list:
            print "-"*130
            print "CHECKING FOR EXCLUSIONS"
            print exclude_list
            print "-"*130
            varlist = [x for x in varlist if not any(x.endswith(v) for v in exclude_list)]
            print varlist
        nvars = len(varlist)
        pmatrix = ROOT.TH1D("pmatrix", "", nvars, 0, nvars)

        setup_histogram_axis(pmatrix = pmatrix, varlist = varlist, translationFile = translationFile)

        for v1 in dictionary:
            if v1 in varlist:
                j = varlist.index(v1)+1
                pmatrix.SetBinContent(j, dictionary[v1])
        pmatrix.GetYaxis().SetRangeUser(0, 1.1)
        pmatrix.Write()
        pmatrix.SetLineWidth(2)
        pmatrix.SetLineColor(ROOT.kBlack)
        pmatrix.Draw("Hist")
        l = ROOT.TLine()
        l.SetLineColor(ROOT.kRed)
        xmin = pmatrix.GetXaxis().GetXmin()
        xmax = pmatrix.GetXaxis().GetXmax()
        l.DrawLine(xmin, 0.05, xmax, 0.05)
        l.SetLineWidth(2)
        canvas.SetTopMargin(0.01)
        canvas.SetBottomMargin(0.55)

        canvas.SaveAs(outname + ".pdf")
        canvas.SaveAs(outname + ".png")
        outfile.Close()
        write_pvals_to_file(pvals = dictionary,
                            filename = outname + ".txt", 
                            mode = "1D", 
                            exclude_list = exclude_list,
                            out_format = out_format)
    else:
        print "ERROR: Did not receive anything to draw!"

def get_variable_names(directory, config):
    var1, var2 = directory.split(config["variable_separator"])
    if var1 == "" or var2 == "":
        var1, var2 = None
    return var1, var2

def get_root_file(identifier):
    wildcard = "higgsCombine*%s*.root"
    files = glob(wildcard % identifier)
    if len(files) > 1:
        msg = "There is more than one file accessable with"
        msg += " '%s'!" % (wildcard % identifier)
        msg += "\nCurrent dir: " + os.getcwd()
        hadd_output = "hadded_%s.root" % identifier
        print hadd_output
        msg += "\nWill hadd files into " + hadd_output
        print msg
        call(["hadd -f %s %s"%(hadd_output, " ".join(files))],shell = True)
        return hadd_output
        # sys.exit(msg)
    if len(files) == 0:
        sys.exit("Could not find file with expression '%s' in '%s'" % (wildcard % identifier, os.getcwd()))
    return files[-1]

def construct_histo(values, autorange = False):
    upper_edge = max(values)
    lower_edge = min(values)
    if upper_edge == lower_edge:
        print "WARNING: There is no value range. This should not happen"
        upper_edge += 1
        lower_edge -= 1
    nbins = 0
    if autorange:
        nbins = int(upper_edge - lower_edge)
    
    nbins = nbins if nbins >0 else default_bins
    ROOT.gStyle.SetOptStat(0)
    h = ROOT.TH1D("h", "test statistics", nbins, lower_edge, upper_edge)
    for v in values:
        h.Fill(v)
    return h

def load_values(identifier):
    filepath = get_root_file(identifier = identifier)
    if not filepath:
        return None
    f = ROOT.TFile(filepath)

    lkeys = f.GetListOfKeys()
    if not "limit" in lkeys:
        msg = "Could not find limit tree in GOF output of file "
        msg += "'%s'!" % os.path.abspath(filepath)
        sys.exit(msg)
    tree = f.Get("limit")
    vals = []
    print "loading tree with %s entries" % str(tree.GetEntries())
    for e in tree:
        vals.append(e.limit)
    f.Close()
    if len(vals) == 1:
        return vals[0]
    else:
        return vals

def getCanvas(name = ""):
    canvas = ROOT.TCanvas(name, name, 1024, 768)
    canvas.SetTopMargin(0.07)
    canvas.SetBottomMargin(0.15)
    canvas.SetRightMargin(0.05)
    canvas.SetLeftMargin(0.15)
    canvas.SetTicks(1,1)
    canvas.cd(1)
    return canvas


def printCMSLabel(canvas):
    canvas.cd(1) 
    l = canvas.GetLeftMargin() 
    t = canvas.GetTopMargin() 
    r = canvas.GetRightMargin() 
    b = canvas.GetBottomMargin() 
 
    latex = ROOT.TLatex() 
    latex.SetNDC() 
    latex.SetTextColor(ROOT.kBlack) 
    latex.SetTextSize(0.04)

    text = "CMS #bf{#it{private Work}}"

    latex.DrawLatex(l,1.-t+0.01, text) 

def getLegend():
    legend=ROOT.TLegend(0.50,0.7,0.95,0.9)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.04);
    legend.SetFillStyle(0);
    return legend

def get_pvalue(directory, config, skip_distr = False):
    """
    readout p-values from limit trees of GOF test.
    Reads value for test static for GOF with data (-> t_0) and
    creates one histogram for GOF with toys (-> distribution f(t)), 
    respectively. p-value is defined as the integral of f(t) from t_0 to infty
    """
    directory = os.path.abspath(directory)
    data_identifier = config["id_data"]
    data_dir = config["data_dir"]
    toy_identifier = config["id_toys"]
    toy_dir = config["toy_dir"]
    currentdir = os.getcwd()
    os.chdir(os.path.join(directory, data_dir))
    value_data = load_values(identifier = data_identifier)
    os.chdir(currentdir)
    if not value_data:
        return None
    os.chdir(directory)
    varname = os.path.basename(directory)
    outname = varname + "_gof_distribution.root"
    outfile = ROOT.TFile.Open(outname, "RECREATE")
    c = getCanvas()

    os.chdir(toy_dir)
    vals_toys = load_values(identifier = toy_identifier)
    h_toys = construct_histo(vals_toys)
    if not h_toys:
        os.chdir(currentdir)
        return None
    os.chdir(directory)
    htoys_copy = h_toys.Clone()
    htoys_copy.Scale(1./h_toys.Integral())

    data_bin = h_toys.FindBin(value_data)
    # pval = htoys_copy.Integral(data_bin, htoys_copy.GetNbinsX())
    count = sum([v > value_data for v in vals_toys])
    print(count)
    print(len(vals_toys))
    pval = float(count)/len(vals_toys)
    print("pval = {}".format(pval))
    if not skip_distr:

        # define chi2 pdf for fit
        chi2f = ROOT.TF1("chi2","[0]*ROOT::Math::chisquared_pdf(x,[1])", 0., 100.)     
        chi2f.SetParameters(10,10)
        chi2f.SetParNames("constant","dof")

        # draw line of data test stat
        line = ROOT.TLine()
        line.SetLineColor(ROOT.kBlue)
        line.SetLineWidth(2)

        # dummy line for legend
        line2 = ROOT.TLine()
        line2.SetLineColor(ROOT.kRed)

        # min max values
        ymin = h_toys.GetYaxis().GetXmin()
        # ymax = h_toys.GetYaxis().GetXmax()
        ymax = h_toys.GetBinContent(h_toys.GetMaximumBin())
    
        # filled histogram for pvalue
        pvalh = h_toys.Clone()
        for iBin in range(data_bin-1):
            pvalh.SetBinContent(iBin+1, 0.)
            pvalh.SetBinError(iBin+1, 0.)
        pvalh.SetLineWidth(0)
        pvalh.SetFillColor(ROOT.kAzure)
        pvalh.SetFillColorAlpha(ROOT.kAzure, 0.5)

        # test stat distribution
        h_toys.SetLineColor(ROOT.kBlack)
        h_toys.SetMarkerStyle(20)
        h_toys.SetMarkerSize(1)
        h_toys.SetMarkerColor(ROOT.kBlack)
        h_toys.SetTitle("")
        h_toys.GetXaxis().SetLabelSize(0.04)
        h_toys.GetXaxis().SetTitleSize(0.04)
        h_toys.GetYaxis().SetLabelSize(0.04)
        h_toys.GetYaxis().SetTitleSize(0.04)
        h_toys.GetXaxis().SetTitle("GoF (saturated) test stat. value")
        h_toys.GetYaxis().SetTitle("number of pseudo experiments")

        # fit chi2 pdf
        h_toys.Fit(chi2f)
        fitresult   = h_toys.Fit(chi2f,"S")
        dof         = fitresult.Parameter(1)
        doferr      = fitresult.ParError(1)

        # draw
        h_toys.Draw("PE")
        pvalh.Draw("hist same")
        h_toys.Draw("PE SAME")
        print "draw line from ({0},{1}) to ({2}, {3})".format(value_data, ymin, value_data, ymax)
        line.DrawLine(value_data, ymin, value_data, ymax)

        # get legend
        legend = getLegend()
        legend.AddEntry(h_toys,"pseudo experiments","P")
        legend.AddEntry(line,"observed test stat. = {:.2f}".format(value_data),"L")
        legend.AddEntry(pvalh,"p-value = {:.2f}".format(pval),"F")
        legend.AddEntry(line2, "#chi^{{2}} fit, ndf = {:.1f} #pm {:.1f}".format(dof, doferr),"L")
        legend.Draw()
    
        # add label        
        printCMSLabel(c)

        # save
        outfile.WriteTObject(h_toys)
        outfile.WriteTObject(c)
        print "saving distribution for", directory
        c.Print(outname.replace(".root", ".png"))
        c.Print(outname.replace(".root", ".pdf"))
        outfile.Close()

    print "p-value: ", pval
    os.chdir(currentdir)
    return pval

def create_2D_entry(varname, pvaldic, config, pval):
    var1, var2 = get_variable_names(directory = varname, 
                                            config = config)
    if var1 is None or var2 is None:
        print "ERROR: Could not load variable names from", varname
        return None
    print "saving p-value {0} for combination ({1}, {2})".format(
        pval, var1, var2) 
    if not var1 in pvaldic:
        pvaldic[var1] = {}
    pvaldic[var1][var2] = pval

def create_header(out_format):
    out_string = ""
    if out_format == "markdown" or out_format == "md":
        out_string = "| variable name | p value |\n"
        out_string += "| --- | --- |"
    elif out_format == "tex":
        out_string = """
        \\begin{tabular}{lc}

        \hline\hline
        Variable Name & p value \\\\
        \hline\hline        
        """
    else:
        out_string = "variablename,pvalue"
    return out_string

def create_table_line(varname, pvalue, out_format):
    line = ""
    if out_format == "markdown" or out_format == "md":
        line = "| {} |".format(" | ".join([varname, str(pvalue)]))
    elif out_format == "tex":
        line = " & ".join([varname.replace("_", "\\_"), str(pvalue)]) + "\\\\"
    else:
        line = ",".join([varname, str(pvalue)])
    return line

def create_table_footer(out_format):
    out_string = ""
    if out_format == "tex":
        out_string = """
        \hline\hline
        \end{tabular}
        """
    return out_string

def write_sorted_lines(pvals, exclude_list = None, out_format = "txt"):
    varlist = [x[0] for x in sorted(pvals.items(), key = lambda x: x[1], reverse = True)]
    lines = []
    lines.append(create_header(out_format))
    values = []
    if not exclude_list is None:
        varlist = [x for x in varlist if not any(x.endswith(v) for v in exclude_list)]
    for var in varlist:
        line = create_table_line(   varname = cleanup_varname(var), 
                                    pvalue = pvals[var], 
                                    out_format = out_format)
        lines.append(line)
        values.append(pvals[var])
    footer = create_table_footer(out_format)
    if not footer == "":
        lines.append(footer)
    return lines, values

def write_all_values(values, outfilename):
    print "creating histogram with all p values"
    
    outfile = ROOT.TFile(outfilename + ".root", "RECREATE")
    h = construct_histo(values = values, autorange = True)
    outfile.WriteTObject(h, h.GetName())
    c = ROOT.TCanvas()
    h.Draw()
    c.SaveAs(outfilename + ".pdf")
    c.SaveAs(outfilename + ".png")
    outfile.WriteTObject(c, "canvas_all_pvals")
    outfile.Close()



def write_pvals_to_file(pvals, filename, mode, exclude_list = None,\
                         out_format = "txt"):
    lines = []
    line = ""

    values = []
    tmpvaluelist = []
    if mode == "1D":
        lines, tmpvaluelist = write_sorted_lines(pvals = pvals, 
                                                exclude_list= exclude_list, 
                                                out_format = out_format)
        values += tmpvaluelist
    elif mode == "2D":
        for key in pvals:
            lines.append(key + ":")
            tmp, tmpvaluelist = write_sorted_lines(pvals = pvals[key], 
                                                    exclude_list = exclude_list, 
                                                    out_format = out_format)
            lines += ["\t"+x for x in tmp]
            values += tmpvaluelist
    filename = ".".join(filename.split(".")[:-1]+ [out_format])
    print "writing lines to", filename
    print "\n".join(lines)
    with open(filename, "w") as f:
        f.write("\n".join(lines))

    rfilename = ".".join(filename.split(".")[:-1]) + "_all_pvals"
    write_all_values(values = values, outfilename = rfilename)

    # optimal_values = auto_exclude(values)
    # write_all_values(values= values, )
    

def main(*wildcards, **kwargs):
    pvals = {}
    mode = kwargs.get("mode", "1D")
    skip_distr = kwargs.get("skip_distr", False)
    config = kwargs.get("config", None)
    if not (mode == "1D" or mode == "2D"):
        sys.exit("Did not recognize mode!")
    with open(config) as f:
        config = json.load(f)
    for w in wildcards:
        for directory in glob(w):
            directory = os.path.abspath(directory)
            varname = os.path.basename(directory)
            print "loading pvalue for dir '%s'" % directory
            pval = get_pvalue(directory = directory, config = config, 
                                skip_distr = skip_distr)
            if not pval: continue
            if mode == "1D":
                pvals[varname] = pval
            elif mode == "2D":
                create_2D_entry(varname = varname, pvaldic = pvals,
                                config = config, pval = pval
                                )
            else:
                print "ERROR: Did not recognize mode '%s'!" % mode
    
    print "done collecting p values!"
    exclude_list = None
    exclude_file = kwargs.get("exclude_file", None)
    if not exclude_file is None:
        exclude_list = []
        with open(exclude_file) as f:
            exclude_list = f.read().splitlines()
    
    translationFile = kwargs.get("translationFile", None)
    if not translationFile is None:
        translationFile = pd.read_csv(translationFile, sep = ",").set_index("variablename", drop = True)
    outname = kwargs.get("outname", "pmatrix")
    out_format = kwargs.get("format", "txt")
    if out_format == "markdown":
        out_format = "md"
    if mode == "1D":
        create_1D_matrix(   dictionary = pvals, 
                            outname = outname, 
                            exclude_list = exclude_list, 
                            translationFile = translationFile,
                            out_format = out_format)

    elif mode == "2D":
        create_2D_matrix(dictionary = pvals, 
                            outname = outname, 
                            exclude_list = exclude_list,
                            out_format = out_format)

    if len(missing) != 0:
        print("Detected missing inputs!")
        for m in missing:
            print(m)

if __name__ == '__main__':
    options, wildcards = parse_arguments()

    main(*wildcards, **vars(options))
