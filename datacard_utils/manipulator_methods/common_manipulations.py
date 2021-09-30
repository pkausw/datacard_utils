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

from .nuisance_manipulator import NuisanceManipulator
from .process_manipulator import ProcessManipulator

class CommonManipulations(object):
    __choices = "rateParams lnN GoF old_lnN old_rateParams".split()
    def __init__(self):
        super(CommonManipulations, self).__init__()
        self.__to_freeze = """kfactor_wjets kfactor_zjets
                                .*bgscale_MCCR.*""".split()

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
                "lumi_13TeV_2016": 1.01,
                "lumi_13TeV_correlated" : 1.006,
            },
            "2017": {
                "lumi_13TeV_2017": 1.020,
                "lumi_13TeV_correlated" : 1.009,
                "lumi_13TeV_1718" : 1.006,
            },
            "2018": {
                "lumi_13TeV_2018": 1.015,
                "lumi_13TeV_correlated" : 1.020,
                "lumi_13TeV_1718" : 1.002,
            }
        }

        self.__lnN_uncertainties = {
            "tHq.*": {
                "QCDscale_tHq": (0.851,1.065),
                "pdf_Higgs_tHq": 1.037
            },
            "tHW.*": {
                "QCDscale_tHW": (0.933,1.049),
                "pdf_Higgs_tHW": 1.063
            },
            "ttH.*": {
                "QCDscale_ttH": (0.908,1.058),
                "pdf_Higgs_ttH": 1.036
            },
            "ttbb.*|ttcc.*|ttlf.*":{
                "QCDscale_ttbar": (1-0.035,1+0.024),
                "pdf_gg": 1.042
            },
            "singlet.*": {
                "QCDscale_singlet": (0.979,1.031),
                "pdf_qg": 1.028
            },
            "wjets.*": {
                "QCDscale_V": 1.038,
                "pdf_qqbar": (0.996,1.008)
            },
            "zjets.*": {
                "QCDscale_V": 1.02,
                "pdf_qqbar": 1.002
            },
            "ttbarW.*": {
                "QCDscale_ttbar": (1-0.164, 1+0.255),
                "pdf_qqbar": 1.036
            },
            "ttbarZ.*": {
                "QCDscale_ttbar": (1-0.093, 1+0.081),
                "pdf_gg": 1.035
            },
            "diboson.*": {
                "QCDscale_VV": 1.03,
                "pdf_qqbar" : 1.05
            }
        }

        self.manipulator = NuisanceManipulator()
        self.__mode = "GoF"
        
    @classmethod
    def bgnorm_mode_choices(cls):
        return cls.__choices
    @property
    def bgnorm_mode(self):
        return self.__mode
    @bgnorm_mode.setter
    def bgnorm_mode(self, value):
        if value in self.__choices:
            self.__mode = value
        else:
            print("Could not set mode to add bgnorm uncertainties!")
            print(("Current choices are: '{}'"\
                    .format(", ".join(self.__choices))))


    def freeze_nuisances(self, harvester):
        harvester.SetFlag("filters-use-regex", True)
        for par in self.__to_freeze:
            systs = harvester.cp().syst_name([par]).syst_name_set()
            for p in systs:
                harvester.GetParameter(p).set_frozen(True)

    def add_lumi_uncertainties(self, harvester):
        eras = harvester.era_set()

        if len(eras) == 0:
            raise ValueError("Harvester instance does not contain an era!")
        # elif len(eras) == 1:
        #     lumi_uncertainties = self.__lumi_uncertainties
        else:
            lumi_uncertainties = self.__lumi_uncertainties_all_years
        
        uncertainties = harvester.syst_name_set()
        uncertainties = [x for x in uncertainties if x.startswith("lumi")]
        harvester.syst_name(uncertainties, False)

        for e in eras:
            uncertainties = lumi_uncertainties.get(e, {})
            for unc in uncertainties:
                value = uncertainties[unc]
                # exclude data_CR template from FH here
                print(harvester.cp().process(["^(?!(data_.*)).*"]).process_set())
                harvester.cp().process(["^(?!(data_.*)).*"]).era([e])\
                    .AddSyst(harvester, unc, "lnN", ch.SystMap()(value))
            if len(uncertainties) == 0:
                print(("WARNING: did not find uncertainties for era '{}'"\
                        .format(e)))
    
    def remove_see_saw(self, harvester):

        self.manipulator.to_remove = {
            "CMS_ttHbb_FSR_ttbb": "ttcc ttlf".split(),
            "CMS_ttHbb_FSR_ttcc": "ttbb ttlf".split(),
            "CMS_ttHbb_FSR_ttlf": "ttbb ttcc".split(),
            "CMS_ttHbb_ISR_ttbb": "ttcc ttlf".split(),
            "CMS_ttHbb_ISR_ttcc": "ttbb ttlf".split(),
            "CMS_ttHbb_ISR_ttlf": "ttbb ttcc".split(),
            "CMS_ttHbb_scaleMuR_ttbbNLO": "ttcc ttlf".split(),
            "CMS_ttHbb_scaleMuR": ["ttbb"],
            "CMS_ttHbb_scaleMuF_ttbbNLO": "ttcc ttlf".split(),
            "CMS_ttHbb_scaleMuF": ["ttbb"],
        }
        self.manipulator.remove_nuisances_from_procs(harvester)

    def add_bgnorm_uncertainties(self, harvester):
        uncertainties = harvester.syst_name_set()
        uncertainties = [".*bgnorm_tt.*"]
        if len(uncertainties) > 0:
            harvester.syst_name(uncertainties, False)
        lnN_processes = []
        rateParam_processes = []
        if self.__mode == "lnN":
            lnN_processes = "ttcc ttbb".split()
            rateParams_processes = []
        elif self.__mode == "rateParams":
            rateParams_processes = "ttcc ttbb".split()
            lnN_processes = []
            
        elif self.__mode == "GoF":
            rateParams_processes = ["ttbb"]
            lnN_processes = ["ttcc"]
            
        elif self.__mode == "old_lnN":
            # apply 50% lnN Parameters to ttcc, ttb, tt2b, ttbb and their counter parts
            # in the FH CR
            lnN_processes = "ttcc ttb tt2b ttbb".split()
            rateParams_processes = []

        elif self.__mode == "old_rateParams":
            # apply 50% lnN Parameters to ttcc, ttb, tt2b, ttbb and their counter parts
            # in the FH CR
            rateParams_processes = "ttcc ttb tt2b ttbb".split()
            lnN_processes = []
        elif self.__mode == "old_GOF":
            rateParams_processes = "ttb tt2b ttbb".split()
            lnN_processes = ["ttcc"]
        
        # centrally add 5FS processes here
        lnN_processes += [x+"_5FS" for x in lnN_processes]
        rateParams_processes += [x+"_5FS" for x in rateParams_processes]
        # apply all lnN parameters here
        for proc in lnN_processes:
            cr = proc + "_CR"
            parname = "CMS_ttHbb_bgnorm_{}".format(proc)
            harvester.cp().process([proc, cr])\
                        .AddSyst(harvester, parname, "lnN", ch.SystMap()(1.5))
        
        # apply all rateParams here
        for proc in rateParams_processes:
            cr = proc + "_CR"
            parname = "CMS_ttHbb_bgnorm_{}".format(proc)
            harvester.cp().process([proc, cr])\
                    .AddSyst(harvester, parname, "rateParam", ch.SystMap()(1.))
            if parname in harvester.cp().syst_type(["rateParam"]).syst_name_set():
                harvester.GetParameter(parname).set_range(-5, 5)
        # 
    
    def add_lnN_uncertainties(self, harvester):
        harvester.SetFlag("filters-use-regex", True)

        for proc in self.__lnN_uncertainties:
            for unc in self.__lnN_uncertainties[proc]:
                #first, drop existing uncertainties
                print(("removing '{}' from '{}'".format(unc, proc)))
                self.manipulator.to_remove = {
                    unc : [proc]
                }
                self.manipulator.remove_nuisances_from_procs(harvester)
                # now add new uncertainties
                print(("adding uncertainty '{}' to '{}'"\
                    .format(unc, proc)))
                value = self.__lnN_uncertainties[proc][unc]
                harvester.cp().process([proc])\
                    .AddSyst(harvester, unc, "lnN", ch.SystMap()(value))


    def remove_5FS_prediction(self, harvester):
        process_manipulator = ProcessManipulator()
        process_manipulator.drop_all_processes(harvester = harvester,
                                                to_drop = ["ttbb_5FS"])

    def decorrelate_btags(self, harvester):
        wildcard = "CMS_btag_(lf|hf|cferr1|cferr2)"

        parameters = harvester.cp().syst_name([wildcard]).syst_name_set()
        print("="*130)
        
        for p in parameters:
            print("decorrelating parameter '{}' in year '{}'".format(p, "2016"))
            harvester.cp().era(["2016"]).\
                RenameSystematic(harvester, p, "_".join([p, "2016"]))
            print("decorrelating parameter '{}' in year '{}'".format(p, "2017, 2018"))
            harvester.cp().era(["2017","2018"]).\
                RenameSystematic(harvester, p, "_".join([p, "1718"]))

        # make sure that all cferr uncertainties are correlated across channels
        wildcard = "CMS_btag_cferr.?_(2016|1718)_FH"
        fh_harvester = harvester.cp().bin([".*fh.*|.*FH.*"])
        parameters = fh_harvester.cp().syst_name([wildcard]).syst_name_set()
        for p in parameters:
            new_parname = p.replace("_FH", "")
            print("renaming parameter '{}' to '{}'".format(p, new_parname))
            fh_harvester.\
                RenameSystematic(harvester, p, new_parname)

    def apply_common_manipulations(self, harvester):
        harvester.SetFlag("filters-use-regex", True)

        self.freeze_nuisances(harvester)
        self.add_lumi_uncertainties(harvester)
        self.remove_see_saw(harvester)
        self.add_bgnorm_uncertainties(harvester)
        process_set = harvester.process_set()
        if all(x in process_set for x in "ttbb ttbb_5FS".split()):
            self.remove_5FS_prediction(harvester)
        self.add_lnN_uncertainties(harvester)
        harvester.SetAutoMCStats(harvester, 10)
        harvester.FilterSysts(lambda x: (x.value_u() == 0 or x.value_d() == 0)\
                                 and any(x.type == t for t in "shape shape? lnN".split()))
        self.decorrelate_btags(harvester)


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
