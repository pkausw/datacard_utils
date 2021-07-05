import os
import sys
import glob
import subprocess
from ROOT import TFile, RooFitResult, RooRealVar, RooWorkspace, RooStats
from shutil import rmtree

scriptDir = os.path.dirname(os.path.abspath(sys.argv[0]))
pathToTxt = sys.argv[1]
pathToDatacards = sys.argv[2]
cmdList = None
if len(sys.argv) > 3:
    cmdList = sys.argv[3:]

print "input:"
print "\tpathToTxt:", pathToTxt
print "\tpathToDatacards:", pathToDatacards
print "\tcmdList:\n", cmdList

basepath = os.getcwd()

def loadPOIs(workspace):
    """
    Loads the list of POIs from the input 'workspace'
    """
    print("loading POIs from workspace in " + workspace)
    infile = TFile(workspace)
    w = infile.Get("w")
    if isinstance(w, RooWorkspace):
        mc = w.obj("ModelConfig")
        if isinstance(mc, RooStats.ModelConfig):
            return mc.GetParametersOfInterest().contentsString().split(",")


def reset_directory(outputDirectory):
    if os.path.exists(outputDirectory):
        print "resetting ", outputDirectory
        rmtree(outputDirectory)
    os.makedirs(outputDirectory)

def do_prefit(datacard, cmdlist = None):
    
    # cmd = "combine -M FitDiagnostics -m 125.38 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 1e-5"
    cmd = "combine -M FitDiagnostics -m 125.38"
    if cmdlist:
        cmd += " "+ " ".join(cmdlist)
    cmd += " " + datacard
    print cmd
    subprocess.call([cmd], shell = True)
    if os.path.exists("fitDiagnostics.root"):
        infile = TFile("fitDiagnostics.root")
        if infile.IsOpen() and not infile.IsZombie() and not infile.TestBit(TFile.kRecovered):
            fit_s = infile.Get("fit_s")
            if isinstance(fit_s, RooFitResult):
                r = fit_s.floatParsFinal().find("r")
                if isinstance(r, RooRealVar):
                    return r.getVal()
                    
    print "could not load parameter r!"
    return None

def do_1D_scan(param, datacard, cmdList):
    reset_directory(param)
    os.chdir(param)
    cmd = ("python {0}/nllscan.py".format(scriptDir)).split()
    cmd += ("-d " + datacard).split()
    cmd += (' -x {0}'.format(param)).split()
    if cmdList:
        cmd += (" -a \"" + " ".join(cmdList) + "\"").split()
    # checkstring = "--setParameterRanges " + param
    # if not any(checkstring in x for x in cmd):
    #     cmd += (' -a "--setParameterRanges {0}=-2,2"'.format(param)).split()
    if r is not None:
        cmd += (' -a "--setParameters r={0}"'.format(r)).split()
    # cmd += " -n _" + os.path.basename(outputDirectory)
    cmd += '-a "--floatOtherPOIs 1"'.split()
    cmd += "--nPointsPerJob 10".split()
    
    print " ".join(cmd)
    subprocess.call([" ".join(cmd)], shell=True)
    os.chdir("../")
    
def do_2D_scan(param_x, param_y, datacard, cmdList):
    reset_directory(param_x)
    os.chdir(param_x)
    cmd = ("python {0}/nllscan.py".format(scriptDir)).split()
    cmd += ("-d " + datacard).split()
    cmd += (' -x {0}'.format(param_x)).split()
    cmd += (' -y {0}'.format(param_y)).split()
    if cmdList:
        cmd += (" -a \"" + " ".join(cmdList) + "\"").split()
    # checkstring = "--setParameterRanges " + param
    # if not any(checkstring in x for x in cmd):
    #     cmd += (' -a "--setParameterRanges {0}=-2,2"'.format(param)).split()
    if r is not None:
        cmd += (' -a "--setParameters r={0}"'.format(r)).split()
    # cmd += " -n _" + os.path.basename(outputDirectory)
    #cmd += '-a "--floatOtherPOIs 1"'.split()
    cmd += "--nPointsPerJob 10".split()
    #cmd += "--scan2D".split()
    #cmd += "--plot2D".split()
    
    print " ".join(cmd)
    subprocess.call([" ".join(cmd)], shell=True)
    os.chdir("../")

if os.path.exists(pathToTxt):
    
    with open(pathToTxt) as f:
        lines = f.read().splitlines()
    print "found datacards:"
    print glob.glob(pathToDatacards)
    # sys.exit(0)
    for datacard in glob.glob(pathToDatacards):
        datacard = os.path.abspath(datacard)
        parts = os.path.basename(datacard).split(".")
        outputDirectory = ".".join(parts[:len(parts)-1])
        reset_directory(outputDirectory = outputDirectory)
        os.chdir(outputDirectory)
        r = None
        # r = do_prefit(datacard = datacard, cmdlist = cmdList)
        for param in lines:
            if param == "": continue
            print param
            if param.startswith("#"):
                continue
            
            #do_1D_scan(param = param, datacard = datacard, cmdList = cmdList)
            pois = loadPOIs(datacard)
            if len(pois)>1:
                print ("Only 1 POI for 2D scans")
            param_r = pois[0]
            do_2D_scan(param_x = param, param_y = param_r, datacard = datacard, cmdList = cmdList)
            
        os.chdir(basepath)
    
