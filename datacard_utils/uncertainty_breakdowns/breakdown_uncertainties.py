import os
import sys
import glob
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
ROOT.gDirectory.cd('PyROOT:/')
from optparse import OptionParser

directory = os.path.dirname(os.path.realpath(__file__))
basefolder = os.path.abspath(os.path.join(directory,"..", "base"))

if not basefolder in sys.path:
    sys.path.append(basefolder)

from batchConfig import batchConfig
batch_fits = batchConfig()
from helperClass import helperClass
helpfulFuncs = helperClass()

# pathToCMSSWsetup = '/nfs/dust/cms/user/pkeicher/setup_combine_cmssw.sh'
if not (os.path.exists(os.environ['CMSSW_BASE']) and os.environ['SCRAM_ARCH']):
    sys.exit("Please setup a CMSSW environment containing the lates combine version!")



# shell_template = """#!/bin/sh
# ulimit -s unlimited
# set -e
# targetdir="%(TARGETDIR)s"
# cmd="%(CMD)s"
# cmsswsource="%(CMSSW_SOURCE)s"
# if [[ -f $cmsswsource ]]; then
#   source $cmsswsource
#   if [[ -d $targetdir ]]; then
#     cd $targetdir
#     echo $cmd
#     eval $cmd
#     cd -
#   else
#     echo "could not change into directory $targetdir"
#   fi
# else
#   echo "could not find $cmsswsource"
# fi
# """

#=======================================================================

def add_basic_commands(cmd, mu, murange, suffix = ""):
    """
    Check if basic combine commands are present in the command 'cmd'.
    Basic commands include:
    -n
    --cminDefaultMinimizerStrategy
    --cminDefaultMinimizerTolerance
    --rMin/--rMax
    if variable 'mu' is given: triggers generation of asimov toy with signal strength 'mu'
    """
    fitrangeUp = murange
    fitrangeDown = -1*murange
    if mu is not None:
        fitrangeUp += mu
        fitrangeDown += mu
    cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "-n", toinsert = suffix, joinwith = "_")
    cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "-m", toinsert = "125.38", joinwith = "insert")

    cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--cminDefaultMinimizerStrategy", toinsert = "0", joinwith = "insert")
    cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--cminDefaultMinimizerTolerance", toinsert = "1e-3", joinwith = "insert")
    # cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--rMin", toinsert = str(fitrangeDown), joinwith = "insert")
    # cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--rMax", toinsert = str(fitrangeUp), joinwith = "insert")
    
    if mu is not None:
        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "-t", toinsert = "-1", joinwith = "insert")
        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--expectSignal", toinsert = str(mu), joinwith = "insert")
    if "MultiDimFit" in cmd and not "FitDiagnostics" in cmd:
        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--floatOtherPOIs",
                                            toinsert=str(1), joinwith="insert"
                                        )
        
        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--floatOtherPOIs",
                                            toinsert=str(1), joinwith="insert"
                                        )
    

def create_script(cmd, scriptname, outfolder = None, wsfile = None):
    """
    Create .sh script containing the command 'cmd'. Additionally, there is a check
    for the existence of the folder 'outfolder', into which the output of the command
    is supposed to be saved. If 'outfolder' is not given, the output is saved into
    the current directory.
    """

    script = [helpfulFuncs.JOB_PREFIX]
    # script = ["ulimit -s unlimited"]
    # script.append("if [ -f " + pathToCMSSWsetup + " ]; then")
    # script.append("  source " + pathToCMSSWsetup)
    if outfolder is not None:
        block = """
          if [ -d "%(OUTFOLDER)s" ]; then
            cd %(OUTFOLDER)s
        """ % ({"OUTFOLDER" : outfolder})
        script.append(block)

    script.append("    if [ -f " + wsfile + " ]; then")

    for c in cmd:
        block = """
            cmdnominal='%s'
            echo "$cmdnominal"
            eval "$cmdnominal"\n
        """ % " ".join(c)
        # script.append(')
        # script.append('')
        # script.append('')
        script.append(block)

    block = """
        else
            echo 'could not find input for combine here: "%s"!'
        fi
    """ % wsfile
    script.append(block)
    # script.append("    else")
    # script.append('      echo "could not find input for combine here: ' + wsfile +'!"')
    # script.append("    fi")

    if outfolder is not None:
        block = """
          else
            echo 'folder "%s" does not exist!'
          fi
        """ % outfolder
        # script.append("  else")
        # script.append('    echo "folder {0} does not exist!"'.format(outfolder))
        # script.append("  fi")
        script.append(block)

    # script.append("else")
    # script.append('  echo "Could not find CMSSW setup file!"')
    # script.append("fi")

    with open(scriptname, "w") as s:
        s.write("\n".join(script))

def finish_cmds(cmd, 
mu, 
murange, 
suffix, 
paramgroup, 
param = None, 
pois = None,
freeze_parameters = None):
    """
    Finalize the combine command given in 'cmd', which means appending the freeze options
    for uncertainty group 'paramgroup'.
    """
    add_basic_commands(cmd = cmd, mu = mu, murange = murange, suffix = suffix)
    
    #if the command is not generating a stat-only fit, freeze the given uncertainty group. Otherwise, freeze all nuisance parameters
    if paramgroup and not freeze_parameters:
        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--freezeNuisanceGroups", toinsert = paramgroup, joinwith = ",")
    elif isinstance(freeze_parameters, str):
        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--freezeParameters", 
                                                toinsert = freeze_parameters,
                                                joinwith="insert"
                                            )
        
        # if (pois and param) and len(pois) > 1:
        #     tofreeze = pois[:]
        #     if param in tofreeze:
        #         tofreeze.pop(tofreeze.index(param))
        #     helpfulFuncs.insert_values(cmds = cmd, keyword = "--freezeParameters", 
        #                                 toinsert = '"var{}"'.format("|".join(tofreeze)), 
        #                                 joinwith=","
        #                             )

    cmd = [x for x in cmd if x != ""]

def create_fit_cmd( 
    mdfout, 
    paramgroup, 
    outfolder, 
    suffix,
    mu = None, 
    murange = 5., 
    cmdbase = None, 
    pois = None, 
    fast = False, 
    param = None,
    freeze_parameters = None
):
    """
    create script for the break down of the uncertainty group 'paramgroup'
    """
    all_cmds = []
    if not fast:
        cmd = "combine -M MultiDimFit".split()
        cmd.append(mdfout)
        cmd += "--algo grid --points 50".split()
        cmd = helpfulFuncs.insert_values(cmds= cmd, keyword = "--floatOtherPOIs", toinsert = str(1), joinwith = "insert")
        if cmdbase:
            cmd += cmdbase
        if paramgroup:
            cmd += '-w w --snapshotName MultiDimFit'.split()

        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--saveFitResult", toinsert = "", joinwith = "insert")

        if paramgroup and paramgroup == "all":
            cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--fastScan", toinsert = "", joinwith = "insert")

        finish_cmds(cmd=cmd,mu=mu,murange=murange,suffix="_"+suffix,
                        paramgroup=paramgroup,pois=pois, param = param,
                        freeze_parameters = freeze_parameters)
        
        
        all_cmds.append(cmd)

    cmd = "combine -M FitDiagnostics".split()
    cmd += mdfout.split()
    if cmdbase:
        cmd += cmdbase
    if paramgroup:
        cmd += '-w w --snapshotName MultiDimFit'.split()
    # cmd += "--minos all".split()
    temp = paramgroup
    
    finish_cmds(cmd = cmd,mu=mu,murange=murange,suffix= "_"+suffix,paramgroup=temp,pois=pois, param = param,
                freeze_parameters = freeze_parameters
                )
    all_cmds.append(cmd)

    outscript = "script_"+paramgroup + ".sh"
    if param:
        outscript = outscript.replace(".sh", "_%s.sh" % param)
    
    create_script(cmd = all_cmds, scriptname = outscript, outfolder = outfolder, wsfile = mdfout)

    if os.path.exists(outscript):
        return outscript
    
    return ""

def loadPOIs(workspace):
    """
    Loads the list of POIs from the input 'workspace'
    """
    print( "loading POIs from workspace in {}".format( workspace))
    infile = ROOT.TFile(workspace)
    w = infile.Get("w")
    npois = 1
    if isinstance(w, ROOT.RooWorkspace):
        mc = w.obj("ModelConfig")
        if isinstance(mc, ROOT.RooStats.ModelConfig):
            return mc.GetParametersOfInterest().contentsString().split(",")

def create_folders( 
    outfolder, 
    combineInput, 
    paramgroup, 
    suffix,
    mu, 
    scripts, 
    cmdbase, 
    murange, 
    pois = None, 
    fast = False, 
    param = None,
    freeze_parameters = None
):
    """
    create a folder for the uncertainty group 'paramgroup' and a corresponding .sh script containing
    the combine fit commands.
    """
    helpfulFuncs.create_folder(folder = outfolder, reset = True)
    
            
    path = create_fit_cmd(  mdfout = combineInput,
            paramgroup = paramgroup,
            suffix = suffix,
            mu = mu,
            outfolder = outfolder,
            cmdbase = cmdbase,
            murange = murange,
            pois = pois,
            fast = fast,
            param = param,
            freeze_parameters = freeze_parameters)        
    if path:
        scripts.append(path)

def create_folders_and_scripts(foldername, combineInput, paramgroup, suffix,
                    mu, scripts, cmdbase, murange, pois = None, fast = False):
    """
    Trigger the generation of the folder structure for the uncertainty group 'paramgroup'.
    If the list if POIs is not None, the function will generate a stat only fit for every
    individual POI while freezing all other POIs.
    """

    # check for on the fly group definitions
    folder_name = paramgroup
    freeze_parameters = None
    if "=" in paramgroup:
        folder_name, freeze_parameters = paramgroup.split("=")

    outfolder = "breakdown_" + folder_name
    
    suffix += "_"+outfolder
 
    if paramgroup == "all":
        if pois:
            for param in pois:
                final_outfolder = "%s_%s" % (outfolder, param)
                create_folders(outfolder = final_outfolder, combineInput = combineInput,
                                paramgroup = folder_name, suffix = suffix,
                                mu = mu, scripts = scripts, cmdbase = cmdbase, murange = murange, 
                                pois = pois, fast = fast, param = param, freeze_parameters = "allConstrainedNuisances")
    else:
        create_folders(outfolder = outfolder, combineInput = combineInput,
                        paramgroup = folder_name, suffix = suffix,
                        mu = mu, scripts = scripts, cmdbase = cmdbase, murange = murange, 
                        pois = pois, fast = fast, freeze_parameters = freeze_parameters)

def add_params_for_minos(cmds, pois, parameters=None, stxs=False):
    if parameters is None:
        parameters = [
            "CMS_ttHbb_bgnorm_ttbb",
            "CMS_ttHbb_tt2b_glusplit"
        ]
    final_set = list()
    if stxs:
        final_set += parameters
        final_set += [
            "{}_STXS_{}".format(p, i)
            for p in parameters
            for i in range(5)
        ]
    else:
        final_set = parameters
    final_set.append("CMS_ttHbb_bgnorm_ttcc")
    final_set.extend(pois)
    cmds += ["-P {}".format(p) for p in final_set]


def submit_fit_cmds(
    ws,
    paramgroups = ["all"],
    mu = None,
    cmdbase = None,
    murange = 5.,
    suffix = "",
    pois = None,
    fast = False,
    stxs=False,
):
    """
    Create a folder for the workspace 'ws', create the folder structure for every uncertainty group in 'paramgroups' and the
    corresponding .sh scripts and submit everything to the batch system for parallel processing.
    The folder for the respective workspace are reset by default.
    By default, the nominal likelihood scan is performed and a snapshot of the bestfit is saved. Afterwards, the folders and 
    scripts for the actual uncertainty breakdowns are generated.
    If the option 'fast' is True, the likelihood scans will be skipped.
    """

    #create workspace folder
    print ("entering submit_fit_cmds")
    if not os.path.exists(ws):
        raise sys.exit("workspace file %s does not exist!" % ws)
    # parts = os.path.basename(ws).split(".")
    foldername = helpfulFuncs.remove_extension(os.path.basename(ws))
    if suffix:
        foldername = suffix + "_" + foldername
    helpfulFuncs.create_folder(folder = foldername, reset = True)
    os.chdir(foldername)
    print (os.getcwd())

    
    #do nominal scan
    if not fast:
        cmd = "combine -M MultiDimFit --algo grid --points 50".split()
        if cmdbase:
            cmd += cmdbase
        add_basic_commands(cmd = cmd, mu = mu, murange = murange, suffix = "_nominal_" + foldername)

        cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--saveFitResult", toinsert = "", joinwith = "insert")
        cmd.append(ws)
        create_script(cmd = [cmd], scriptname = "nominal_scan.sh", wsfile = ws)
        if os.path.exists("nominal_scan.sh"):
            batch_fits.submitJobToBatch("nominal_scan.sh")
            pass
        else:
            sys.exit("could not create script for nominal scan! Aborting")

    #do bestfit
    cmd = "combine -M MultiDimFit --saveWorkspace --algo singles".split()
    if cmdbase:
        cmd += cmdbase
    add_basic_commands(cmd = cmd, mu = mu, murange = murange, suffix = "_bestfit_" + foldername)
    add_params_for_minos(cmds=cmd, pois=pois, stxs=stxs)
    cmd = helpfulFuncs.insert_values(cmds = cmd, keyword = "--saveFitResult", toinsert = "", joinwith = "insert")
    cmd.append(ws)


    prefit_script = "bestfit.sh"
    create_script(cmd=[cmd], scriptname = prefit_script, wsfile = ws)
    if os.path.exists(prefit_script):
        print ("successfully created prefit script, submitting")
        jobid = batch_fits.submitJobToBatch(prefit_script)
        scripts = []
        mdfout = "higgsCombine"
        mdfout += cmd[cmd.index("-n")+1]
        mdfout += ".MultiDimFit.mH125.38.root"
        mdfout = os.path.abspath(mdfout)
        #start scancs with frozen np groups
        if not "all" in paramgroups:
            paramgroups.append("all")
        for group in paramgroups:
            create_folders_and_scripts( foldername = foldername,
                            combineInput = mdfout,
                            paramgroup = group,
                            suffix = foldername,
                            mu = mu, scripts = scripts,
                            cmdbase = cmdbase, murange = murange,
                            pois = pois, fast = fast
                            )
        # if not "all" in paramgroups:
        #     create_folders( foldername = foldername,
        #               combineInput = mdfout,
        #               paramgroup = "all",
        #               suffix = foldername,
        #               mu = mu, scripts = scripts,
        #               cmdbase = cmdbase, murange = murange,
        #               pois = pois, fast = fast)

        if(len(scripts) > 0):
            print ("submitting {0} jobs".format(len(scripts)))
            return batch_fits.submitArrayToBatch(   scripts = scripts,
                        arrayscriptpath = "arrayJob.sh",
                        jobid = jobid )
        return -1

def parse_arguments():
    parser = OptionParser()
    parser.add_option(  "-a", "--addCommands", 
                        help="additional combine commands (can be used multiple times)", 
                        action="append", 
                        dest = "addCommands",
                        metavar = "'list of combine options'",
                        type = "str"
                    )
    parser.add_option(  "-r", "--mu",
                        help = "signal strength for asimov toys",
                        dest = "mu",
                        type= "float")
    parser.add_option( "--stxs",
                        help= "add partially decorrelated ttbb parameters to list of POIs for bestfit",
                        dest = "stxs",
                        action="store_true",
                        default=False,
    )
    parser.add_option(  "--murange",
                        help= "+/- range around injected value to be scanned",
                        type = "float",
                        default = 5.0,
                        dest = "murange")
    parser.add_option(  "-b", "--breakdown",
                        help = """list of parameter groups to break down. Either collon-separated or can be used multiple times.
                        Please note that the keyword for the stat-only fit is 'all' (will be generated automatically if not given explicitely)
                        """,
                        action = "append",
                        dest = "paramgroups",
                        )
    parser.add_option(  "-s", "--suffix",
                        help = "add this suffix to output files",
                        dest = "suffix")
    parser.add_option(  "-f", "--fast",
                        help = "skip NLL scans, just perform fits",
                        dest = "fast",
                        action = "store_true",
                        default = False
                    )
    (options, args) = parser.parse_args()
    return options, args

#=======================================================================

def main(options, wildcards):
    mu = options.mu
    murange = options.murange
    # print wildcards
    paramgroups = []
    if options.paramgroups == None:
        paramgroups = ["all"]
    else:
        for group in options.paramgroups:
            paramgroups += group.split(":")
    combineoptions = []
    if options.addCommands != None:
        for cmd in options.addCommands:
            combineoptions += cmd.split()

    base = os.getcwd()
    for wildcard in wildcards:
        for d in glob.glob(wildcard):
            d = os.path.abspath(d)
            if os.path.exists(d):
                print( "checking %s for workspace" % d)
                d = helpfulFuncs.check_workspace(d)
                pois = loadPOIs(d)
                arrayid = submit_fit_cmds(  ws = d,
                                            paramgroups = paramgroups,
                                            mu = mu,
                                            murange= murange,
                                            cmdbase = combineoptions,
                                            suffix = options.suffix,
                                            pois = pois,
                                            fast = options.fast,
                                            stxs=options.stxs
                                        )
                if arrayid != -1:
                    print( "all fits submitted to batch")
                os.chdir(base)

if __name__ == '__main__':
    options, wildcards = parse_arguments()
    main(options = options, wildcards = wildcards)


    
    
