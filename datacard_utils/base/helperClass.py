import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
import json
import os
import shutil
import fnmatch
import subprocess

# import extension with helpful functions
from helpfulFuncs import helpfulFuncs

class helperClass(helpfulFuncs):

    def __init__(self):
        print("initializing helperClass")
        self._debug = 0
        if not ("CMSSW_BASE" in os.environ or "SCRAM_ARCH" in os.environ):
            exit("You need to setup CMSSW")
        self._JOB_PREFIX = """#!/bin/sh
ulimit -s unlimited
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
        toinsert = str(toinsert)
        if keyword in cmds and not joinwith == "add":
            i = cmds.index(keyword)
            # print i
            if joinwith == "replace":
                # print i
                # print i+1
                cmds[i+1] = toinsert
            elif joinwith == "insert":
                pass
            elif joinwith == "remove":
                print( "removing '{} {}'".format(keyword, toinsert))
                print( "index: {}".format(cmds.index(keyword)))
                # cmds = [x for j, x in enumerate(cmds) if j != i or j!= i+1]
                cmds = cmds[:i] + cmds[i+2:]
                print( cmds)
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
            print( "resetting folder", folder)
            if os.path.exists(folder):
                shutil.rmtree(folder)

        if not os.path.exists(folder):
            os.makedirs(folder) 
    
    def remove_extension(self, s):
        return ".".join(s.split(".")[:-1])

    def check_workspace(self, pathToDatacard, additional_cmds = ""):
        workspacePath = ""
        parts = pathToDatacard.split(".")
        outputPath = ".".join(parts[:len(parts)-1]) + ".root"
        if not os.path.exists(outputPath):
            print( "generating workspace for {}".format(pathToDatacard))
            
            bashCmd = ["{0} ;".format("; ".join(self._JOB_PREFIX.split()))]
            bashCmd.append("text2workspace.py -m 125.38 " + pathToDatacard)
            bashCmd.append(additional_cmds)
            bashCmd.append("-o " + outputPath)
            print( bashCmd)
            subprocess.call([" ".join(bashCmd)], shell = True)
       
        workspacePath = outputPath
       
        if os.path.exists(workspacePath):
            f = ROOT.TFile(workspacePath)
            if not (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
                workspacePath = ""
            else:
                test = f.Get("w")
                if not isinstance(test, ROOT.RooWorkspace):
                    print ("could not find workspace in {}".format(workspacePath))
                    workspacePath = ""
        else:
            print ("could not find {}".format(workspacePath))
            workspacePath = ""
        return workspacePath
    def check_for_twin(self, name, iteration=0):

        tocheck = name
        ext = "." + name.split(".")[-1]
        if not iteration == 0:
            add = "_" + str(iteration)
            tocheck = tocheck.replace(ext, add + ext)
        if os.path.exists(tocheck):
            iteration += 1

            tocheck = self.check_for_twin(name, iteration)
        return tocheck
        
    def dump_json(self, outname, allvals):
        if len(allvals) > 0:
            print ("opening file {}".format(outname))
            with open(outname, "w") as outfile:
                json.dump(allvals, outfile, indent = 4, separators = (',', ': '))
        else:
            print ("given dictionary is empty, will not create '{}'".format(outname))

    def is_number(self, s):
        s.replace("p", ".")
        try:
            float(s)
            return True
        except ValueError:
            print ("{0} is not a number!".format(s))
            return False

    def intact_root_file(self, f):

        if f and isinstance(f, ROOT.TFile):
            if f.IsOpen():
                if not f.IsZombie():
                    if not f.TestBit(ROOT.TFile.kRecovered):
                        return True
                    else:
                        if self._debug >= 99: 
                            print ("ERROR: file '%s' is recovered!" % f.GetName())
                else:
                    if self._debug >= 99:
                        print ("ERROR: file '%s' is zombie!" % f.GetName())
            else:
                if self._debug >= 99:
                    print ("ERROR: file '%s' is not open" % f.GetName())
        return False
    
    def is_good_fit(self, result):
        if result.status() == 0 and result.covQual() == 3:
            return True
        print ("WARNING: This is not a good fit!")
        print ("\tStatus: {0}\tQuality: {1}".format(result.status(), result.covQual()))
        return True #DANGERZONE!

    def load_roofitresult(self, rfile, fitres = "fit_s"):
        result = rfile.Get(fitres)
        if not isinstance(result, ROOT.RooFitResult):
            result = rfile.Get("fit_mdf")
            if not isinstance(result, ROOT.RooFitResult):
                result = None
        if result and not self.is_good_fit(result):
            result = None
        
        return result


    def load_variable(self, result, parname):
        var = result.floatParsFinal().find(parname)
        if isinstance(var, ROOT.RooRealVar):
            return var

    def load_postfit_uncert_from_variable(self, filename, parname, fitres = "fit_s"):
        f = ROOT.TFile(filename)
        error = None
        if self.intact_root_file(f):
            result = self.load_roofitresult(rfile = f, fitres = fitres)
            if result:
                var = self.load_variable(result = result, parname = parname)
                if var:
                    error = var.getError()
        if f.IsOpen(): f.Close()
        return error

    def load_postfit_uncert(self, filename, parname, fitres = "fit_s"):
        vals = self.load_asym_postfit(filename = filename, parname = parname, fitres = fitres)
        # vals = None
        if vals:
            value = (vals[1] + vals[2])/2
            value = 0
            if value != 0:
                return value
            else:
                return self.load_postfit_uncert_from_variable(filename = filename, parname = parname, fitres = fitres)


    def load_asym_postfit(self, filename, parname, fitres = "fit_s"):
        f = ROOT.TFile.Open(filename)
        if self.intact_root_file(f):
            result = self.load_roofitresult(rfile = f, fitres = fitres)
            if result:
                var = self.load_variable(result = result, parname = parname)
                if var:
                    value = var.getVal()
                    errorhi = var.getErrorHi()
                    errorlo = var.getErrorLo()
                    f.Close()
                    return value, errorhi, abs(errorlo)
                else:
                    print ("Could not load RooRealVar %s from %s" % (parname, filename))
            else:
                print ("Could not load RooFitResult from %s" % (filename))
        else:
            print ("File %s is not intact!" % filename)
        if f.IsOpen(): f.Close()
        return None
