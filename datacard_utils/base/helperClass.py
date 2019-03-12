import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
import json
import os
import shutil
import fnmatch

class helperClass(object):

    def __init__(self):
        print "initializing helperClass"
        self._debug = 0
        self._JOB_PREFIX = """#!/bin/sh
ulimit -s unlimited
set -e
cd %(CMSSW_BASE)s/src
export SCRAM_ARCH=%(SCRAM_ARCH)s
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
eval `scramv1 runtime -sh`
cd -
""" % ({
    'CMSSW_BASE': os.environ['CMSSW_BASE'],
    'SCRAM_ARCH': os.environ['SCRAM_ARCH'],
    # 'PWD': os.environ['PWD']
    })


    @property
    def JOB_PREFIX(self):
        return self._JOB_PREFIX
    @JOB_PREFIX.setter
    def JOB_PREFIX(self, prefix):
        self._JOB_PREFIX = prefix
    
    def insert_values(self, cmds, keyword, toinsert = "", joinwith=","):
        # print "keyword:", keyword
        # print "toinsert:", toinsert
        if keyword in cmds:
            i = cmds.index(keyword)
            # print i
            if joinwith == "replace":
                # print i
                # print i+1
                cmds[i+1] = toinsert
            elif joinwith == "insert":
                pass
            elif joinwith == "remove":
                print "removing",keyword, toinsert
                print "index:", cmds.index(keyword)
                # cmds = [x for j, x in enumerate(cmds) if j != i or j!= i+1]
                cmds = cmds[:i] + cmds[i+2:]
                print cmds
            else:
                cmds[i+1] = joinwith.join([cmds[i+1],toinsert])
        else:
            if not joinwith == "remove":
                if not toinsert == "":
                    cmds += [keyword, toinsert]
                else:
                    cmds.append(keyword)
        return cmds

    def create_folder(self, folder, reset = False):
        if reset:
            if os.path.exists(folder):
                shutil.rmtree(folder)

        if not os.path.exists(folder):
            os.makedirs(folder) 

    def remove_extension(self, s):
        return ".".join(s.split(".")[:-1])

    def check_workspace(self, pathToDatacard):
        workspacePath = ""
        parts = pathToDatacard.split(".")
        outputPath = ".".join(parts[:len(parts)-1]) + ".root"
        if not os.path.exists(outputPath):
            print "generating workspace for", pathToDatacard
            
            bashCmd = ["source {0} ;".format(pathToCMSSWsetup)]
            bashCmd.append("text2workspace.py -m 125 " + pathToDatacard)
            bashCmd.append("-o " + outputPath)
            print bashCmd
            subprocess.call([" ".join(bashCmd)], shell = True)
       
        workspacePath = outputPath
       
        if os.path.exists(workspacePath):
            f = ROOT.TFile(workspacePath)
            if not (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
                workspacePath = ""
            else:
                test = f.Get("w")
                if not isinstance(test, ROOT.RooWorkspace):
                    print "could not find workspace in", workspacePath
                    workspacePath = ""
        else:
            print "could not find", workspacePath
            workspacePath = ""
        return workspacePath