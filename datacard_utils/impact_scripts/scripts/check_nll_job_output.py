import os, sys, glob
from subprocess import call

if __name__ == '__main__':
    current_dir = os.path.abspath(os.getcwd())
    for comb_dir in glob.glob(current_dir+"/*"):
        if not os.path.isdir(comb_dir):
            continue
        print (comb_dir.split("/")[-1])
        for nuisance_dir in glob.glob(comb_dir+"/*"):
            print ("  " + nuisance_dir.split("/")[-1])
            fit_parts_dir = nuisance_dir + "/fit_parts"

            n_files = 0
            n_broken_files = 0
            for f in glob.glob(fit_parts_dir+"/*root"):
                n_files += 1
                size = os.path.getsize(f)
                if size<1000:
                    n_broken_files += 1
            if n_files!=100:
                print ("    ERROR: Missing fit result file, nr. of files = %d"%n_files)
            if n_broken_files>0:
                print ("    ERROR: %d Broken fit result files"%n_broken_files)
            if n_files == 0:
                print("Found no .root files at all, resubmitting")
                script_path = glob.glob(os.path.join(fit_parts_dir, "*.sub"))
                for s in script_path:
                    call(["condor_submit {}".format(s)], shell=True)

            merge_file = nuisance_dir + "/merged_combine_output.root"
            if not os.path.isfile(merge_file):
                print ("    Merged root file not present, will be created automatically in next step")
            else:
                size_root = os.path.getsize(merge_file)
                if size_root<1000:
                    os.system("rm -rf " + merge_file)
                    print ("    Broken merged root file, removed, will be created automatically in next step")
        print ("")


