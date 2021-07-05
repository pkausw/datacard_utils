import os, sys
import glob

if __name__ == '__main__':

    current_dir = os.path.abspath(os.getcwd())
    combinations = []
    for d in os.listdir(current_dir):
        if os.path.isdir(os.path.join(current_dir, d)):
            combinations.append(d)

    for comb in combinations:
        print (comb)
        comb_dir = os.path.join(current_dir, comb)
        params = []
        for d in os.listdir(comb_dir):
            if os.path.isdir(os.path.join(comb_dir, d)):
                params.append(d)
	
        for param in params:
            print (param)
            param_dir = os.path.join(comb_dir, param)
            param_fit_dir = os.path.join(param_dir, "fit_parts")
			
            condor_sh_file_path = os.path.join(param_fit_dir, "condor_jobs.sh")
            condor_sub_file_path = os.path.join(param_fit_dir, "condor_jobs.sub")
            condor_sh_file = open(condor_sh_file_path, "w+")
            condor_sub_file = open(condor_sub_file_path, "w+")
            log_path = os.path.join(param_fit_dir, "logs")
            if os.path.isdir(os.path.join(param_fit_dir, "logs")):
                os.system("rm -rf "+os.path.join(param_fit_dir, "logs"))
            os.system("mkdir "+log_path)
            os.system("rm -rf "+os.path.join(param_fit_dir, "*.root"))
            
            condor_sh_file.write("#!/bin/sh \n")
            condor_sh_file.write("ulimit -s unlimited \n")
            condor_sh_file.write("cd "+param_fit_dir+"\n\n")
      
            condor_sub_file.write("executable = condor_jobs.sh \n")
            condor_sub_file.write("arguments = $(ProcId) \n")
            condor_sub_file.write("output = logs/do_fits.$(ClusterId).$(ProcId).out \n")
            condor_sub_file.write("error = logs/do_fits.$(ClusterId).$(ProcId).err \n")
            condor_sub_file.write("log = logs/do_fits.$(ClusterId).$(ProcId).log \n")
            condor_sub_file.write("+MaxRuntime = 7200 \n\n")
       
            n=0
            for f in os.listdir(param_fit_dir):
                if not os.path.isfile(os.path.join(param_fit_dir,f)):
                    continue
                if "do_fits" not in f or ".sh" not in f:
                    continue
                condor_sh_file.write("if [ $1 -eq "+str(n)+" ]; then \n")
                condor_sh_file.write("source "+os.path.join(param_fit_dir,f)+" \n")
                condor_sh_file.write("fi \n")
                n+=1

            condor_sub_file.write("queue "+str(n)+"\n")
            condor_sh_file.close()
            condor_sub_file.close()
            
            os.chdir(param_fit_dir)
            os.system("condor_submit condor_jobs.sub")
            os.chdir(current_dir)

            #merge_sub_file_path = os.path.join(param_dir, "merge_files.sub")
            #merge_sub_file = open(merge_sub_file_path, "w+")
            #merge_sub_file.write("executable = merge_files.sh \n")
            #merge_sub_file.write("output = do_fits.$(ClusterId).$(ProcId).out \n")
            #merge_sub_file.write("error = do_fits.$(ClusterId).$(ProcId).err \n")
            #merge_sub_file.write("log = do_fits.$(ClusterId).$(ProcId).log \n")
            #merge_sub_file.write("+MaxRuntime = 7200 \n\n")
            #merge_sub_file.write("queue 1 \n")
            #merge_sub_file.close()
            
            print ("")
            
            
            
