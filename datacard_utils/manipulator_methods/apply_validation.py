from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import ROOT
import json
import numpy as np
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
from tqdm import tqdm
from .nuisance_manipulator import NuisanceManipulator
from .process_manipulator import ProcessManipulator

ROOT.TH1.AddDirectory(False)

class ValidationInterface(ProcessManipulator):

    def __init__(self):
        self.__jsonpath = None
        self.__debug = 0
        self.__validation_dict = None
        self.__do_smallShapeEff = True
        self.__do_smallSigCut = True
        self.__remove_empty_shapes = True
        self.__cmd_template = " ".join("ValidateDatacards.py -p 3 \
            --mass 125.38 --jsonFile {outpath} {input_path}".split())
        self.__np_manipulator = NuisanceManipulator()
        self.__bkg_threshold = 0.001
        self.__do_smallBkgCut = True
        self.__symmetrize = False
        self.__channels_to_combine = []
        
    
    @property
    def verbosity(self):
        return self.__debug
    
    @verbosity.setter
    def verbosity(self, val):
        try:
            verbo_level = int(val)
            print(("setting verbosity to level '{}'".format(verbo_level)))
            self.__debug = verbo_level
        except:
            print(("Could not convert value '{}' to integer!".format(val)))
            print(("Verbosity level will stay at '{}'".format(self.verbosity)))

    @property
    def channels_to_combine(self):
        return self.__channels_to_combine

    @channels_to_combine.setter
    def channels_to_combine(self, varlist):
        if not isinstance(varlist, (list, type(None))):
            raise ValueError("'channels_to_combine' must be a list of channels or None!")
        else:
            self.__channels_to_combine = varlist

    @property
    def jsonpath(self):
        return self.__jsonpath
    @jsonpath.setter
    def jsonpath(self, path):
        if isinstance(path, str):
            if os.path.exists(path):
                self.__jsonpath = path
                with open(self.__jsonpath) as f:
                    self.__validation_dict = json.load(f)
                if self.verbosity >= 99:
                    s = json.dumps(self.__validation_dict, 
                                indent = 4, separators = (",", ":"))
                    print(s)

            else:
                print(("ERROR: file '{}' does not exist!".format(path)))
        else:
            print("ERROR: path to validation json has to be a string!")
    
    @property
    def remove_small_signals(self):
        return self.__do_smallSigCut

    @remove_small_signals.setter
    def remove_small_signals(self, val):
        if isinstance(val, bool):
            if val:
                print("Will drop small signals")
            else:
                print("Will keep small signals")
            self.__do_smallSigCut = val
        else:
            print(("Could not set 'remove_small_signals' to '{}'".format(val)))
            print("Value has to be bool")

    @property
    def background_threshold(self):
        return self.__bkg_threshold
    @background_threshold.setter
    def background_threshold(self, value):
        try:
            fvalue = float(value)
            self.__bkg_threshold = fvalue
        except:
            print(("could not convert '{}' to float!".format(fvalue)))
            print(("Background threshold will stay at '{}'"\
                    .format(self.background_threshold)))

    @property
    def remove_small_backgrounds(self):
        return self.__do_smallBkgCut

    @remove_small_backgrounds.setter
    def remove_small_backgrounds(self, val):
        if isinstance(val, bool):
            if val:
                print("Will drop small backgrounds")
            else:
                print("Will keep small backgrounds")
            self.__do_smallBkgCut = val
        else:
            print(("Could not set 'remove_small_backgrounds' to '{}'".format(val)))
            print("Value has to be bool")

    @property
    def validation_dict(self):
        return self.__validation_dict

    @property
    def symmetrize(self):
        return self.__symmetrize

    @symmetrize.setter
    def symmetrize(self, val):
        if not isinstance(val, bool):
            raise ValueError("Input for symmetrize must be boolean!")
        self.__symmetrize = val
    
    
    def fill_syst_value_array(self, syst, val_array, norm_array = None):
        
        result_vector = [syst.value_u(), syst.value_d()]
        val_array.append(result_vector)
        if isinstance(norm_array, list):
            norm_array.append([syst.scale()])


    def load_rate_values(self, harvester, uncertainty, channel, process):
        vals = []
        if len(channel) >1:
            val_list = []
            norm_list = []
            real_channels = harvester.cp().process([str(process)]).\
                                bin([str(x) for x in channel]).bin_set()
            for b in real_channels:
                harvester.cp().bin([str(b)]).process([str(process)]).\
                    syst_type(["shape"]).syst_name([str(uncertainty)]).\
                        ForEachSyst(lambda x: self.fill_syst_value_array(
                            x, 
                            val_list
                        ))
                harvester.cp().bin([str(b)]).process([str(process)]).\
                    syst_type(["shape"]).syst_name([str(uncertainty)]).\
                        ForEachProc(lambda p: norm_list.append([p.rate()]))

            if len(val_list) > 0:
                # calculate the average lnN factors
                val_array = np.array(val_list, dtype = "f")
                norm_array = np.array(norm_list, dtype = "f")
                summed_values = np.sum(val_array * norm_array, axis=0, dtype = "f")
                norm_sum = np.sum(norm_array, axis=0, dtype = "f")
                vals = [(summed_values/norm_sum).tolist()]

        else:
            harvester.cp().bin(channel).process([str(process)]).\
                syst_type(["shape"]).syst_name([str(uncertainty)]).\
                        ForEachSyst(lambda x: self.fill_syst_value_array(
                            x, 
                            vals
                        ))
        # print(vals)
        if len(vals) > 0:
            vals = vals[0]
            vals = [round(x, 3) for x in vals]
            val_u = vals[0]
            val_d = vals[1]
            if all(v <= 1. for v in vals):
                if self.verbosity > 10:
                    print("Found purely down fluctuation!")
                if self.symmetrize:
                    vals[0] = 1.
                    vals[1] = (val_u + val_d)/2.
                    vals[0] = 1./vals[1]
            elif all(v >= 1. for v in vals):
                if self.verbosity > 10:
                    print("Found purely up fluctuation!")
                
                if self.symmetrize:
                    vals[1] = 1.
                    vals[0] = (val_u + val_d)/2.
                    vals[1] = 1./vals[0]
            elif not val_u == 1. and val_d == 1.:
                vals[1] = 1./val_u
            elif not val_d == 1. and val_u == 1.:
                vals[0] = 1./val_d
        return vals


    def ratify_uncertainty_in_channels(
        self,
        harvester,
        dict_unc,
        unc,
        eras = [".*"],
        channels = [".*"],
        ):
        era_harvester = harvester.cp().era(eras)
        processes = []
        for channel in channels:
            processes = list(set(processes + list(dict_unc[channel])))

        pbar_proc = tqdm(processes)
        for process in pbar_proc:
            pbar_proc.set_description("Processing process '{}'".format(process))
            if self.verbosity > 5:
                print(("\t\tProcess: {}".format(process)))
            harvester_processes = era_harvester.cp().bin(channels).process_set()
            if not process in harvester_processes:
                if self.verbosity > 5:
                    print((" ".join("""Process '{}' is not part of the 
                                        current harvester instance, 
                                        skipping
                                    """.format(process)
                                    )
                            )
                        )
                continue
            if self.verbosity > 20:
                print("="*130)
                print("current list of nuisances")
                era_harvester.cp().bin(channels).process([str(process)]).PrintSysts()
                print("="*130)
            vals = self.load_rate_values(harvester = era_harvester,
                                        uncertainty = unc,
                                        channel = channels,
                                        process = process)
            # print(vals)
            # harvester.bin([str(channel)]).process([str(process)]).syst_name([str(unc)], False)
            # harvester.PrintAll()
            if len(vals) > 0:
                if any(abs(1.-x)>= 1e-3 for x in vals):
                    harvester.cp().era(eras).\
                        bin(channels).\
                        process([str(process)]).\
                        syst_name([str(unc)]).\
                        syst_type(["shape"]).\
                        ForEachSyst(lambda x: x.set_type("lnN"))

                    harvester.cp().era(eras).\
                        bin(channels).\
                        process([str(process)]).\
                        syst_name([str(unc)]).\
                        syst_type(["lnN"]).\
                        ForEachSyst(lambda x: x.set_value_u(vals[0]))
                    harvester.cp().era(eras).\
                        bin(channels).\
                        process([str(process)]).\
                        syst_name([str(unc)]).\
                        syst_type(["lnN"]).\
                        ForEachSyst(lambda x: x.set_value_d(vals[1]))
                else:
                    print("Detected uncertainty with less than 0.1% yield effect!")
                    print(("will drop '{}' for process '({})/{}'"\
                            .format(unc, ", ".join(channels), process)))
                    # self.__np_manipulator.debug = 3
                    self.__np_manipulator.to_remove = {unc: [str(process)]}
                    self.__np_manipulator.remove_nuisances_from_procs(
                                            harvester = harvester,
                                            bins = channels,
                                            eras = eras)
            else:
                print(("="*130))
                print(("Could not find uncertainty '{}' in '({})/{}'".\
                        format(unc, ", ".join(channels), process)))


    def ratify(self, harvester, change_dict, eras = [".*"]):
        
        harvester_channels = harvester.cp().era(eras).bin_set()
        pbar_unc = tqdm(change_dict)
        for unc in pbar_unc:
            pbar_unc.set_description("Processing uncertainty '{}'".format(unc))
            if self.verbosity > 5:
                print(("Uncertainty: {}".format(unc)))
            dict_unc = change_dict[unc]
            channels_to_change = dict_unc.keys()
            already_changed_channels = []
            pbar_combined_channels = tqdm(self.channels_to_combine or [])
            for channel_wildcard in pbar_combined_channels:
                # evaluate real channel names
                channel_wildcard = str(channel_wildcard)
                channels = harvester.cp().bin([channel_wildcard]).bin_set()
                pbar_combined_channels.set_description("Consider combination of '{}'".format(", ".join(channels)))

                if not all(x in channels_to_change for x in channels):
                    print("Not all of the following channels are marked for changes")
                    print(", ".join(channels))
                    print("Will treat them individually instead")
                    continue
                self.ratify_uncertainty_in_channels(
                    harvester=harvester,
                    dict_unc=dict_unc,
                    unc=unc,
                    eras=eras,
                    channels=channels
                )
                already_changed_channels = list(set(already_changed_channels + channels))

            untouched_channels = set(already_changed_channels).symmetric_difference(channels_to_change)
            pbar_chan = tqdm(untouched_channels)
            for channel in pbar_chan:
                pbar_chan.set_description("Processing remaining single channel '{}'".format(channel))
                if not channel in harvester_channels:
                    if self.verbosity > 5:
                        print((" ".join("""Could not find channel '{}' 
                                    in current harvester instance, skipping"
                                """.format(channel))))
                    continue
                self.ratify_uncertainty_in_channels(
                    harvester=harvester,
                    dict_unc=dict_unc,
                    unc=unc,
                    eras=eras,
                    channels=[str(channel)]
                )
                        
        return harvester
    
    
    def drop_small_signals(self, harvester, change_dict, eras = [".*"], \
                            channels = [".*"], bins = [".*"]):
        if self.verbosity >= 50:
            print("parameters for dropping processes:")
            print(("\teras: {}".format(", ".join(eras))))
            print(("\tchannels: {}".format(", ".join(channels))))
            print(("\tbins: {}".format(", ".join(bins))))
            print(("\tchange_dict: \n{}".format(json.dumps(change_dict, indent=4))))
        for chan in change_dict:
            to_drop = list(change_dict[chan].keys())
            
            bins = [str(chan)]
            self.drop_all_processes(harvester = harvester, to_drop = to_drop,
                                    eras = eras, channels = channels, 
                                    bins = bins)

    def drop_small_backgrounds(self, harvester, eras = [".*"], \
                            channels = [".*"], bins = [".*"]):
        harvester.SetFlag("filters-use-regex", True)
        if self.verbosity >= 50:
            print("parameters for dropping processes:")
            print(("\teras: {}".format(", ".join(eras))))
            print(("\tchannels: {}".format(", ".join(channels))))
            print(("\tbins: {}".format(", ".join(bins))))
        # first, collect the channels and eras present in the harvester
        # instance to avoid double matching of bins later
        channels = harvester.cp().channel(channels).channel_set()
        if len(channels) == 0:
            channels = [".*"]
        eras = harvester.cp().era(eras).era_set()
        if len(eras) == 0:
            eras = [".*"]
        # entries in list are unicode per default
        # convert to 'normal' strings by hand
        channels = [str(x) for x in channels]
        eras = [str(x) for x in eras]
        # for each bin in each channel and era
        # check for minor backgrounds
        for chan in channels:
            for era in eras:
                these_bins = harvester.cp().channel([chan])\
                                .era([era]).bin(bins).bin_set()
                self.drop_small_processes(harvester = harvester, chan = [chan], \
                                era = [era], bins = these_bins)
                
    def drop_empty_shapes(self, harv, validation_dict):
        """
        input structure:
        {
            nuisance_name: {
                bin: {
                    process: {
                        val_u: XXX,
                        val_d: YYY,
                    }
                }
            }
        }
        """
        for nuisance in validation_dict:
            for b in validation_dict[nuisance]:
                self.__np_manipulator.to_remove = {
                    nuisance: list(validation_dict[nuisance][b].keys())
                }
                self.__np_manipulator.remove_nuisances_from_procs(
                    harvester=harv, bins=[str(b)]
                )

    def apply_validation(self, harvester,  eras = [".*"], \
                            channels = [".*"], bins = [".*"]):
        harvester.SetFlag("filters-use-regex", True)
        if self.verbosity >= 50:
            print("input to 'apply_validation':")
            print(("\teras: {}".format(", ".join(eras))))
            print(("\tchannels: {}".format(", ".join(channels))))
            print(("\tbins: {}".format(", ".join(bins))))
        if isinstance(self.validation_dict, dict):
            if "smallShapeEff" in self.validation_dict and self.__do_smallShapeEff:
                if self.verbosity > 15:
                    print("Will ratify uncertainties w/ small shape effect")
                subdict = self.validation_dict["smallShapeEff"]
                harvester = self.ratify(harvester = harvester, 
                                        change_dict = subdict,
                                        eras = eras)

            if "smallSignalProc" in self.validation_dict and self.__do_smallSigCut:
                if self.verbosity > 15:
                    print("Processes before small signal pruning:")
                    harvester.PrintProcs()
                subdict = self.validation_dict["smallSignalProc"]
                self.drop_small_signals(harvester, change_dict = subdict,
                                        eras = eras, channels = channels,
                                        bins = bins)
                if self.verbosity > 15:
                    print("Processes after small signal pruning:")
                    harvester.PrintProcs()
            if "emptySystematicShape" in self.validation_dict and self.__remove_empty_shapes:
                print("removing systematics with empty shapes")
                subdict = self.validation_dict["emptySystematicShape"]
                self.drop_empty_shapes(harvester, subdict)

                
        if self.__do_smallBkgCut:
            self.drop_small_backgrounds(harvester, eras = eras, 
                                        channels = channels,
                                        bins = bins)

    def generate_validation_output(self, dcpath):
        if isinstance(dcpath, str):
            if os.path.exists(dcpath):
                print("building validation output")
                dirname = os.path.dirname(dcpath)
                dcname = os.path.basename(dcpath)
                outname = ".".join(dcname.split(".")[:-1] + ["json"])
                outname = "validation_" + outname
                outpath = os.path.join(dirname, outname)
                cmd = self.__cmd_template.format(outpath = outpath, 
                                                 input_path = dcpath)
                print(cmd)
                call([cmd], shell = True)
                if os.path.exists(outpath):
                    self.jsonpath = outpath
                else:
                    raise ValueError("Could not generate output \
                        file in '{}'".format(outpath))
    
    
def main(**kwargs):

    harvester = ch.CombineHarvester()
    cardpath = kwargs.get("datacard")
    
    print(cardpath)
    harvester.ParseDatacard(cardpath, "test", "13TeV", "")

    # harvester.PrintAll()

    jsonpath = kwargs.get("jsonpath")
    interface = ValidationInterface()
    if not jsonpath:
        interface.generate_validation_output(cardpath)
    else:
        interface.jsonpath = jsonpath
    
    interface.apply_validation(harvester)

    

    outdir = kwargs.get("outdir")
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    basename = os.path.basename(cardpath)
    prefix = kwargs.get("prefix", None)
    basename = "{}_{}".format(prefix, basename) if prefix else basename
    newpath = os.path.join(outdir, "datacards", basename)
    output_rootfile = kwargs.get("output_rootpath")
    output_rootfile = "{}_{}".format(prefix, output_rootfile) if prefix else output_rootfile
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

    parser.add_option("-j", "--validationoutput",
                        help = " ".join(
                            """
                            path to .json file that is output
                            of 'ValidateDatacard.py'
                            """.split()
                        ),
                        dest = "jsonpath",
                        metavar = "path/to/validationoutput.json",
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

    cardpath = options.datacard
    if not cardpath:
        parser.error("You need to provide the path to a datacard!")
    elif not os.path.exists(cardpath):
        parser.error("Could not find datacard in '{}'".format(cardpath))
    
    jsonpath = options.jsonpath
    if not jsonpath:
        msg = " ".join("""You need to provide the path to 
        the output of the validation tool!""".split())
        parser.error(msg)
    elif not os.path.exists(jsonpath):
        parser.error("Could not find datacard in '{}'".format(jsonpath))

    return options, files

if __name__ == "__main__":
    options, files = parse_arguments()
    main(**vars(options))
