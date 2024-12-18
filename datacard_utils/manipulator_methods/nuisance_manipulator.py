from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import ROOT
import json
from fnmatch import filter
# from six.moves import filter
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

# from common_manipulations import CommonManipulations


class NuisanceManipulator(object):

    def __init__(self):
        self.to_remove = {}
        self.__debug = 0
    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        self.__debug = value
    def matching_proc(self, p,s):
        return ((p.bin()==s.bin()) and (p.process()==s.process()) \
                and (p.signal()==s.signal()) and \
                (p.analysis()==s.analysis()) and (p.era()==s.era()) \
                and (p.channel()==s.channel()) and (p.bin_id()==s.bin_id()) \
                and (p.mass()==s.mass()))

    def copy_and_rename(self, syst, suffix=None, bin=None, era=None):
        copy_func = getattr(syst, "Copy", None)
        if not callable(copy_func):
            msg = " ".join("""This version of CombineHarvester does not include the 
                    ch.Systematic.Copy function, cannot copy systematics!
                    """.split())
            raise NotImplementedError(msg)
        new = syst.Copy()
        name = new.name()
        if suffix:
            name = "_".join([name, suffix])
        new.set_name(name)

        # overwrite nuisance parameter information if needed
        if era:
            new.set_era(era)
        if bin:
            new.set_bin(bin)


        return new

    def partially_decorrelate_nuisances(
        self,
        harvester,
        channel_suffixes,
        problematic_nps,
        processes,
        syst_types=["lnN", "shape"],
    ):
        if "rateParam" in syst_types:
            raise ValueError("You cannot partially decorrelate rateParams! Please use the add function.")
        for c in channel_suffixes:
            suffix = channel_suffixes[c]
            sub_harvester = harvester.cp().bin([c])
            syst_harvester = sub_harvester.cp().syst_type(
                syst_types).syst_name(problematic_nps)
            to_decorrelate = syst_harvester.syst_name_set()
    #       for param in to_decorrelate:
    #            these_pars = filter(harvester_params, param)
            bins = sub_harvester.cp().bin_set()
            
            if self.debug >= 3:
                print("partially decorrelating bin '{}'".format(bins))
                print("\tprocesses: '{}'".format(", ".join(processes)))
                print("\tsystematics: '{}'".format(to_decorrelate))
            syst_harvester.cp().bin(bins).process(processes).ForEachSyst(
                lambda syst: harvester.InsertSystematic(self.copy_and_rename(syst, suffix))
            )

    def add_nuisances(self, harvester, nuisance_dictionary):
        for parname in nuisance_dictionary:
            this_dict = nuisance_dictionary[parname]
            syst_type = this_dict.get("type", "lnN")
            value = this_dict.get("value", 1.5)
            processes = this_dict.get("processes", [])
            channels = this_dict.get("channels", [])
            harvester.cp().bin(channels).process(processes)\
                            .AddSyst(harvester, parname, syst_type, ch.SystMap()(value))
            if parname in harvester.cp().syst_type(["rateParam"]).syst_name_set():
                harvester.GetParameter(parname).set_range(-5, 5)


    def drop_syst(self, harvester,proc, parameter_to_drop):
        # print("dropping sys {}".format(parameter_to_drop))
        harvester.FilterSysts(lambda syst: self.matching_proc(proc, syst) and syst.name() == parameter_to_drop)

    def remove_nuisances_from_procs(self, harvester, bins = None, channels = [".*"], eras = [".*"]):
        harvester.SetFlag("filters-use-regex", True)
        harvester_params = harvester.syst_name_set()
        if not isinstance(bins, list):
            bins = harvester.bin_set()
        # print(harvester_params)
        if self.debug >= 3: 
            print("will remove nuisances based on following dictionary")
            print((json.dumps(self.to_remove, indent=4)))
        for wildcard_par in self.to_remove:
            print(wildcard_par)
            procs = self.to_remove[wildcard_par]
            procs = [str(x) for x in procs]
            these_pars = harvester.cp().process(procs).syst_name([str(wildcard_par)]).syst_name_set()
            print(these_pars)
            for par in these_pars:
                # print(self.__debug)
                if self.__debug >= 3:
                    print(par)
                    print(procs)
                    print(bins)
                    print(("removing param '{}' for procs '{}' in bins '{}'".\
                        format(par, ", ".join(procs), ", ".join(bins))))
                harvester.cp().bin(bins).channel(channels).era(eras).process(procs).\
                    ForEachProc(lambda proc: self.drop_syst(harvester,proc, par))



def main(*args, **kwargs):

    harvester = ch.CombineHarvester()
    #harvester.SetFlag("check-negative-bins-on-import", False)
    harvester.SetFlag("allow-missing-shapes", False)
    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "ttH", "13TeV", "")
    # for f in args:
    #     print(f)
    #     harvester.ParseDatacard(f, "ttH")

    nuisance_manipulator = NuisanceManipulator()

    # harvester.PrintAll()
    nuisance_manipulator.to_remove = {
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
    nuisance_manipulator.remove_nuisances_from_procs(harvester)
    
    # if c == "ljets":
    #     pnames = []
    #     harvester.cp().bin(current_bins)\
    #         .ForEachProc(lambda x: pnames.append(x.process()))
    #     pnames = list(set(pnames))
    #     for p in pnames:
    #         harvester.cp().bin(current_bins)\
    #         .process([p])\
    #         .RenameSystematic(harvester, new_parname, "_".join([new_parname, p]))
    #         if p == "ttlf":
    #             for b in current_bins:
    #                 ultisplit = "_".join([new_parname, p, b])
    #                 harvester.cp().bin([b])\
    #                 .process([p])\
    #                 .RenameSystematic(harvester, "_".join([new_parname, p]), ultisplit)
    harvester.PrintSysts()
    # common_manipulations = CommonManipulations()
    # common_manipulations.apply_common_manipulations(harvester)
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
    output_rootfile = os.path.join(outdir, output_rootfile)

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

    # cardpath = options.datacard
    # if not cardpath:
    #     parser.error("You need to provide the path to a datacard!")
    # elif not os.path.exists(cardpath):
    #     parser.error("Could not find datacard in '{}'".format(cardpath))
    
    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))