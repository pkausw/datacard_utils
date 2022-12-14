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

combinations = """
combined_SL_{}_DNN.root combined_SL_{}_DNN_ge4j_ge4t.root combined_SL_{}_DNN_ge4j_3t.root
""".split()

combinations = ["_fixed_ttH_{}_old_RO.root".format(i) for i in [0, 7, 8, 11]]
# combinations += ["fixed_ttH_{}.root".format(i) for i in [1, 3, 5, 7, 9, 18, 22]]
combinations += ["fixed_ttH_{}.root".format(i) for i in [3, 7, 9, 22]]
combinations += ["_double_glusplit"]
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
    # "CMS_btag_lf",
    # "CMS_ttHbb_scaleMuF_ttbbNLO",
    # "CMS_ttHbb_scaleMuR_ttbbNLO",
    # "CMS_btag_cferr2",
    # "CMS_eff_e_2018"
    # "CMS_ttHbb_bgnorm_ttbarPlusBBbar"
]

bestfit_path_template = "multidimfit{comb}.root"
# bestfit_path_template = "bestfits/fitDiagnostics_asimov_sig1_*r*{comb}.root"
outname_template = "{comb}__{param}.json"

def is_good_fit(result):
    if result.status() == 0 and result.covQual() == 3:
        return True
    print "WARNING: This is not a good fit!"
    print "\tStatus: {0}\tQuality: {1}".format(result.status(), result.covQual())
    return True #DANGERZONE!

def load_roofitresult(rfile, fitres = "fit_s"):
    result = rfile.Get(fitres)
    if not isinstance(result, ROOT.RooFitResult):
        result = rfile.Get("fit_mdf")
        if not isinstance(result, ROOT.RooFitResult):
            result = None
    if result and not is_good_fit(result):
        result = None
    
    return result

def is_good_rootfile(fpath):
    if os.path.exists(fpath):
        f = ROOT.TFile.Open(fpath)
        if (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
            return True
        else:
                print("File '{}' is broken, skipping".format(fpath)) 
    else:
        print("WARNING: file {} does not exist!".format(fpath))
    return False

def load_variable(result, parname):
    var = result.floatParsFinal().find(parname)
    if isinstance(var, ROOT.RooRealVar):
        return var

def load_bestfit(fpath, paramname):
    print("Loading from infile:")
    print(fpath)
    
    values = {}
    f = ROOT.TFile.Open(fpath)
    fit = load_roofitresult(rfile = f)
    if not fit is None:
        par = load_variable(result = fit, parname = paramname)
        if par is None:
            print(" ".join(
                """WARNING: Could not load parameter '{par}'
                from file {file}""".format(par=paramname, file = fpath).split()
                    )   
                    )
        else:
            values = {  "value" : par.getVal(), 
                        "down" : par.getErrorLo(), 
                        "up" : par.getErrorHi()
                    }

    else:
        print("Fit in file '{}' is broken, skipping".format(fpath))
    
    f.Close()
    
    return values

def dump_json(outname, allvals):
    if len(allvals) > 0:
        print "opening file", outname
        with open(outname, "w") as outfile:
            json.dump(allvals, outfile, indent = 4, separators = (',', ': '))
    else:
        print "given dictionary is empty, will not create '%s'" % outname


def create_jsons(combinations, files, outname_prefix):
    
    params = load_parameters(files)
    
    results = {}
    all_results = {}
    all_results["allParams"] = params
    for comb in combinations:
    
        results_ = {}
        key_bestfit = bestfit_path_template.format(comb = comb)
        files_bestfit = filter(files, "*{}*".format(key_bestfit))
        
        if not len(files_bestfit) == 1:
            raise ValueError("Found no clear match for combination '{}'".format(comb))
        bestfit_file = files_bestfit[0]
        for p in params:
            
            tmp = load_bestfit(bestfit_file, p)
            if len(tmp) != 0:
                results_[p] = tmp 
        if not len(results_) == 0:
            results[comb] = results_
    pprint(results)
    all_results["r"] = results
    dump_json(outname = "{}_ParamEvolution.json".format(outname_prefix), allvals = all_results)

def load_parameters(files):
    params = []
    for f in files:
        try:
            rfile = ROOT.TFile.Open(f)
            f = load_roofitresult(rfile)
            params = list(set(params + f.floatParsFinal().contentsString().split(",")))
            rfile.Close()
        except:
            print("Could not load parameters from file '{}'".format(f))
    params = [p for p in params if not p.startswith("prop_bin")]
    return params

def collect_results(*infiles, **kwargs):
    #load options
    parameters = kwargs.get("parameters")
    key_bestfit = kwargs.get("key_bestfit")
    outname = kwargs.get("outname")
    # files = kwargs.get("files")
    # exit()
    #initialize dictionary for results
    results = {}
    for p in params:
        print("="*130)
        print("Collecting results for param {}".format(p))
        print("="*130)
        
        #load bestfits
        # infiles = filter_files(infiles = files, exclude_crits = others, must_include= [p])
        print("="*130)
        print("Collecting bestfits")
        print("="*130)
        load_bestfit(files = files_bestfit, paramname = p, results = results[p], keyword = "bestfit")
    # dump_json(outname = outname, allvals = results)
    return results


def main(prefix = sys.argv[1], files = sys.argv[2:]):
    global bestfit_path_template
    # filter out bad root files
    files = [f for f in files if is_good_rootfile(f)]
    create_jsons(combinations = combinations,
                    files = files,
                    outname_prefix = prefix
                 )
    
    

if __name__ == '__main__':
    main()
    