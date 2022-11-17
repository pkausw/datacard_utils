import os, sys
import glob
import json
import ROOT
from math import fsum

def loadPOIs(workspace):
    """
    Loads the list of POIs from the input 'workspace'
    """
    print("loading POIs from workspace in " + workspace)
    infile = ROOT.TFile(workspace)
    w = infile.Get("w")
    if isinstance(w, ROOT.RooWorkspace):
        mc = w.obj("ModelConfig")
        if isinstance(mc, ROOT.RooStats.ModelConfig):
            return mc.GetParametersOfInterest().contentsString().split(",")

def load_groups(datacard, group_delimiter = " group = "):
    datacard = datacard.split(".root")[0]+".txt"
    groups = {}
    if os.path.exists(datacard):
        with open(datacard) as datacard_file:
            for line in datacard_file.readlines():
                if group_delimiter in line:
                    print(line)
                    line_parts = line.split(group_delimiter)
                    groups[line_parts[0]] = line_parts[1].split()
    else:
        print("Could not load '{}', will not add groups".format(datacard))

    return groups

def create_param_entry(nll_tree, param, poi):
    param_entry = {}
    param_entry["fit"] = []
    param_entry[poi] = []
    param_list = []
    r_list = []
    nll_list = []
    param_best = []
    r_best = []
    for i,e in enumerate(nll_tree):
        param_value = eval("e."+param)
        r_value = eval("e."+poi)
        nll_value = 2*eval("e.deltaNLL")
        if nll_value == 0:
            param_best.append(param_value)
            r_best.append(r_value)
            continue
        param_list.append(param_value)
        r_list.append(r_value)
        nll_list.append(nll_value)
    if len(param_best) > 0 and len(r_best) > 0:
        param_bestfit = fsum(param_best)/len(param_best)
        r_bestfit = fsum(r_best)/len(r_best)
    else:
        print("Unable to find best fit value with NLL == 0, looking for minimal NLL value")
        nll_min_idx = nll_list.index(min(nll_list))
        param_bestfit = param_list[nll_min_idx]
        r_bestfit = r_list[nll_min_idx]
        print("\t NLL min value: {}".format(nll_list[nll_min_idx]))
        print("\t best fit parameter values: {}".format(param_bestfit))
    
    param_low_err = 9999
    param_high_err = 9999
    i_low = 0
    i_high = 0
    for i in range(0, len(param_list)):
        if param_list[i] < param_bestfit:    
            if abs(nll_list[i]-1.0) < param_low_err:
                i_low = i
                param_low_err = abs(nll_list[i]-1.0)
        else:
            if abs(nll_list[i]-1.0) < param_high_err:
                i_high = i
                param_high_err = abs(nll_list[i]-1.0)
    param_low = param_list[i_low]
    param_high = param_list[i_high]
    r_low = r_list[i_low]
    r_high = r_list[i_high]           
    param_entry["fit"].append(param_low)
    param_entry["fit"].append(param_bestfit)
    param_entry["fit"].append(param_high)
    param_entry[poi].append(r_low)
    param_entry[poi].append(r_bestfit)
    param_entry[poi].append(r_high)
    diffs = [abs(r_low-r_bestfit), abs(r_high-r_bestfit)]
    param_entry["impact_{}".format(poi)] = max(diffs)
    return param_entry
    
def calculate_missing_impacts(datacard, impact_comb_dir, params, log_file, impact_json_file, pois = ["r"]):
    groups = load_groups(datacard)      
	       	   
    # impact_comb_dir = os.path.join(impact_year_dir, comb)
    
    with open(impact_json_file) as f:
        dic = json.load(f)


    # first filter the param from the dictionary
    orig_params = dic["params"]
    clean_params = [x for x in orig_params if not any(x.get("name") == param for param in params)]
    
    dic["params"] = clean_params

    #load POIs from input workspace
    
    for param in params:
        if param in pois: continue
        print (param)
        param_dir = os.path.join(comb_dir, param)
        os.chdir(param_dir)

        # os.system("rm -rf merged_combine_output.root nllscan_*")
        # os.system("source "+os.path.join(param_dir, "merge_files.sh"))
                    
        param_entry = {}
        param_entry["groups"] = []
        param_entry["name"] = param
        
        if "CMS_ttHbb_bgnorm_" in param:
            param_entry["prefit"] = [1.0, 1.0, 1.0]
            param_entry["type"] = "Unconstrained"
        else:
            param_entry["prefit"] = [-1.0, 0, 1.0]
            param_entry["type"] = "Gaussian"
        
        for g in groups:
            if param in groups[g]:
                param_entry["groups"].append(g)
        
        if not os.path.exists("merged_combine_output.root"):
            print("generating merged root file")
            print("current dir: {}".format(os.getcwd()))
            if os.path.exists("merge_files.sh"):
                cmd = "source "+os.path.join(param_dir, "merge_files.sh")
                # cmd = "source merge_files.sh"
                print(cmd)
                os.system(cmd)
            else:
                fit_parts = glob.glob("fit_parts/*.root")
                if len(fit_parts) > 0:
                    cmd = "hadd -f merged_combine_output.root " + " ".join(fit_parts)
                    print(cmd)
                    os.system(cmd)
                else:
                    print("unable to find parts for NLL scan!")
        # check again if merged combine output file exists.
        # If not, something went wrong and we will skip this datacard
        if not os.path.exists("merged_combine_output.root"):
            os.chdir(current_dir)
            return None
        nll_root_file = ROOT.TFile("merged_combine_output.root")
        nll_tree = nll_root_file.Get("limit")
        
        for poi in pois:
            param_entry.update(create_param_entry(nll_tree = nll_tree,
                                                  param = param,
                                                  poi = poi  )
                                )
        
        dic["params"].append(param_entry)

        # print ("")
        # print (json.dumps(param_entry, indent=2))
        # print ("")
        # sys.exit("DEBUG OUT")
        json.dump(param_entry, log_file, indent=2)
        nll_root_file.Close()
        os.chdir(current_dir)
    return dic

if __name__ == '__main__':

    fit_type = sys.argv[1]
    submit_json = sys.argv[2:]
    current_dir = os.path.abspath(os.getcwd())
    log_file = open(os.path.join(current_dir, "output_log.json"), "w")
    combinations = []
    for d in os.listdir(current_dir):
        if os.path.isdir(os.path.join(current_dir, d)):
            combinations.append(d)

    #year_list = ["2016", "2017", "2018", "all_years"]
    year_list = ["2016", "2017", "2018", "all_years", "1617", "1718"]

    for comb in combinations:
        print (comb)
        comb_dir = os.path.join(current_dir, comb)
        params = []
        for d in os.listdir(comb_dir):
            if os.path.isdir(os.path.join(comb_dir, d)):
                params.append(d)
	
        # year = ""
        # for y in year_list:
        #     if y in comb:
        #         year = y
        #         break
        # impact_year_dir = os.path.join(current_dir, ("../"+year))
        datacard = ""
        # for json_path in glob.glob(os.path.join(impact_year_dir, "*.json")):
        impact_comb_dir = None
        for json_path in submit_json:
            if datacard is not "":
                continue
            with open(json_path) as f:
                dic = json.load(f)
            listOfDatacards = dic["datacards"]
            listOfImpactFolders = dic["impact_folders"]
            for i, card in enumerate(listOfDatacards):
                if any("{}.{}".format(comb, ext) in card 
                            for ext in "txt root"):
                    datacard = card
                    impact_comb_dir = listOfImpactFolders[i]
                    break
        if not impact_comb_dir:
            print("="*130)
            print("Error for comb '{}': could not find entry in list of impact folders".format(comb))
            print("list of impact folders:")
            print(listOfImpactFolders)
            continue
        json_files = glob.glob(os.path.join(impact_comb_dir, "*.json"))
        if len(json_files) == 0:
            print("could not load json file for combination '{}'".format(impact_comb_dir))
            continue
        elif len(json_files) > 1:
            print("found multiple json files for combination '{}', skipping".format(impact_comb_dir))
            continue
        impact_json_file = os.path.join(impact_comb_dir, json_files[0])
        pois = loadPOIs(datacard)

        dic = calculate_missing_impacts(datacard = datacard, 
                                            impact_comb_dir = impact_comb_dir,
                                            log_file = log_file,
                                            params = params,
                                            impact_json_file = impact_json_file,
                                            pois = pois)
        
        if not dic:
            msg = ["="*130]
            msg.append(("could not calculate all impacts for combination '{}'"
                        .format(comb)))
            msg.append("="*130)
            raise ValueError("\n".join(msg))

                                          
        for orig_file in glob.glob(os.path.join(impact_comb_dir, "*_orig*")):
            os.system("mv "+orig_file+" "+orig_file+"_orig")
        os.system("mv "+impact_json_file+" "+impact_json_file+"_orig")
        impact_json_file_new = open(impact_json_file, "w")
        json.dump(dic, impact_json_file_new, indent=2)
        impact_json_file_new.close()
        print ("JSON written: "+impact_json_file+"\n")
        
        missing_input_file = os.path.join(impact_comb_dir, "json_creation.log")
        with open(missing_input_file, "r") as missing_input_file_old:
            lines = missing_input_file_old.readlines() 
            line1 = lines[0]
            line2 = lines[1]
        # missing_input_file_old.close()
        os.system("mv "+missing_input_file+" "+missing_input_file+"_orig")
        with open(missing_input_file, "w") as missing_input_file_new:
            missing_input_file_new.write(line1 + line2)
        # missing_input_file_new.close()
        print ("Missing Inputs File written: "+missing_input_file+"\n")

        os.chdir(impact_comb_dir)
        impact_file = os.path.basename(impact_json_file)
        impact_name = ".".join(impact_file.split(".")[:-1])
        for poi in pois:
            
            cmd = "plotImpacts.py -i {infile} -o {name}_{poi} --POI {poi}".format(infile = impact_file, name = impact_name, poi = poi)
            if fit_type=="blind":
                cmd += " --blind"
            
            os.system(cmd)
        os.chdir(current_dir)
    
    log_file.close()
           
         
 
            
            
            
