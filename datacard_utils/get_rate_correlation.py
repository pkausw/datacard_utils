from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import ROOT
import json
cmssw_base = os.environ["CMSSW_BASE"]
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetPaintTextFormat("2.1f")

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

def parse_arguments():

    parser = OptionParser()

    parser.add_option("-o", "--outpath",
                    help = " ".join(
                        """
                        save rate correlation plots here. Default: here
                        """.split()
                    ),
                    dest = "outpath",
                    type="str",
                    default="."
    )
    parser.add_option("-d", "--data",
                    help = " ".join(
                        """
                        name of the observed data set. Default: data_obs
                        """.split()
                    ),
                    dest = "data",
                    type="str",
                    default="data_obs"
    )
    parser.add_option("-f", "--fit_result",
                    help = " ".join(
                        """
                        use this RooFitResult object to sample the nuisance 
                        parameters
                        """.split()
                    ),
                    dest = "fitresult",
                    type="str",
    )
    parser.add_option("-n", "--nsamples",
                    help = " ".join(
                        """
                        use this amount of toys to evaluate the rate 
                        covariance matrix. Default: 300
                        """.split()
                    ),
                    dest = "nsamples",
                    type="int",
                    default=300,
    )
    parser.add_option("-s", "--shift",
                    help = " ".join(
                        """
                        evaluate rate evolution for this shift. 
                        Choices: [up (u), down(d), nominal(n)].
                        Default: nominal
                        """.split()
                    ),
                    dest = "shift",
                    choices = ["up", "down", "nominal", "u", "d", "n"],
                    default="nominal"
    )
    parser.add_option("-e", "--extentions",
                    help = " ".join(
                        """
                        save in these formats. Default:
                        [png, pdf, root]
                        """.split()
                    ),
                    dest = "extensions",
                    action = "append",
                    default = []
    )
    parser.add_option("-p", "--process",
                    help = " ".join(
                        """
                        Do the evolution of the rates for these processes.
                        Can be called multiple times.
                        regex is allowed
                        """.split()
                    ),
                    dest = "process_list",
                    action = "append",
                    default = []
    )
    parser.add_option("-u", "--uncertainties",
                    help = " ".join(
                        """
                        Do the evolution of the rates for these uncertainties.
                        Can be called multiple times.
                        regex is allowed
                        """.split()
                    ),
                    dest = "uncertainty_list",
                    action = "append",
                    default = []
    )
    parser.add_option("--do-correlations",
                    help = " ".join(
                        """
                        create the correlation matrix of rates.
                        Default: False
                        """.split()
                    ),
                    dest = "do_correlations",
                    action = "store_true",
                    default= False
    )


    options, files = parser.parse_args()

    exts = options.extensions
    if not isinstance(exts, list) or len(exts) == 0:
        options.extensions = "root png pdf".split()

    procs = options.process_list
    if not isinstance(procs, list) or len(procs) == 0:
        options.process_list = [".*"]
    uncertainties = options.uncertainty_list
    if not isinstance(uncertainties, list) or len(uncertainties) == 0:
        options.uncertainty_list = [".*"]

    # convert short cuts for shifts into real names
    shift = options.shift
    if shift == "u":
        options.shift = "up"
    elif shift == "d":
        options.shift = "down"
    elif shift == "n":
        options.shift = "nominal"

    return options, files

def get_rate_evolution(harvester, fit, shift = "nominal"):
    parameters = fit.floatParsFinal().contentsString().split(",")
    rate = harvester.GetRate()
    rate_dict = harvester.RateEvolution(fit, shift)
    return rate_dict
        


def load_fitresult(fitpath):
    filepath, obj_name = fitpath.split(":")
    if not os.path.exists(filepath):
        raise ValueError("File '{}' does not exist!".format(filepath))
    rfile = ROOT.TFile.Open(filepath)
    fit = rfile.Get(obj_name)
    # fit.SetDirectory(0)
    return fit

def draw_2D_map(value_dict, processes, parameters, outname, extensions):
    processes = sorted(processes)
    parameters = sorted(parameters)
    nprocs = len(processes)
    nparams = len(parameters)
    c = ROOT.TCanvas("rate_pull", "rate_pull", 2200, 3600)
    c.SetRightMargin(0.2)
    c.SetLeftMargin(0.35)
    corrmat = ROOT.TH2D("rate_diffs", "", nprocs, 0, nprocs, nparams, 0, nparams)
    corrmat.SetStats(False)
    zaxis = corrmat.GetZaxis()
    zaxis.SetTitleOffset(1.7)
    zaxis.SetRangeUser(-100,100)
    zaxis.SetTitle("#frac{rate_{postfit} - rate_{prefit}}{rate_{prefit}} in %")
    for x, proc in enumerate(processes, 1):
        corrmat.GetXaxis().SetBinLabel(x, proc)
        proc_dict = value_dict[proc]
        prefit = proc_dict["prefit"]
        for y, param in enumerate(parameters, 1):
            if x == 1:
                corrmat.GetYaxis().SetBinLabel(y, param)
            if param == "prefit": continue
            postfit = proc_dict.get(param, prefit)
            rate_diff = (postfit - prefit)/prefit * 100 if not prefit == 0 else 0
            corrmat.SetBinContent(x, y, rate_diff)
    corrmat.Draw("coltzTEXT")
    for e in extensions:
        c.SaveAs(".".join([outname, e]), e)

def create_2D_map(value_dict, outname, extensions):
    processes = list(set(value_dict.keys()))
    parameters = list(set(value_dict.values()[0]))
    parameters.pop(parameters.index("prefit")) # substract prefit
    # split parameters into autoMCStats and others
    standard_params = [x for x in parameters if not "prop_bin" in x]
    autoMCStats = [x for x in parameters if "prop_bin" in x]
    draw_2D_map(value_dict=value_dict, 
                processes=processes, 
                parameters = standard_params, 
                outname=outname, 
                extensions=extensions)
    draw_2D_map(value_dict=value_dict, 
                processes=processes, 
                parameters = autoMCStats, 
                outname=outname+"_autoMCStats", 
                extensions=extensions)


def rate_evolution_per_process(harvester, process_list, fit, outpath, extensions, shift = "nominal"):
    bins = harvester.bin_set()
    for b in bins:
        bin_dict = {}
        for procs in process_list:
            proc_harvester = harvester.cp().bin([b]).process([procs])
            if len(proc_harvester.process_set()) == 0:
                print("Could not load processes '{}' for bin '{}'".format(procs, b))
                continue
            bin_dict[procs] = get_rate_evolution(proc_harvester, fit, shift = shift)
            print(json.dumps(bin_dict[procs], indent=4, sort_keys= lambda x: x[1]))
        
        outname = "rate_pull_{}_{}".format(b, shift)
        outname = os.path.join(outpath, outname)
        create_2D_map(value_dict = bin_dict, 
                        outname = outname, 
                        extensions = extensions)
        
def create_correlation_plots(harvester, 
                            fit, 
                            nsamples, 
                            workspace, 
                            outpath,
                            exts
):
    c = ROOT.TCanvas()

    cormat = harvester.GetRateCorrelation(fit, nsamples)

    cormat.Draw("coltzTEXT")
    
    outname = os.path.basename(workspace)
    outname = ".".join(outname.split(".")[:-1])
    outname = "cormat_{}".format(outname)
    outname = os.path.join(outpath, outname)
    for e in exts:
        c.SaveAs("{}.{}".format(outname, e), e)

def main(*files, **kwargs):
    fitresult = kwargs.get("fitresult")
    nsamples = kwargs.get("nsamples", 300)
    data = kwargs.get("data", "data_obs")
    outpath = kwargs.get("outpath", ".")
    exts = kwargs.get("extensions", "root pdf png".split())
    process_list = kwargs.get("process_list", [".*"])
    do_correlations = kwargs.get("do_correlations", False)
    shift = kwargs.get("shift", "nominal")
    uncertainties = kwargs.get("uncertainty_list", [".*"])
    # check if outpath exists
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    # load RooFitResult object
    fit = load_fitresult(fitresult)
    for workspace in files:
        if not os.path.exists(workspace):
            print("File {} does not exist, skipping".format(workspace))
            continue
        
        f = ROOT.TFile.Open(workspace)
        ws = f.Get("w")
        cmb = ch.CombineHarvester()
        cmb.SetFlag("workspaces-use-clone", True)
        cmb.SetFlag("filters-use-regex", True)
        ch.ParseCombineWorkspace(cmb, ws, "ModelConfig", data, False)

        rate_evolution_func = getattr(cmb, "RateEvolution", None)
        if callable(rate_evolution_func):
            this_cmb = cmb.cp().syst_name(uncertainties)
            rate_evolution_per_process(harvester=this_cmb,
                                    process_list=process_list,
                                    fit=fit,
                                    outpath=outpath, 
                                    extensions=exts,
                                    shift = shift
                                    )
        else:
            msg = " ".join("""
            Instance of CombineHarvester does not have callable instance
            with name 'RateEvolution'. This probably means that the hack
            needed for this is not in you Harvester installation.
            Cannot create rate evolutions.
            """.split())
            print(msg)
        
        if do_correlations:
            create_correlation_plots(harvester=cmb,
                                        fit = fit,
                                        nsamples=nsamples,
                                        workspace=workspace,
                                        outpath=outpath, 
                                        exts=exts
                                    )


if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))