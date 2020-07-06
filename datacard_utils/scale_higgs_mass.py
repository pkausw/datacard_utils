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

ROOT.TH1.AddDirectory(False)
try:
    print("importing CombineHarvester")
    import CombineHarvester.CombineTools.ch as ch
    print("done")
except:
    msg = " ".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)


def GenerateScalingLine(objects, ws_name, path, source, wildcard):
    lines = []
    for e in objects:
        line = " ".join([e, "extArg", ":".join(["\\"+path, ws_name])])
        line = "\n"+line
        lines.append(line)
        baseval = source.function(e).getVal()
        new_parname = e+"_rescale"
        line=' '.join([new_parname,'rateParam',"*",wildcard.format(e.replace("_13TeV", "")),"@0/%f"%baseval,e])
        lines.append(line)
        # line = "nuisance edit freeze {} ifexists".format(new_parname)
        # lines.append(line)
    return lines
        

def MassScaling(productions, decays, basemass):
    ''' return a list of fully formed rateParameter with the xs*br scaling over the 125'''
    xs_path = '$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root'
    br_path = '$CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root'
    fXS=ROOT.TFile.Open(xs_path)
    fBR=ROOT.TFile.Open(br_path)
    
    wBR=fBR.Get("br")
    wXS=fXS.Get("xs_13TeV")
    
    wBR.var("MH").setVal(basemass)
    wXS.var("MH").setVal(basemass)
    xs_procs=[x+"_13TeV" for x in productions]
    lines = GenerateScalingLine( objects = xs_procs, ws_name = "xs_13TeV",
                                 path = xs_path, source = wXS, wildcard = "{}_*")
    lines += GenerateScalingLine( objects = decays, ws_name = "br",
                                 path = br_path, source = wBR, wildcard = "*_{}")
    return lines


def main(*args, **kwargs):
    processes = kwargs.get("procs", [])
    basemass = kwargs.get("base_mass", 125)
    productions = []
    decays = []
    for p in processes:
        if "_" in p:
            prod, decay = p.split("_")
            productions.append(prod)
            decays.append(decay)
    
    productions = list(set(productions))
    decays = list(set(decays))
    
    lines = MassScaling(productions = productions, decays = decays, 
                        basemass = basemass)
    print("\n".join(lines))
    apply = kwargs.get("apply", False)
    if apply:
        for f in args:
            if not os.path.exists(f):
                print("ERROR: file '{}' does not exist".format(f))
                continue
            for l in lines:
                cmd = 'echo "{}" >> {}'.format(l, f)
                print(cmd)
                call([cmd], shell = True)

def parse_arguments():
    procs = [   'ttH_hbb',
                'ttH_hcc',
                'ttH_htt',
                'ttH_hgg',
                'ttH_hgluglu',
                'ttH_hww',
                'ttH_hzz',
                'ttH_hzg'
            ]
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
    options, files = parse_arguments()
    main(*files, **vars(options))