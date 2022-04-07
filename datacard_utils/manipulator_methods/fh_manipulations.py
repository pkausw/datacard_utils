from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import ROOT
import json
cmssw_base = os.environ["CMSSW_BASE"]
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

if not os.path.exists(cmssw_base):
    raise ValueError("Could not find CMSSW base!")
# import CombineHarvester.CombineTools.ch as ch

from optparse import OptionParser, OptionGroup

ROOT.TH1.AddDirectory(False)
try:
    print("importing CombineHarvester")
    import CombineHarvester.CombineTools.ch as ch
    print("done")
except:
    msg = " ".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)
thisdir = os.path.dirname(os.path.realpath(__file__))
if not thisdir in sys.path:
    sys.path.append(os.path.abspath(thisdir))
# manipulator_dir = os.path.join(thisdir, "manipulator_methods")
# if not manipulator_dir in sys.path:
#     sys.path.append(manipulator_dir)

class FHmanipulations(object):
    global_SF_2016 = 1.0114142451
    scale_factors = {
        "2016" : {
            "fh_j7_t4": 0.298331205916*global_SF_2016,
            "fh_j8_t4": 0.310568080696*global_SF_2016,
            "fh_j9_t4": 0.315537503101*global_SF_2016,
        },
        "2017" : {
            "fh_j7_t4": 0.324771466079,
            "fh_j8_t4": 0.336343954268,
            "fh_j9_t4": 0.347464438842,
        },
        "2018" : {
            "fh_j7_t4": 0.313797775386,
            "fh_j8_t4": 0.323104689866,
            "fh_j9_t4": 0.33753576508,
        }
    }
    
    
    
    def __init__(self):
        super(FHmanipulations, self).__init__()
        self.__debug = 10
        
    def scale_uncertainty(self, syst, scalefactor):
        name = syst.name()
        b = syst.bin()
        era = syst.era()
        up = syst.value_u()
        down = syst.value_d()
        if self.__debug >= 10:
            print("scaling uncertainy '{name}'".format(name=name))
            print("{bin:^{width}} {era:^{width}} {up:^{width}} {down:^{width}} {sf:^{width}}".format(
                width = 20,
                bin = "bin",
                era = "era",
                up = "up variation",
                down = "down variation",
                sf = "scale factor"
            ))
            print("{bin:^{width}} {era:^{width}} {up:^{width}.3f} {down:^{width}.3f} {sf:^{width}.3f}".format(
                width = 20,
                bin = b,
                era = era,
                up = up,
                down = down,
                sf = scalefactor
            ))
        syst.set_value_u(up*scalefactor)
        syst.set_value_d(down*scalefactor)
        if self.__debug >= 10:
            print("after scaling uncertainy")
            print("{bin:^{width}} {era:^{width}} {up:^{width}.3f} {down:^{width}.3f}".format(
                width = 20,
                bin = b,
                era = era,
                up = syst.value_u(),
                down = syst.value_d(),
            ))
        # sys.exit("DEBUG OUT")
        
    def apply_glusplit_scalefactors(self, harvester, stxs = False):
        print("applying scale factor for glusplit uncertainty in FH CR")
        cr_harvester = harvester.cp().process([".*_CR"])
        cr_harvester.PrintProcs()
        scale_dict = self.scale_factors if not stxs else None
        if not scale_dict:
            raise ValueError("sorry, haven't programmed this path yet")
        for era in scale_dict:
            if self.__debug >= 10:
                print("current era: {}".format(era))
            for b in scale_dict[era]:
                if self.__debug >= 10:
                    print("current bin: {}".format(b))
                factor = scale_dict[era][b]
                current_harv = cr_harvester.cp().era([era]).bin(["{}.*".format(b)])
                # current_harv.PrintAll()
                # current_harv.syst_name([".*_tt2b_glusplit"]).PrintSysts()
                current_harv.syst_name([".*_tt2b_glusplit"]).syst_type(["shape"]).ForEachSyst(
                    lambda x: self.scale_uncertainty(x, factor)
                )
        # sys.exit("DEBUG OUT")
def main():
    pass    

if __name__ == '__main__':
    main()