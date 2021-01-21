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
#     print c
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

def load_json(path):
    return_dict = {}
    with open(path) as f:
        return_dict = json.load(f)
    return return_dict.get("params", {})

def dump_json(outname, allvals):
    if len(allvals) > 0:
        print "opening file", outname
        with open(outname, "w") as outfile:
            json.dump(allvals, outfile, indent = 4, separators = (',', ': '))
    else:
        print "given dictionary is empty, will not create '%s'" % outname

def loadParams(inFile):
    paramDict = load_json(inFile)
    # pprint(paramDict)
    result = {}
    allParams = []
    for param in paramDict:
        result[param["name"]] = {
            "bestfit" : {
                "value": param["fit"][1],
                "up": param["fit"][2]-param["fit"][1],
                "down": param["fit"][0]-param["fit"][1]
            }
        }
        allParams.append(param["name"])

    return result, allParams
    # pprint(result)
    # exit()



def main(indir = sys.argv[1], outname = sys.argv[2]):
    # global bestfit_path_template
    # if os.path.exists(indir) and os.path.isdir(indir):
    #     bestfit_path_template = os.path.join(indir, bestfit_path_template)
    # else:
    #     raise ValueError("Directory {} does not exist!".format(indir))
    results = {}
    for comb in combinations:
        print("#"*10)
        print(comb)
        inFiles = glob.glob(indir+"/"+comb+"/*.json")
        if len(inFiles) != 1:
            print("WARNING found more than one or zero json files: {}".format(inFiles))
        else:
            inFile = inFiles[0]
            # print(inFile)
            results_, allParams = loadParams(inFile)
            results[comb] = results_
    dump = {
        "r" : results,
        "allParams" : allParams    
            }
    dump_json(outname = outname+"_ParamEvolution.json", allvals = dump)
    
    

if __name__ == '__main__':
    main()
    