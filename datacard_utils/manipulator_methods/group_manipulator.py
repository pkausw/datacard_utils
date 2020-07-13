import os
import ROOT
from pprint import pformat
cmssw_base = os.environ["CMSSW_BASE"]
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

if not os.path.exists(cmssw_base):
    raise ValueError("Could not find CMSSW base!")

try:
    print("importing CombineHarvester")
    import CombineHarvester.CombineTools.ch as ch
    print("done")
except:
    msg = " ".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)

class GroupManipulator(object):
    def __init__(self):
        self.groups = {
            "sig_thy" : [
                ".*QCDscale_ttH$", 
                ".*pdf_Higgs_ttH$",
                ".*ISR_ttH$",
                ".*FSR_ttH$", 
            ], 
            "thy" : [
                ".*QCDscale.*", 
                ".*pdf.*", 
                "^CMS_ttHbb_bgnorm.*", 
                ".*ISR.*", 
                ".*FSR.*", 
                ".*HDAMP.*", 
                ".*PDF.*", 
                ".*scaleMu.*"
            ], 
            "exp" : [
                "^CMS_btag.*", 
                "^CMS_eff.*", 
                "^CMS_res_j.*", 
                "^CMS_scale.*j.*", 
                "^CMS_ttHbb_PU", 
                ".*L1PreFiring.*", 
                ".*UE.*"

            ], 
            "ps": [
                ".*ISR.*", 
                ".*FSR.*", 
                ".*HDAMP.*", 
                ".*UE.*"
                ],
            "jes": ["^CMS_scale.*j.*"], 
            "btag": ["^CMS_btag.*"], 
            "bgn": [".*bgnorm.*"], 
            "tthf_bgn": [".*bgnorm_tt.*"], 
            "tthf_model": [".*_tt.*"], 
            "ddQCD": [".*ddQCD.*", ".*TFLoose.*"], 
            "syst" : [".*"]
        }
    
    
    def add_groups_to_harvester(self, cb):
        if not isinstance(cb, ch.CombineHarvester):
            raise ValueError("object must be CombineHarvester instance!")
        for g in self.groups:
            cb.SetGroup(g, self.groups[g])

    def __str__(self):
        return pformat(self.groups, indent = 4, width = 1)
        