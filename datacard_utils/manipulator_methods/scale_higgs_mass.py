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
from subprocess import call
from fnmatch import filter

ROOT.TH1.AddDirectory(False)
try:
    print("importing CombineHarvester")
    import CombineHarvester.CombineTools.ch as ch
    print("done")
except:
    msg = " ".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)

class MassManipulator(object):
    
    def __init__(self):
        self.processes = [   'ttH_hbb',
                'ttH_hcc',
                'ttH_htt',
                'ttH_hgg',
                'ttH_hgluglu',
                'ttH_hww',
                'ttH_hzz',
                'ttH_hzg'
            ]
        self.basemass = 125
        self.apply = False
        self.xs_path = '$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root'
        self.br_path = '$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root'
    
    def GenerateScalingLine(self, objects, ws_name, path, source, wildcard):
        lines = []
        for e in objects:
            line = " ".join([e, "extArg", ":".join([path, ws_name])])
            line = "\n"+line
            lines.append(line)
            baseval = source.function(e).getVal()
            new_parname = e+"_rescale"
            line=' '.join([new_parname,'rateParam',"*",wildcard.format(e.replace("_13TeV", "")),"@0/%f"%baseval,e])
            lines.append(line)
            # line = "nuisance edit freeze {} ifexists".format(new_parname)
            # lines.append(line)
        return lines
            

    def MassScaling(self, productions, decays, basemass):
        ''' return a list of fully formed rateParameter with the xs*br scaling over the 125'''
        
        fXS=ROOT.TFile.Open(self.xs_path)
        fBR=ROOT.TFile.Open(self.br_path)
        
        wBR=fBR.Get("br")
        wXS=fXS.Get("xs_13TeV")
        
        wBR.var("MH").setVal(basemass)
        wXS.var("MH").setVal(basemass)
        xs_procs=[x+"_13TeV" for x in productions]
        print("xs_procs: {}".format(xs_procs))
        lines = self.GenerateScalingLine( objects = xs_procs, ws_name = "xs_13TeV",
                                    path = self.xs_path, source = wXS, wildcard = "{}_*")
        lines += self.GenerateScalingLine( objects = decays, ws_name = "br",
                                    path = self.br_path, source = wBR, wildcard = "*_{}")
        return lines


    def ScaleMasses(self, *args):
        """
        Function that generates lines to scale the production 
        cross section (XS) and branching ratios (BR) for
        the processes of this class.
        
        Inputs:
        
        args ([list]) --    list of files or CombineHarvester instances
                            If self.apply is True, the generated lines
                            are added to the files or the CombineHarvester
                            instances 
        """
        productions = []
        decays = []
        for p in self.processes:
            if "_" in p:
                prod, decay = p.split("_")
                productions.append(prod)
                decays.append(decay)
        
        productions = list(set(productions))
        decays = list(set(decays))
        
        lines = self.MassScaling(productions = productions, decays = decays, 
                            basemass = self.basemass)
        print("\n".join(lines))
        if self.apply:
            for f in args:
                if isinstance(f, str):
                    if not os.path.exists(f):
                        print("ERROR: file '{}' does not exist".format(f))
                        continue
                    elif os.path.isfile(f):
                        for l in lines:
                            cmd = 'echo "{}" >> {}'.format(
                                                l.replace("$", "\\$"), f)
                            print(cmd)
                            call([cmd], shell = True)
                elif isinstance(f, ch.CombineHarvester):
                    param_list = f.cp().syst_type(["rateParam", "extArg"]).syst_name_set()
                    for l in lines:
                        if not any(l.startswith(x) for x in param_list) and not l=="":
                            parts = l.split()
                            bins = f.bin_set()
                            param_type = parts[1]
                            print(parts)
                            print(tuple(parts[:-1]))
                            print(parts[-1])
                            if param_type == "extArg":
                                # f.cp().bin(bins).AddSyst(f, parts[0], parts[1], ch.SystMap()(parts[-1], ""))
                                f.AddDatacardLineAtEnd(l)
                            elif param_type == "rateParam":
                                current_bins = filter(bins, parts[2])
                                current_procs = filter(f.cp().bin(current_bins).process_set(), parts[3])
                                if len(current_procs) > 0:
                                    f.AddDatacardLineAtEnd(l)
                                

def main(*args, **kwargs):
    processes = kwargs.get("procs", [])
    basemass = kwargs.get("base_mass", 125)
    apply = kwargs.get("apply", False)
    mass_scaler = kwargs.get("mass_scaler", None)
    if not mass_scaler:
        raise ValueError("Could not load object 'mass_scaler'!")
    mass_scaler.processes = processes
    mass_scaler.basemass = basemass
    mass_scaler.apply = apply
    
    mass_scaler.ScaleMasses(*args)


def parse_arguments(mass_scaler):
    procs = mass_scaler.processes
    usage = " ".join("""
    Tool that generates lines to introde rate factors
    that scale the XS and BR according to
    an input higgs mass This tool employs functions
    from the CombineHarvester package. Please make sure
    that you have installed it!
    """.split())
    parser = OptionParser(usage = usage)

    parser.add_option("-b", "--base-mass",
                        help = " ".join(
                            """
                            Use this value as the base for the calculation,
                            i.e. the current value of the higgs mass.
                            Default: 125 GeV
                            """.split()
                        ),
                        dest = "base_mass",
                        metavar = "MASS_IN_GeV",
                        default = 125.09,
                        type = "float"
                    )
    parser.add_option("-p", "--process",
                      help = " ".join(
                          """
                          scale this process. Process name should follow 
                          general CMS combine naming convention, 
                          i.e. PRODUCTION_DECAY. Default: {}
                          """.format(",".join(procs)).split()
                        ),
                      action = "append",
                      metavar = "processes,to,scale",
                      dest = "procs"
                      )
    parser.add_option("-a", "--apply",
                      help = " ".join(
                          """
                          Add the generated scaling lines directly
                          to the datacards. Default: False
                          """.format(",".join(procs)).split()
                        ),
                      action = "store_true",
                      default = False,
                      dest = "apply"
                      )
    
    options, files = parser.parse_args()
    if options.procs is None or len(options.procs) == 0:
        options.procs = procs

    return options, files

if __name__ == "__main__":
    mass_scaler = MassManipulator()
    options, files = parse_arguments(mass_scaler)
    main(*files, mass_scaler = mass_scaler, **vars(options))