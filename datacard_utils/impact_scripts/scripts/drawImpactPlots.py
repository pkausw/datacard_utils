import os
import sys
import glob
import subprocess
import json
from ROOT import TFile, RooWorkspace, RooStats

def loadPOIs(workspace):
    """
    Loads the list of POIs from the input 'workspace'
    """
    print("loading POIs from workspace in " + workspace)
    infile = TFile.Open(workspace)
    w = infile.Get("w")
    if isinstance(w, RooWorkspace):
        mc = w.obj("ModelConfig")
        if isinstance(mc, RooStats.ModelConfig):
            return mc.GetParametersOfInterest().contentsString().split(",")

addCommands = sys.argv[1]
pathToJson = sys.argv[2]
pathToJson = os.path.abspath(pathToJson)
if os.path.exists(pathToJson) and pathToJson.endswith(".json"):
    print "loading impact submit infos from", pathToJson
    with open(pathToJson) as f:
        dic = json.load(f)
    listOfDatacards = dic["datacards"]
    listOfImpactFolders = dic["impact_folders"]
    origSubmitCmds = dic["commands"]
else:
    sys.exit("Input has to be a .json file!")
if len(sys.argv) != 3:
    wildcards = sys.argv[3:]
else:
    wildcards = listOfImpactFolders

basepath = os.getcwd()
print "wildcards:", wildcards
for wildcard in wildcards:
    print glob.glob(wildcard)
    os.chdir(basepath)
    for directory in glob.glob(wildcard):
        os.chdir(basepath)
        directory = os.path.abspath(directory)
        if not directory in listOfImpactFolders:
            print "The directory %s was not part of the submit saved in %s! Skipping" % (directory, pathToJson)
            continue
        workspace = os.path.basename(directory) + ".root"
        lworkspaces = [x for x in listOfDatacards if x.endswith(workspace)]
        if len(lworkspaces) == 0:
            print "The workspace %s was not part of the submit saved in %s! Skipping" % (workspace, pathToJson)
            continue
        if len(lworkspaces) != 1:
            print "Workspace %s has multiple occurances in submit json! Skipping" % workspace
            continue
        workspace = lworkspaces[-1]
        os.chdir(directory)
        print "changing into", directory
    
        
        print "checking for file", workspace
        if os.path.exists(workspace):
            print "creating impact plots for directory", directory
            taskname = os.path.basename(workspace).replace(".root", "")
            #taskname = taskname.replace("ttH_hbb_13TeV", "")
            impactName = os.path.basename(directory) + "_impacts"
            cmd = "combineTool.py -M Impacts -m 125.38"
            cmd += " -o " + impactName +".json"
            cmd += " -d " + workspace
            cmd += " -n " + taskname
            cmd += " " + " ".join(origSubmitCmds)
            cmd += " | tee json_creation.log"
            print cmd
            subprocess.call([cmd], shell=True)
            
            if os.path.exists(impactName +".json"):
                pois = loadPOIs(workspace)
                for poi in pois:
                    cmd = " ".join(("""plotImpacts.py -i {impactName}.json
                    -o {impactName}_{poi} --POI {poi} {addCommands}
                    | tee plotImpacts_{poi}.log""".format(impactName = impactName,
                                                            poi = poi,
                                                            addCommands = addCommands).split())
                                    )
                    print cmd
                    subprocess.call([cmd], shell=True)
                    # cmd = "plotImpacts.py -i " + impactName +".json"
                    # cmd += " -o " + impactName + "_10perpage"
                    # cmd += " --per-page 10"
                    # cmd += " " + addCommands
                    # cmd += " | tee plotImpacts_10perpage.log"
                    # print cmd
                    # subprocess.call([cmd], shell=True)
            else:
                print "could not find .json file"
        else:
            print "could not find workspace in", workspace
            os.chdir(basepath)

