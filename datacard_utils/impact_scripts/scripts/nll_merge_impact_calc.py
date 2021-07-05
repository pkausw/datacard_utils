import os, sys
import glob
import json
import ROOT
from math import fsum

if __name__ == '__main__':

    fit_type = sys.argv[1]
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
	
        year = ""
        for y in year_list:
            if y in comb:
                year = y
                break
        impact_year_dir = os.path.join(current_dir, ("../"+year))
        datacard = ""
        for json_path in glob.glob(os.path.join(impact_year_dir, "*.json")):
            if datacard is not "":
                continue
            with open(json_path) as f:
                dic = json.load(f)
            listOfDatacards = dic["datacards"]
            for card in listOfDatacards:
                if comb in card:
                    datacard = card
                    break
        datacard = datacard.split(".root")[0]+".txt"
        datacard_file = open(datacard)
        groups = {}
        for line in datacard_file.readlines():
            if "group" in line:
                groups[line.split(" group = ")[0]] = line.split(" group = ")[1].split()
        datacard_file.close()      
	       	   
        impact_comb_dir = os.path.join(impact_year_dir, comb)
        impact_json_file = os.path.join(impact_comb_dir, glob.glob(os.path.join(impact_comb_dir, "*.json"))[0])
        with open(impact_json_file) as f:
            dic = json.load(f)

        for param in params:
            print (param)
            param_dir = os.path.join(comb_dir, param)
            os.chdir(param_dir)
            os.system("rm -rf merged_combine_output.root nllscan_*")
            os.system("source "+os.path.join(param_dir, "merge_files.sh"))
                        
            param_entry = {}
            param_entry["fit"] = []
            param_entry["groups"] = []
            param_entry["impact_r"] = 0
            param_entry["name"] = param
            param_entry["r"] = []
            
            if "CMS_ttHbb_bgnorm_" in param:
                param_entry["prefit"] = [1.0, 1.0, 1.0]
                param_entry["type"] = "Unconstrained"
            else:
                param_entry["prefit"] = [-1.0, 0, 1.0]
                param_entry["type"] = "Gaussian"
            
            for g in groups:
                if param in groups[g]:
                    param_entry["groups"].append(g)
            
            nll_root_file = ROOT.TFile("merged_combine_output.root")
            nll_tree = nll_root_file.Get("limit")
            n_entries = nll_tree.GetEntries()
            param_list = []
            r_list = []
            nll_list = []
            param_best = []
            r_best = []
            for i,e in enumerate(nll_tree):
                param_value = eval("e."+param)
                r_value = eval("e.r")
                nll_value = 2*eval("e.deltaNLL")
                if nll_value == 0:
                    param_best.append(param_value)
                    r_best.append(r_value)
                    continue
                param_list.append(param_value)
                r_list.append(r_value)
                nll_list.append(nll_value)
            param_bestfit = fsum(param_best)/len(param_best)
            r_bestfit = fsum(r_best)/len(r_best)
            
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
            param_entry["r"].append(r_low)
            param_entry["r"].append(r_bestfit)
            param_entry["r"].append(r_high)
            if abs(r_low-r_bestfit) > abs(r_high-r_bestfit):
                param_entry["impact_r"] = abs(r_low-r_bestfit)
            else:
                param_entry["impact_r"] = abs(r_high-r_bestfit)
            
            dic["params"].append(param_entry)
            print ("")
            print (param_entry)
            print ("")
            json.dump(param_entry, log_file, indent=2)
            nll_root_file.Close()
            os.chdir(current_dir)
                                          
        for orig_file in glob.glob(os.path.join(impact_comb_dir, "*_orig*")):
            os.system("mv "+orig_file+" "+orig_file+"_orig")
        os.system("mv "+impact_json_file+" "+impact_json_file+"_orig")
        impact_json_file_new = open(impact_json_file, "w")
        json.dump(dic, impact_json_file_new, indent=2)
        impact_json_file_new.close()
        print ("JSON written: "+impact_json_file+"\n")
        
        missing_input_file = os.path.join(impact_comb_dir, "json_creation.log")
        missing_input_file_old = open(missing_input_file, "r")
        lines = missing_input_file_old.readlines() 
        line1 = lines[0]
        line2 = lines[1]
        missing_input_file_old.close()
        os.system("mv "+missing_input_file+" "+missing_input_file+"_orig")
        missing_input_file_new = open(missing_input_file, "w")
        missing_input_file_new.write(line1 + line2)
        missing_input_file_new.close()
        print ("Missing Inputs File written: "+missing_input_file+"\n")

        os.chdir(impact_comb_dir)
        if fit_type=="blind":
            os.system("plotImpacts.py -i " + impact_json_file.split("/")[-1] + " -o " + impact_json_file.split("/")[-1].split(".json")[0])
        elif fit_type=="unblind":
            os.system("plotImpacts.py -i " + impact_json_file.split("/")[-1] + " -o " + impact_json_file.split("/")[-1].split(".json")[0] + " --blind")
        os.chdir(current_dir)
    
    log_file.close()
           
         
 
            
            
            
