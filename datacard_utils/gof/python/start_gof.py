import sys
import os
import subprocess
from math import ceil

from glob import glob
from optparse import OptionParser

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.join(thisdir, "..", "..", "base")
if not basedir in sys.path:
    sys.path.append(basedir)

# import module to generate command string to load postfit results
if not thisdir in sys.path:
    sys.path.append(thisdir)

import create_postfit_value_string as postfit_reader 

from batchConfig import batchConfig
from helperClass import helperClass
helper = helperClass()
batch = batchConfig()


#Following two lines necessary in order to supress pyROOT help function
from ROOT import PyConfig, TFile
PyConfig.IgnoreCommandLineOptions = True

shell_template = helper.JOB_PREFIX + """
targetdir="%(TARGETDIR)s"
cmd='%(CMD)s'

if [[ -d $targetdir ]]; then
    cd $targetdir
    echo $cmd
    eval $cmd
    cd -
else
    echo "could not change into directory $targetdir"
fi

"""
base_gof_cmd = 'combine -M GoodnessOfFit --algo "{ALGO}"'
base_bestfit_cmd = 'combine -M FitDiagnostics'


def parse_arguments():
    global base_gof_cmd

    usage = """
    usage: %prog [options] path/to/datacards OR path/to/workspaces

    Current base commands
    For GoF: {gof}
    For Bestfit: {bestfit}
    """.format(
                gof = base_gof_cmd,
                bestfit = base_bestfit_cmd
            )

    parser = OptionParser(usage=usage)

    parser.add_option(  "-a", "--addCommands", 
                        help="""additional combine commands (can be used 
                        multiple times). 
                        """, 
                        action="append", 
                        dest = "additionalCommand"
                    )
    parser.add_option(  "--runLocally", "-r",
                        help="""run scripts locally instead of submitting them
                        to cluster""",
                        action="store_true",
                        dest = "runLocally",
                        default= False
                    )
    parser.add_option(  "-n", "--nToys",
                        help = "Use this number of toys for test (default=300)",
                        type = "int",
                        default = "300",
                        dest = "nToys"
                    )
    parser.add_option(  "--asimov",
                        help = "perform first fit on Asimov dataset (for debug)",
                        action = "store_true",
                        default = False,
                        dest = "asimov"
                    )
    parser.add_option(  "--skipBestFits",
                        help = """skip the generation of the best fits, 
                        only do the GOF""",
                        action = "store_true",
                        default = False,
                        dest = "skip_bestfit"
                    )
    parser.add_option(  "--skipGOFdata",
                        help = """skip the generation of the GOF to data""",
                        action = "store_true",
                        default = False,
                        dest = "skip_gof_data"
                    )
    parser.add_option(  "--skipGOFtoys",
                        help = """skip the generation of the GOF to toys""",
                        action = "store_true",
                        default = False,
                        dest = "skip_gof_toys"
                    )
    parser.add_option(  "--data_obs_name" , "-d",
                        help = "use this name for observation (default = data_obs)",
                        dest = "data_obs",
                        default = "data_obs"
                    )
    parser.add_option(  "--background-only" , "-b",
                        help = "perform the GOF with the background-only hypothesis (default = False)",
                        dest = "background_only",
                        default = False,
                        action = "store_true"
                    )
    parser.add_option(  "--loadPostfitFrom" , "-l",
                        help = " ".join("""
                            load postfit results from this file. The input 
                            should have this format:
                            /path/to/root/file:object_to_read_from
                            e.g. fitDiagnostics.root:fit_s to read the 
                            signal+background results.  
                            Use this option to generate postfit p values!
                            """.split()),
                        dest = "postfit_results",
                        metavar = "/path/to/root/file:object_to_read_from",
                        type = "str"
                    )
    parser.add_option(  "-o", "--outputPath",
                        help = "save GOF test in this directory",
                        dest = "outputPath",
                        type = "str",
                        metavar = "path/to/save/outputs/in",
                        default = "."

                    )
    parser.add_option(  "-f", "--fixSignalTo",
                        help = " ".join("""
                            fix the signal strength everywhere to this value
                            """.split()),
                        dest = "signal_strength",
                        type = "float",
                        default = None

                    )
    parser.add_option( "--nToysPerJob",
                        help = """Split generation in multiple jobs. Input is the number of toys per job 
                                (default: generate all toys in one job)""",
                        dest = "nToysPerJob",
                        metavar = "n_toys_per_job",
                        type = "int",
                        default = -1
                    )
    parser.add_option( "--skip-submit",
                        help = """Just generate the files to generate the toys but do not submit anything (Default: False)""",
                        dest = "skip_submit",
                        default = False,
                        action = "store_true"
                    )
    parser.add_option( "--algorithm", "--algo",
                        help = """Use this method for the GoF test. Choices: saturated, KS, AD. Defaults to saturated""",
                        dest = "algorithm",
                        default = "saturated",
                        choices = "saturated KS AD".split(),
                    )
    
    (options, args) = parser.parse_args()

    base_gof_cmd = base_gof_cmd.format(ALGO=options.algorithm)
    if not options.postfit_results is None:
        filepath, result_object = options.postfit_results.split(":")
        if not (filepath and os.path.exists(filepath)):
            parser.error("ERROR: Path '%s' does not exist!" % filepath)
        filepath = os.path.abspath(filepath)
        options.postfit_results = ":".join([filepath, result_object])
    batch.dry_run = options.skip_submit
    
    if options.background_only:
        options.signal_strength = 0
    return options, args

def generate_gof_cmd(datacard, nToys = None, additional_cmds = None,
                         run_asimov = False, no_frequentist_toys = False):
    code = []
    code += base_gof_cmd.split()
    if additional_cmds:
        #make sure there are no double white spaces in additional cmds
        code += additional_cmds
    code = helper.insert_values( cmds = code, keyword = "-m",
                                    toinsert = "125.38", joinwith="insert"
                                )
    if run_asimov and nToys is None:
        code = helper.insert_values(    cmds = code, keyword = "-t", 
                                        toinsert = "-1", joinwith="insert")
        code = helper.insert_values(    cmds = code, keyword = "-n", 
                                        toinsert = "asimov", joinwith="_")
    elif not nToys is None:
        t = str(nToys)
        code = helper.insert_values(    cmds = code, keyword = "-t", 
                                        toinsert = t, joinwith="insert")
        code = helper.insert_values(    cmds = code, keyword = "-s", 
                                        toinsert = "-1", joinwith="insert")
        if run_asimov:
            code = helper.insert_values(    cmds = code, 
                                        keyword = "--toysNoSystematics", 
                                        toinsert = "", joinwith="insert")
        else:
            if not no_frequentist_toys:
                code = helper.insert_values(    cmds = code, 
                                            keyword = "--toysFrequentist", 
                                            toinsert = "", joinwith="insert")
        code = helper.insert_values(    cmds = code, keyword = "-n", 
                                        toinsert = t+"_toys", joinwith="_")

    code.append(datacard)
    return " ".join(code)



def generate_bestfit_cmd(datacard, additional_cmds = None,
                         run_asimov = False, postfit_path = None):
    code = []
    if postfit_path == None:
        code += base_bestfit_cmd.split()
        if additional_cmds:
            #make sure there are no double white spaces in additional cmds
            code += additional_cmds
        # code = helper.insert_values(    cmds = code, keyword = "--rMin", 
        #                                 toinsert = "-1", joinwith="insert")
        # code = helper.insert_values(    cmds = code, keyword = "--saveShapes", 
        #                                     toinsert = "", joinwith="insert")
        # code = helper.insert_values(    cmds = code, keyword = "--saveWithUncertainties", 
        #                                     toinsert = "", joinwith="insert")
        code = helper.insert_values( cmds = code, keyword = "-m",
                                    toinsert = "125.38", joinwith="insert"
                                )
        if run_asimov:
            code = helper.insert_values(    cmds = code, keyword = "-t", 
                                            toinsert = "-1", joinwith="insert")
            code = helper.insert_values(    cmds = code, keyword = "-n", 
                                            toinsert = "asimov", joinwith="_")

        code.append(datacard)
    else:
        dirname = os.path.dirname(datacard)
        base = helper.remove_extension(os.path.basename(datacard))
        code += "PostFitShapesFromWorkspace --postfit --sampling --print".split()
        code = helper.insert_values( cmds = code, keyword = "-m",
                                    toinsert = "125.38", joinwith="insert"
                                )
        # code += ("-d " + os.path.join(dirname, base + ".txt")).split()
        code += ("-w " + os.path.join(dirname, base + ".root")).split()
        code += ("-o " + "postfit_shape_%s.root" % base).split()
        code += ("-f " + postfit_path).split()
    return " ".join(code)

def write_combine_script(   datacard, outname, nToys = None, 
                            additional_cmds = None, run_asimov = False,
                            mode = "gof", no_frequentist_toys = False,
                            postfit_path = None
                            ):
    code = []
    targetdir = os.getcwd()
    cmd = ""
    if mode == "gof":
        cmd = generate_gof_cmd( datacard = datacard, nToys = nToys, 
                                additional_cmds = additional_cmds, 
                                run_asimov = run_asimov,
                                no_frequentist_toys = no_frequentist_toys)
    if mode == "bestfit":
        cmd = generate_bestfit_cmd( datacard = datacard, additional_cmds = additional_cmds,
                                    run_asimov = run_asimov, postfit_path = postfit_path
                                    )
    code = shell_template % ({
            "CMD" : cmd,
            "TARGETDIR" : targetdir
        })

    # print "\n".join(code)
    # print code
    with open(outname, "w") as f:
        f.write(code)
    return os.path.abspath(outname)

def generate_folder_and_script( folder, scriptname, datacard, nToys,
                                run_asimov, additional_cmds, mode = "gof",
                                no_frequentist_toys = False,
                                postfit_path = None,
                                nToysPerJob = -1
                                ):
    currentdir = os.getcwd()
    helper.create_folder(folder, reset = True)
    os.chdir(folder)
    nparts = 1 if nToysPerJob == -1 else int(ceil(float(nToys)/nToysPerJob))
    scripts = []
    ext = scriptname.split(".")[-1] 
    for i in range(nparts):
        tmp_scriptname = scriptname.replace("."+ext, "_{0}.{1}".format(i, ext))
        tmp_ntoys = nToys
        if not nparts == 1:
            tmp_ntoys = nToysPerJob if not i == nparts else nToys - i*nToysPerJob
        if not tmp_ntoys == 0:
            script = write_combine_script(  outname = tmp_scriptname,
                                            datacard = datacard, nToys = tmp_ntoys, 
                                            run_asimov = run_asimov,
                                            additional_cmds = additional_cmds,
                                            mode = mode,
                                            no_frequentist_toys = no_frequentist_toys,
                                            postfit_path = postfit_path)
            if os.path.exists(script):
                scripts.append(script)
    os.chdir(currentdir)
    return scripts

def append_to_additional_cmds(additional_cmds, postfit_string):
    l = additional_cmds
    if len(l) == 0:
        l = postfit_string.split()

    postfit_list = postfit_string.split()
    # print postfit_list
    skipNext = False
    for i in range(len(postfit_list)):
        if skipNext:
            skipNext = False
            continue
        # print "{0}/{1}".format(i, len(postfit_list))
        # print postfit_list[i]
        if not i == len(postfit_list):
            if not postfit_list[i+1].startswith("-"):
                # print "using next argument as well"
                keyword = postfit_list[i]
                toinsert = postfit_list[i+1]
                # print "keyword:", keyword
                # print "toinsert:", toinsert
                l = helper.insert_values( cmds = l, 
                                        keyword = keyword,
                                        toinsert = toinsert, 
                                        joinwith="replace")
                i += 1
                skipNext = True
                continue

        l = helper.insert_values( cmds = l, 
                                keyword = postfit_list[i],
                                toinsert = "", 
                                joinwith="replace")

    return l

def main(options, datacard_paths):
    """
    Script to perform combine's 'Goodness of Fit Test' for multiple datacards
    """
    runLocally = options.runLocally
    nToys = options.nToys
    run_asimov = options.asimov
    additional_cmds = []
    if options.additionalCommand:
        for cmd in options.additionalCommand:
            additional_cmds += cmd.split() if " " in cmd else [cmd]
    if not any(x in additional_cmds for x in ["-D", "--dataset"]):
        additional_cmds = helper.insert_values( cmds = additional_cmds, 
                                                keyword = "-D",
                                                toinsert = options.data_obs, 
                                                joinwith="insert")

    outputPath = options.outputPath
    skip_bestfit = options.skip_bestfit
    startdir = os.getcwd()
    # batch.runtime = 64800

    skip_frequentist_toys = False
    nToysPerJob = options.nToysPerJob

    if not options.postfit_results is None:
        filepath, result_object = options.postfit_results.split(":")
        rfile = TFile.Open(filepath)
        if not helper.intact_root_file(rfile):
            sys.exit("ERROR: File '%s' is broken!" % filepath)
        postfit_string = postfit_reader.create_postfit_input_cmd(rfile = rfile, fit = result_object)
        if postfit_string == "":
            sys.exit("ERROR: Could not load postfit values from object '%s' in file '%s'" % result_object, filepath)
        additional_cmds = append_to_additional_cmds(additional_cmds = additional_cmds, postfit_string = postfit_string)
        skip_frequentist_toys = True

    for wildcard in datacard_paths:
        for datacard in glob(wildcard):
            scripts = []
            datacard = os.path.abspath(datacard)
            # folder = os.path.dirname(datacard)
            filename = os.path.basename(datacard)
            filename = ".".join(filename.split(".")[:-1])
            folder = os.path.join(outputPath, filename)
            helper.create_folder(folder = folder, reset = True)
            os.chdir(folder)
            #check for workspace
            add_t2w_cmd = "-D %s --channel-masks" % options.data_obs
            path = helper.check_workspace(  pathToDatacard = datacard,
                                            additional_cmds = add_t2w_cmd
                                            )
            if path == "":
                s= "Could not generate workspace for '%s', skipping" % datacard
                print (s)
                continue
            datacard = path
            #perform fit to data
            tmp_cmds = additional_cmds[:]
            if not options.signal_strength is None:
                # tmp_cmds = helper.insert_values(    cmds = tmp_cmds, keyword = "--fixedSignalStrength", 
                #                         toinsert = "0", joinwith="replace")
                tmp_cmds = helper.insert_values(    cmds = tmp_cmds, 
                                                keyword = "--fixedSignalStrength", 
                                                toinsert = str(options.signal_strength), 
                                                joinwith="replace")
            if not options.skip_gof_data:
                scripts += generate_folder_and_script(folder = "gof_to_data",
                                                    scriptname = "gof_to_data.sh",
                                                    datacard = datacard,
                                                    nToys = None,
                                                    run_asimov = run_asimov,
                                                    additional_cmds = tmp_cmds,
                                                    no_frequentist_toys = skip_frequentist_toys
                                                    )
                # if not script is None:
                #     scripts.append(script)
            #perform fit to toys
            if not options.skip_gof_toys:
                scripts += generate_folder_and_script(folder = "gof_to_toys",
                                                    scriptname = "gof_to_toys.sh",
                                                    datacard = datacard,
                                                    nToys = nToys,
                                                    run_asimov = run_asimov,
                                                    additional_cmds = tmp_cmds,
                                                    no_frequentist_toys = skip_frequentist_toys,
                                                    nToysPerJob = nToysPerJob
                                                    )
                # if not script is None:
                #     scripts.append(script)

            #perform bestfit to data
            if not skip_bestfit:
                tmp_cmds = additional_cmds[:]
                if not options.signal_strength is None:
                    mu = options.signal_strength
                    s = "r={}".format(mu)
                    # precision to fix signal strength (should be tight)
                    prec = 1e-3
                    ranges = "r={},{}".format(mu-prec, mu + prec)
                    tmp_cmds = helper.insert_values( cmds = tmp_cmds, 
                                                keyword = "--setParameters", 
                                                toinsert = s, 
                                                joinwith=",")
                    tmp_cmds = helper.insert_values( cmds = tmp_cmds, 
                                                keyword = "--setParameterRanges", 
                                                toinsert = ranges, 
                                                joinwith=":")

                scripts += generate_folder_and_script(folder = "bestfit",
                                                scriptname = "bestfit.sh",
                                                datacard = datacard,
                                                nToys = None,
                                                run_asimov = run_asimov,
                                                additional_cmds = tmp_cmds,
                                                mode = "bestfit",
                                                postfit_path = options.postfit_results
                                                )
                # if not script is None:
                #     scripts.append(script)

            if len(scripts) > 0:
                if not runLocally:
                    #submit scripts as array job to batch
                    batchdir = "job_infos"
                    if not os.path.exists(batchdir):
                        os.mkdir(batchdir)
                    os.chdir(batchdir)
                    suffix = os.path.basename(datacard)
                    suffix = helper.remove_extension(suffix)
                    # arrayscriptname = "arrayScript_%s.sh" % suffix
                    arrayscriptname = "arrayJob.sh"
                    # batch.runtime = 60*60*5
                    batch.submitArrayToBatch(   scripts = scripts, 
                                            arrayscriptpath = arrayscriptname)
                else:
                    for script in scripts:
                        cmd = "source " + script
                        subprocess.call([cmd], shell=True)
            else:
                print( "ERROR: Could not generate any scripts for {}".format(datacard))
            os.chdir(startdir)

    
    os.chdir(startdir)
    



if __name__ == '__main__':
    options, datacard_paths = parse_arguments()
        
    if not len(datacard_paths) == 0:
        main(options = options, datacard_paths = datacard_paths)
    else:
        print ("You need to provide at least one datacard!")
