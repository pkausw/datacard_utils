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

class CommonManipulations(object):

    def __init__(self):
        super(CommonManipulations, self).__init__()
        self.__to_freeze = """kfactor_wjets kfactor_zjets
                                CMS_ttHbb_bgscale_MCCR""".split()

        self.__lumi_uncertainties={
            "2016": {
                "lumi_13TeV_2016" : 1.025 
                },
            "2017": {
                "lumi_13TeV_2017" : 1.023 
                },
            "2016": {
                "lumi_13TeV_2016" : 1.025 
                },
        }

        self.__lumi_uncertainties_all_years={
            "2016": {
                "lumi_13TeV_2016": 1.022,
                "lumi_13TeV_XY" : 1.009,
                "lumi_13TeV_BBD" : 1.004,
                "lumi_13TeV_DB": 1.005,
                "lumi_13TeV_GS": 1.004
            },
            "2017": {
                "lumi_13TeV_2017": 1.020,
                "lumi_13TeV_XY" : 1.008,
                "lumi_13TeV_LS" : 1.003,
                "lumi_13TeV_BBD" : 1.004,
                "lumi_13TeV_DB": 1.005,
                "lumi_13TeV_BCC": 1.003,
                "lumi_13TeV_GS": 1.001
            },
            "2018": {
                "lumi_13TeV_2018": 1.015,
                "lumi_13TeV_XY" : 1.020,
                "lumi_13TeV_LS" : 1.002,
                "lumi_13TeV_BCC": 1.002,
            }
        }


    def freeze_nuisances(self, harvester):
        systs = harvester.syst_name_set()
        for p in self.__to_freeze:
            if p in systs:
                harvester.GetParameter(p).set_frozen(True)

    def add_lumi_uncertainties(self, harvester):
        eras = harvester.era_set()

        if len(eras) == 0:
            raise ValueError("Harvester instance does not contain an era!")
        elif len(eras) == 1:
            lumi_uncertainties = self.__lumi_uncertainties
        else:
            lumi_uncertainties = self.__lumi_uncertainties_all_years
        
        uncertainties = harvester.syst_name_set()
        uncertainties = [x for x in uncertainties if x.startswith("lumi")]
        harvester.syst_name(uncertainties, False)

        for e in eras:
            uncertainties = lumi_uncertainties.get(e, {})
            for unc in uncertainties:
                value = uncertainties[unc]
                harvester.cp().era([e])\
                    .AddSyst(harvester, unc, "lnN", ch.SystMap()(value))
            if len(uncertainties) == 0:
                print("WARNING: did not find uncertainties for era '{}'"\
                        .format(e))
        
    def apply_common_manipulations(self, harvester):
        self.freeze_nuisances(harvester)
        self.add_lumi_uncertainties(harvester)




def main(**kwargs):

    harvester = ch.CombineHarvester()
    harvester.SetFlag("allow-missing-shapes", False)
    harvester.SetFlag("workspaces-use-clone", True)

    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    
    common_manipulations = CommonManipulations()
    common_manipulations.apply_common_manipulations(harvester)
       
    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    basename = os.path.basename(cardpath)
    prefix = kwargs.get("prefix", None)
    basename = "{}_{}".format(prefix, basename) if prefix else basename
    newpath = os.path.join(outdir, "datacards", basename)
    output_rootfile = kwargs.get("output_rootpath")
    if output_rootfile is None:
        output_rootfile = ".".join(basename.split(".")[:-1] + ["root"])
    output_rootfile = "{}_{}".format(prefix, output_rootfile) \
                        if prefix else output_rootfile
    output_rootfile = os.path.join(outdir, "rootfiles", output_rootfile)

    # harvester.WriteDatacard(newpath)
    writer = ch.CardWriter(newpath, output_rootfile)
    writer.SetWildcardMasses([])
    writer.SetVerbosity(1)
    writer.WriteCards("cmb", harvester)


def parse_arguments():
    usage = " ".join("""
    This tool combines multiple manipulator methods.
    Current list of implemented methods:
    apply_validation, group_manipulator, nuisance_manipulator, 
    rebin_distributions, scale_higgs_mass. 
    This tool employs functions from the CombineHarvester package. 
    Please make sure that you have installed it!

    The script will first scale the higgs mass and will then proceed
    with other manipulations.
    """.split())

    usage += """

    python %prog [options]
    """
    parser = OptionParser(usage = usage)
    parser.add_option("-i", "--input",
                        help = " ".join(
                            """
                            define groups of inputs. The format should be like
                            'SCHEME:wildcard/to/input/files*.txt'
                            """.split()
                        ),
                        dest = "input_groups",
                        metavar = "SCHEME:path/to/datacard",
                        type = "str",
                        action = "append"
                    )

    parser.add_option("-o", "--outputrootfile",
                        help = " ".join(
                            """
                            use this root file name for the varied
                            inputs. Default is the original root file
                            name
                            """.split()
                        ),
                        dest = "output_rootpath",
                        metavar = "path/for/output",
                        # default = ".",
                        type = "str"
                    )
    

    optional_group = OptionGroup(parser, "optional options")
    optional_group.add_option("--directory",
                        help = " ".join(
                            """
                            save new datacards in this directory.
                            Default = "."
                            """.split()
                        ),
                        dest = "outdir",
                        metavar = "path/for/output",
                        default = ".",
                        type = "str"
                    )
    optional_group.add_option("-p", "--prefix",
                        help = " ".join(
                            """
                            prepend this string to the datacard names.
                            Output will have format 'PREFIX_DATACARDNAME'
                            """.split()
                        ),
                        dest = "prefix",
                        type = "str"
                    )
    
    parser.add_option_group(optional_group)
    options, files = parser.parse_args()

    cardpath = options.datacard
    if not cardpath:
        parser.error("You need to provide the path to a datacard!")
    elif not os.path.exists(cardpath):
        parser.error("Could not find datacard in '{}'".format(cardpath))
    
    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(**vars(options))