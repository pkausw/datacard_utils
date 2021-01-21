import os
import sys
import ROOT
import json
import glob

from fnmatch import filter
from optparse import OptionParser
from pprint import pprint

thisdir = os.path.realpath(os.path.dirname(__file__))
thisdir = os.path.abspath(thisdir)

# DANGERZONE
#scriptdir = os.path.join(thisdir,"..", "utilities")
scriptdir = thisdir

# options
key_bestfit = "bestfit"
key_statonly = "stat_only"
key_signi = "significance"
do_bestfits = True
do_statonly = True
multisignal = True


combinations = """
combined_DLFHSL_{}_baseline_v01.root  combined_FH_{}_DNN.root          combined_SL_{}_DNN_ge4j_ge4t.root
combined_DLSL_{}_baseline_v01.root    combined_SL_{}_DNN.root          combined_full_{}_baseline_v01.root
combined_DL_{}_DNN.root               combined_SL_{}_DNN_ge4j_3t.root
""".split()

#combinations = """
#combined_SL_{}_DNN.root combined_SL_{}_DNN_ge4j_ge4t.root combined_SL_{}_DNN_ge4j_3t.root
#""".split()
#combinations = """
#combined_full_{}_baseline_v01_packaged_mus_channels.root
#""".split()

#combinations = """
#rate_5FS_to_4FS_combined_full_2017_baseline_v01.root
#hybrid_5FS_to_4FS_combined_full_2017_baseline_v01_withMCCR.root
#""".split()

#combinations = "combined_SL_2017_DNN.root".split()
#combinations = ["combined_full_{}_baseline_v01.root"]
years = "2016 2017 2018 all_years".split()
#years = ["2017"]
#combinations += ["No_minor_"+x for x in combinations]
#combinations += ["ttbb_CR_{}.root"]
combinations = [x.format(y) for x in combinations for y in years]
# combinations += """
# combined_full_all_years_baseline_v01_packaged_mus.root
# combined_full_all_years_baseline_v01_packaged_mus_per_year.root
# combined_full_all_years_baseline_v01_packaged_mus_per_year_per_channel.root""".split()
combinations = [x.replace(".root", "") for x in combinations]

# combinations = """
#     combined_SL_2018_DNN
#     combined_SL_2017_DNN
# """.replace(".root","").split()
# for c in sorted(combinations):
    # print c
# print(combinations)
# exit()
# list of POIs in case of multisignal model (each POI has its own fitDiagnostics file)
POIs = [
    "r"
]

params = [
    # "r",
    # "r_ttH_PTH_0_60",
    # "r_ttH_PTH_60_120",
    # "r_ttH_PTH_120_200",
    # "r_ttH_PTH_200_300",
    # "r_ttH_PTH_GT300",
    #"r_SL",
    #"r_DL",
    #"r_FH",
    #"r_ttbbCR",
    "CMS_ttHbb_bgnorm_ttbb",
    "CMS_ttHbb_bgnorm_ttcc",
    "CMS_btag_lf",
    "CMS_ttHbb_scaleMuF_ttbbNLO",
    "CMS_ttHbb_scaleMuR_ttbbNLO",
    "CMS_btag_cferr2",
    "CMS_eff_e_2018"
    # "CMS_ttHbb_bgnorm_ttbarPlusBBbar"
]

bestfit_path_template = "bestfits/fitDiagnostics_asimov_sig1*{param}_{comb}.root"
# bestfit_path_template = "bestfits/fitDiagnostics_asimov_sig1_*r*{comb}.root"
outname_template = "{comb}__{param}.json"

def is_good_fit(result):
    if result.status() == 0 and result.covQual() == 3:
        return True
    print "WARNING: This is not a good fit!"
    print "\tStatus: {0}\tQuality: {1}".format(result.status(), result.covQual())
    return False #DANGERZONE!

def load_roofitresult(rfile, fitres = "fit_s"):
    result = rfile.Get(fitres)
    if not isinstance(result, ROOT.RooFitResult):
        result = rfile.Get("fit_mdf")
        if not isinstance(result, ROOT.RooFitResult):
            result = None
    if result and not is_good_fit(result):
        result = None
    
    return result

def load_variable(result, parname):
    var = result.floatParsFinal().find(parname)
    if isinstance(var, ROOT.RooRealVar):
        return var

def load_bestfit(files, paramname, results, keyword):
    print("Loading from files:")
    print(files)
    for fpath in files:
        # if not paramname in fpath:
        #     print("WARNING: Could not find '{param}' in path name '{fpath}'! Skipping".format(
        #         param = paramname,
        #         fpath = fpath
        #     ))
        #     continue
        if not os.path.exists(fpath):
            print("WARNING: file {} does not exist!".format(fpath))
            continue
        f = ROOT.TFile.Open(fpath)
        if not (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
            print("File '{}' is broken, skipping".format(fpath))
            continue
        fit = load_roofitresult(rfile = f)
        if fit is None:
            print("Fit in file '{}' is broken, skipping".format(fpath))
            continue
        par = load_variable(result = fit, parname = paramname)
        if par is None:
            print(" ".join(
                """WARNING: Could not load parameter '{par}'
                from file {file}""".format(par=paramname, file = fpath).split()
                    )   
                  )
            continue
        if keyword in results:
            print("WARNING: keyword '{}' is already in results dict!".format(keyword))
            keyword += "_new"
        results[keyword] = {"value" : par.getVal(), "down" : par.getErrorLo(), "up" : par.getErrorHi()}

def dump_json(outname, allvals):
    if len(allvals) > 0:
        print "opening file", outname
        with open(outname, "w") as outfile:
            json.dump(allvals, outfile, indent = 4, separators = (',', ': '))
    else:
        print "given dictionary is empty, will not create '%s'" % outname

def prepare_files(infiles):
    return_dict = {}
    for f in infiles:
        tmp = os.path.basename(f)
        #remove root extension
        tmp = tmp.split(".")[0]
        if tmp.endswith("2D"):
            tmp = "_".join(tmp.split("_")[:-4])
        return_dict[f] = tmp
    return return_dict

def filter_files(infiles, exclude_crits, must_include = []):
    print("FILTER_FILES: input")
    print(infiles)
    tmp = prepare_files(infiles)
    l = [f for f in tmp if not any(c in tmp[f] for c in exclude_crits)]
    l = [f for f in l if all(c in tmp[f] for c in must_include)]
    print("FILTER_FILES: output")
    print(l)
    return l

def create_jsons(combinations, params):
    results = {}
    for p in POIs:
        results_ = {}
        for comb in combinations:
            files = []
            outname = outname_template.format(
                comb = comb,
                param = p
            )
            if multisignal:
                files.append(bestfit_path_template.format(
                    param = p,
                    comb = comb,
                ))
            else:
                files.append(bestfit_path_template.format(
                    param = "",
                    comb = comb,
                ))
            # print("-----------")
            # for f in files:
            #     print(f)     
            results_[comb] = collect_results(
                    parameters = params,
                    do_bestfits = do_bestfits,
                    do_statonly = do_statonly,
                    key_bestfit = key_bestfit,
                    key_statonly = key_statonly,
                    key_signi = key_signi,
                    outname = outname,
                    files=files
                )
        results[p] = results_
    pprint(results)
    dump_json(outname = "ParamEvolution.json", allvals = results)


def collect_results(**kwargs):
    #load options
    parameters = kwargs.get("parameters")
    do_bestfits = kwargs.get("do_bestfits")
    do_statonly = kwargs.get("do_statonly")
    key_bestfit = kwargs.get("key_bestfit")
    key_statonly = kwargs.get("key_statonly")
    key_signi = kwargs.get("key_signi")
    outname = kwargs.get("outname")
    files_ = kwargs.get("files")

    files = []
    for f in files_:
        files+=glob.glob(f)
    print(files)
    # exit()
    #initialize dictionary for results
    results = {}
    for p in parameters:
        print("="*130)
        print("Collecting results for param {}".format(p))
        print("="*130)
        if not p in results:
            results[p] = {}
        others = [par for par in parameters if not par == p]
        if "r" in others:
            others.pop(others.index("r"))
        #load bestfits
        # infiles = filter_files(infiles = files, exclude_crits = others, must_include= [p])
        infiles = filter_files(infiles = files, exclude_crits = others)
        if do_bestfits:
            print("="*130)
            print("Collecting bestfits")
            print("="*130)
            files_bestfit = filter(infiles, "*{}*".format(key_bestfit))
            files_bestfit = filter_files(infiles = files_bestfit, exclude_crits = [key_statonly, key_signi])
            load_bestfit(files = files_bestfit, paramname = p, results = results[p], keyword = "bestfit")
        if do_statonly:
            print("="*130)
            print("Collecting stat-only")
            print("="*130)
            files_statonly = filter(infiles, "*{}*".format(key_statonly))
            files_statonly = filter_files(infiles = files_statonly, exclude_crits = [key_bestfit, key_signi])
            load_bestfit(files = files_statonly, paramname = p, results = results[p], keyword = "stat_only")
    dump_json(outname = outname, allvals = results)
    return results


def main(indir = sys.argv[1]):
    global bestfit_path_template
    if os.path.exists(indir) and os.path.isdir(indir):
        bestfit_path_template = os.path.join(indir, bestfit_path_template)
    else:
        raise ValueError("Directory {} does not exist!".format(indir))
    create_jsons(combinations = combinations,
                 params = params
                 )
    
    

if __name__ == '__main__':
    main()
    