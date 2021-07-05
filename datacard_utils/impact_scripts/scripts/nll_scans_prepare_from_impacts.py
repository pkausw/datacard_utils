import os, sys
import glob
import json


if __name__ == '__main__':

    current_dir = os.path.abspath(os.getcwd())
    year = sys.argv[1]
    print ("Year: " + year)
    
    year_dir = os.path.join(current_dir, ("../"+year))
    
    for json_path in glob.glob(os.path.join(year_dir, "*.json")):
        with open(json_path) as f:
            dic = json.load(f)
        listOfDatacards = dic["datacards"]
        listOfImpactFolders = dic["impact_folders"]
        origSubmitCmds = dic["commands"]

        for d in listOfImpactFolders:
            print (d)
            file_sh = open(glob.glob(os.path.join(d, "*.sh"))[0])
            job_dic = {}
            n=0
            lines = file_sh.readlines()
            for n in range(0, len(lines)):
                if "-eq" in lines[n]:
                    n_j = lines[n].split()[4]
                    param_line = lines[n+1].split()
                    match=0
                    i=0
                    for p in param_line:
                        if p=="-P":
                            match = i
                            break
                        i+=1
                    param_j = param_line[match+1]
                    job_dic[n_j] = param_j 
            file_sh.close()
            
            comb = d.split("/")[-1]
            param_file = open("param_"+comb+".txt", "w+")
            n_param = 0
            for e in glob.glob(os.path.join(d, "*.err")):           
                if os.stat(e).st_size!=0:
                    job_n = e.split(".")[-2]
                    param = job_dic[job_n]
                    print ("NLL to be run for parameter: "+param)
                    param_file.write(param+"\n")
                    n_param+=1
            param_file.close()
            if n_param==0:
                os.system("rm -rf param_"+comb+".txt")
            datacard = ""
            for card in listOfDatacards:
                if comb in card:
                    datacard = card
                    break    
            cmd = "python ../../../scripts/doNllscanFromTxt.py "
            cmd += "param_"+comb+".txt "
            cmd += datacard + " "
            cmd += ' '.join(origSubmitCmds) + " "
            cmd += "--robustFit 1"
            print (cmd)
            os.system(cmd)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
       
