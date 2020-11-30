from sys import path as spath
import os

thisdir = os.path.realpath(os.path.dirname(__file__))
baserepodir = os.path.join(thisdir, "..", "..", "base")
if not baserepodir in spath:
    spath.append(baserepodir)
# from helperClass import helperClass as helperClass_base
class helperClass(object):
    def __init__(self):
        super(helperClass, self).__init__()
        if not ("CMSSW_BASE" in os.environ or "SCRAM_ARCH" in os.environ):
            exit("You need to setup CMSSW")
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
