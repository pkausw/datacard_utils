import os
import sys
import ROOT
import json
cmssw_base = os.environ["CMSSW_BASE"]
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
if not os.path.exists(cmssw_base):
    raise ValueError("Could not find CMSSW base!")

try:
    import CombineHarvester.CombineTools.ch as ch
except:
    msg = "".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)


from optparse import OptionParser, OptionGroup
from subprocess import call
from nuisance_manipulator import NuisanceManipulator

ROOT.TH1.AddDirectory(False)


class STXSModifications(object):

    def __init__(self):
        self.__migration_dict = {}
        self.__debug = 0
        self.removal_dict = {
            "*FSR_ttH" : [".*"],
            "*ISR_ttH" : [".*"],
            "*MuF_ttH" : [".*"],
            "*MuR_ttH" : [".*"],
            "QCDscale_ttH": [".*"] 
        }
        self.setup_default_migrations()

        
    
    @property
    def verbosity(self):
        return self.__debug
    
    @verbosity.setter
    def verbosity(self, val):
        try:
            verbo_level = int(val)
            print("setting verbosity to level '{}'".format(verbo_level))
            self.__debug = verbo_level
        except:
            print("Could not convert value '{}' to integer!".format(val))
            print("Verbosity level will stay at '{}'".format(self.verbosity))

    @property
    def migration_dict(self):
        return self.__migration_dict
    @migration_dict.setter
    def migration_dict(self, input_dict):
        if isinstance(input_dict, dict):
            if self.verbosity >= 10:
                print("new migration dictionary:")
                print(json.dumps(input_dict, indent=4))
            self.__migration_dict = input_dict
        else:
            s = " ".join("""Error: input for removal_dict 
                            must be a dictionary of the form
                            {
                                migration_parameter : {
                                    "process" : value
                                }
                            }
                        """.split())
            raise ValueError(s)

    @property
    def removal_dict(self):
        return self.__removal_dict
    @removal_dict.setter
    def removal_dict(self, input_dict):
        if isinstance(input_dict, dict):
            if self.verbosity >= 10:
                print("new removal dictionary:")
                print(json.dumps(input_dict, indent=4))
            self.__removal_dict = input_dict
        else:
            s = " ".join("""Error: input for removal_dict 
                            must be a dictionary of the form
                            {
                                param_to_remove : [list_of_processes]
                            }
                        """.split())
            raise ValueError(s)
    
    def setup_default_migrations(self):
        scheme = "default_k0p7"
        thisdir = os.path.realpath(os.path.dirname(__file__))
        data_dir = os.path.join(thisdir, "..", "data")
        jsonpath = os.path.join(data_dir, "stxs_ttH_migUncs.json")
        if os.path.exists(jsonpath):
            with open(jsonpath) as f:
                full_migration_dict = json.load(f)
                self.migration_dict = full_migration_dict.get(scheme, {})
        else:
            s = " ".join("""WARNING: unable to load default 
                            migration uncertainties from path
                            '{}'""".format(jsonpath).split())
            print(s)


    def remove_signal_theory_nuisances(self, harvester):
        np_manipulator = NuisanceManipulator()
        np_manipulator.to_remove = self.removal_dict

        np_manipulator.remove_nuisances_from_procs(harvester)

    def add_migration_nuisances(self, harvester):
        for unc in self.migration_dict:
            unc_dict = self.migration_dict[unc]
            for process in unc_dict:
                value = float(unc_dict[process])
                if value == 0:
                    continue
                proc_wildcard = str(process+".*")
                print("Adding uncertainty '{}' to processes '{}'"\
                        .format(unc, proc_wildcard))
                harvester.cp().process([proc_wildcard])\
                    .AddSyst(harvester, str(unc), "lnN", ch.SystMap()(round(1+value, 2)))

    def do_stxs_modifications(self, harvester):
        harvester.SetFlag("filters-use-regex", True)
        self.remove_signal_theory_nuisances(harvester)

        self.add_migration_nuisances(harvester)

def main(**kwargs):

    harvester = ch.CombineHarvester()
    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "test", "13TeV", "")
    

    # harvester.PrintAll()

    jsonpath = kwargs.get("jsonpath")
    interface = STXSModifications()
    interface.jsonpath = jsonpath
    
    interface.do_stxs_modifications(harvester)

    

    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    basename = os.path.basename(cardpath)
    prefix = kwargs.get("prefix", None)
    basename = "{}_{}".format(prefix, basename) if prefix else basename
    newpath = os.path.join(outdir, "datacards", basename)
    output_rootfile = kwargs.get("output_rootpath")
    output_rootfile = "{}_{}".format(prefix, output_rootfile) \
                        if prefix else output_rootfile
    output_rootfile = os.path.join(outdir, output_rootfile)
    print(newpath)
    print(output_rootfile)
    # harvester.WriteDatacard(newpath)
    writer = ch.CardWriter(newpath, output_rootfile)
    writer.SetWildcardMasses([])
    writer.SetVerbosity(1)
    writer.WriteCards("cmb", harvester)


def parse_arguments():
    usage = " ".join("""
    Tool to change inputs for combine based on output of
    'ValidateDatacards.py'. This tool employs functions
    from the CombineHarvester package. Please make sure
    that you have installed it!
    """.split())
    parser = OptionParser(usage = usage)
    parser.add_option("-d", "--datacard",
                        help = " ".join(
                            """
                            path to datacard to change
                            """.split()
                        ),
                        dest = "datacard",
                        metavar = "path/to/datacard",
                        type = "str"
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
                        default = "all_shapes.root",
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
