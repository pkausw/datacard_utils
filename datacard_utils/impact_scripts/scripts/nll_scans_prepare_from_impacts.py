import os, sys
import glob
import json

this_dir = os.path.realpath(os.path.dirname(__file__))

def load_parameters(indir, job_dic, logfile = "json_creation.log"):
    params = []
    lines = []
    log_path = os.path.join(indir, logfile)
    if not os.path.exists(log_path):
        for e in glob.glob(os.path.join(indir, "*.err")):           
            if os.stat(e).st_size!=0:
                job_n = e.split(".")[-2]
                param = job_dic[job_n]
                params.append(param)
    else:
        with open(log_path) as f:
            lines = f.read().splitlines()
        
        for l in lines:
            l = l.strip()
            if l.startswith("Missing"):
                words = l.split()
                params = words[-1].split(",")
    for param in params:
        print ("NLL to be run for parameter: "+param)
    return params

if __name__ == '__main__':

    current_dir = os.path.abspath(os.getcwd())
    json_files = sys.argv[1:]
    # print ("Year: " + year)
    
    # year_dir = os.path.join(current_dir, ("../"+year))
    
    for json_path in json_files:
        if not os.path.exists(json_path):
            print("path '{}' does not exist".format(json_path))
            continue
        with open(json_path) as f:
            dic = json.load(f)
        listOfDatacards = dic["datacards"]
        listOfImpactFolders = dic["impact_folders"]
        origSubmitCmds = dic["commands"]

        for d in listOfImpactFolders:
            print (d)
            sh_files = glob.glob(os.path.join(d, "*.sh"))
            if len(sh_files) == 0:
                print("could not load any .sh files for '{}', skipping".format(d))
                continue
            elif len(sh_files) != 1:
                msg = "found multiple .sh files for '{}', please check manually!"
                raise ValueError(msg)
                
            with open(sh_files[0]) as file_sh:
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
            
            par_list = load_parameters(indir = d, job_dic = job_dic)

            if len(par_list) > 0:
                comb = d.split("/")[-1]
                param_file = "param_"+comb+".txt"

                with open(param_file, "w") as f:
                    f.write("\n".join(par_list))
                
                datacard = None
                for card in listOfDatacards:
                    if any("{}.{}".format(comb, ext) in card 
                            for ext in "txt root"):
                        datacard = card
                        break  
                if not datacard:
                    raise ValueError("Could not find datacard for combination '{}'".format(comb))  
                cmd = "python {}/doNllscanFromTxt.py ".format(this_dir)
                cmd += "{} ".format(param_file)
                cmd += datacard + " "
                cmd += ' '.join(origSubmitCmds) + " "
                cmd += "--robustFit 1"
                print (cmd)
                os.system(cmd)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
       
