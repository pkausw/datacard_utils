from __future__ import absolute_import
from __future__ import print_function
import os
import ROOT
from pprint import pformat
cmssw_base = os.environ["CMSSW_BASE"]
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

from .common_manipulations import CommonManipulations

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
            # "sig_thy" : {
            #     "parameters" : [
            #         ".*QCDscale_ttH$", 
            #         ".*pdf_Higgs_ttH$",
            #         ".*ISR_ttH$",
            #         ".*FSR_ttH$", 
            #         ".*scaleMu.*_ttH$"
            #     ],
            #     "split": False}, 
            "thy" : {
                "parameters": [
                    ".*QCDscale.*", 
                    ".*pdf.*", 
                    #"^CMS_ttHbb_bgnorm.*", 
                    ".*ISR.*", 
                    ".*FSR.*", 
                    ".*HDAMP.*", 
                    ".*PDF.*", 
                    ".*scaleMu.*",
                    ".*UE.*"
                ],
                "split": True
            }, 
            "exp" : {
                "parameters": [
                    "^CMS_btag.*", 
                    "^CMS_eff.*", 
                    "^CMS_res_j.*", 
                    "^CMS_scale.*j.*", 
                    "^CMS_ttHbb_PU", 
                    ".*L1PreFiring.*", 
                    "lumi.*",
                ],
                "split": False
            }, 
            "ps": {
                "parameters": [
                    ".*ISR.*", 
                    ".*FSR.*", 
                    ".*HDAMP.*", 
                    ".*UE.*"
                    ],
                "split": True
            },
            "jes": {
                "parameters": ["^CMS_scale.*j.*"],
                "split": False
            }, 
            "btag": {
                "parameters": ["^CMS_btag.*"],
                "split": False
            }, 
            "bgn": {
                "parameters": [".*bgnorm.*"],
                "split": False
            }, 
            "tthf_bgn": {
                "parameters": [".*bgnorm_ttbb.*"],
                "split": False}, 
            "tthf_model": {
                "parameters": [".*_ttbb", ".*_ttbbNLO"],
                "split": False
            }, 
            "ddQCD": {
                "parameters": [".*ddQCD.*", ".*TFLoose.*"],
                "split": False
            }, 
            "syst" : {
                "parameters": [".*"],
                "split": False},
            "mig" : {
                "parameters": ["d60","d120","d200","d300","d450","dy"],
                "split": False
            },
            "acc" : {
                "parameters": [".*_lowpt",".*_highpt"],
                "split": False
            },
            "STXS" : {
                "parameters": ["d60","d120","d200","d300","d450","dy",
                        "ttH_scale_lowpt","ttH_scale_highpt",
                        "ttH_ISR_highpt", "ttH_ISR_lowpt",
                        "ttH_FSR_highpt", "ttH_FSR_lowpt"],
                "split": False
            }
        }
        self.group_categories = {
            "ttH": ["ttH.*"],
            "tHq": ["tHq.*"],
            "tHW": ["tHW.*"],
            "ttbar": ["ttbb|ttcc|ttlf"],
            "ttbb": ["ttbb"]
        }
    
    def add_groups_to_harvester(self, cb):
        if not isinstance(cb, ch.CombineHarvester):
            raise ValueError("object must be CombineHarvester instance!")
        for g in self.groups:

            entry = self.groups[g]
            split = entry.get("split", False)
            if split:
                for c in self.group_categories:
                    new_group_name = "_".join([g, c])
                    processes = self.group_categories[c]
                    cb.cp().process(processes).SetGroup(
                        new_group_name, entry["parameters"]
                    )
            else:
                cb.SetGroup(g, entry["parameters"])

    def __str__(self):
        return pformat(self.groups, indent = 4, width = 1)
        