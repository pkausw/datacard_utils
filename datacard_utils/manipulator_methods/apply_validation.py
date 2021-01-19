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

ROOT.TH1.AddDirectory(False)

class ValidationInterface(object):

    def __init__(self):
        self.__jsonpath = None
        self.__debug = 0
        self.__validation_dict = None
        self.__do_smallShapeEff = True
        self.__do_smallSigCut = True
        self.__cmd_template = " ".join("ValidateDatacards.py -p 3 \
            --mass 125.38 --jsonFile {outpath} {input_path}".split())
    
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
                print("ERROR: file '{}' does not exist!".format(path))
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
            print("Could not set 'remove_small_signals' to '{}'".format(val))
            print("Value has to be bool")

    @property
    def validation_dict(self):
        return self.__validation_dict
    
    def matching_proc(self, p,s):
        return ((p.bin()==s.bin()) and (p.process()==s.process()) \
                and (p.signal()==s.signal()) and \
                (p.analysis()==s.analysis()) and (p.era()==s.era()) \
                and (p.channel()==s.channel()) and (p.bin_id()==s.bin_id()) \
                and (p.mass()==s.mass()))
    
    def drop_procs(self, chob, proc, bin_name, drop_list):
        if self.verbosity >= 50:
            print("="*130)
            print("checking process if it should be dropped:")
            print("\tname: {}".format(proc.process()))
            print("\tbin: {}".format(proc.bin()))
            print("\trate: {}".format(proc.rate()))
            print("\tcurrent bin to prune: {}".format(bin_name))
            print("\tcurrent list to drop: {}".format(", ".join(drop_list)))
        drop = (proc.process() in drop_list) and (proc.bin() == bin_name)
        drop = drop or proc.rate() == 0
        if(drop):
            if self.verbosity >= 10:
                print("dropping process '{}/{}'".\
                        format(proc.bin(), proc.process()))
            chob.FilterSysts(lambda sys: self.matching_proc(proc,sys)) 
        return drop
    
    def load_rate_values(self, harvester, uncertainty, channel, process):
        vals = []
        harvester.cp().bin([str(channel)]).process([str(process)]).\
            syst_name([str(uncertainty)]).ForEachSyst(\
                lambda x: vals.append([x.value_u(), x.value_d()]))
        # print(vals)
        if len(vals) > 0:
            vals = vals[0]
            if all(v <= 1. for v in vals):
                if self.verbosity > 10:
                    print("Found purely down fluctuation!")
                val_u = vals[0]
                val_d = vals[1]

                vals[0] = 1.
                vals[1] = (val_u + val_d)/2.
                vals[0] = vals[1]
            elif all(v >= 1. for v in vals):
                if self.verbosity > 10:
                    print("Found purely up fluctuation!")
                val_u = vals[0]
                val_d = vals[1]

                vals[1] = 1.
                vals[0] = (val_u + val_d)/2.
                vals[1] = vals[0]
        return vals

    def ratify(self, harvester, change_dict, eras = [".*"]):
        for unc in change_dict:
            if self.verbosity > 5:
                print("Uncertainty: {}".format(unc))
            dict_unc = change_dict[unc]
            for channel in dict_unc:
                if self.verbosity > 5:
                    print("\tChannel: {}".format(channel))
                dict_chan = dict_unc[channel]
                for process in dict_chan:
                    if self.verbosity > 5:
                        print("\t\tProcess: {}".format(process))
                    era_harvester = harvester.cp().era(eras)
                    vals = self.load_rate_values(harvester = era_harvester,
                                                uncertainty = unc,
                                                channel = channel,
                                                process = process)
                    # print(vals)
                    # harvester.bin([str(channel)]).process([str(process)]).syst_name([str(unc)], False)
                    # harvester.PrintAll()
                    if len(vals) > 0:
                        harvester.cp().era(eras).\
                            bin([str(channel)]).\
                            process([str(process)]).\
                            syst_name([str(unc)]).\
                            ForEachSyst(lambda x: x.set_type("lnN"))

                        harvester.cp().era(eras).\
                            bin([str(channel)]).\
                            process([str(process)]).\
                            syst_name([str(unc)]).\
                            ForEachSyst(lambda x: x.set_value_u(vals[0]))
                        harvester.cp().era(eras).\
                            bin([str(channel)]).\
                            process([str(process)]).\
                            syst_name([str(unc)]).\
                            ForEachSyst(lambda x: x.set_value_d(vals[1]))
                    else:
                        print("="*130)
                        print("Could not find uncertainty '{}' in '{}/{}'".\
                                format(unc, channel, process))

                    # harvester.PrintSysts()
                    # sys.exit()
        return harvester
    
    def drop_small_signals(self, harvester, change_dict, eras = [".*"], \
                            channels = [".*"], bins = [".*"]):
        if self.verbosity >= 50:
            print("parameters for dropping processes:")
            print("\teras: {}".format(", ".join(eras)))
            print("\tchannels: {}".format(", ".join(channels)))
            print("\tbins: {}".format(", ".join(bins)))
            print("\tchange_dict: \n{}".format(json.dumps(change_dict, indent=4)))
        for chan in change_dict:
            to_drop = change_dict[chan].keys()
            if self.verbosity >= 50:
                print("pruning bin '{}'".format(chan))
                print("to drop: [{}]".format(", ".join(to_drop)))
                print("harvester with era selection:")
                harvester.cp().era(eras).PrintProcs()
                print("="*130)
                print("harvester with bin selection")
                harvester.cp().era(eras).channel(channels).bin(bins).PrintProcs()
                print("="*130)
                print("harvester with channel selection")
                harvester.cp().era(eras).channel(channels).PrintProcs()
            
                print("="*130)
            bins = [str(chan)]
            harvester.cp().era(eras).channel(channels).bin(bins)\
                .ForEachProc(lambda x: \
                    harvester.FilterProcs(lambda y: True if self.matching_proc(x, y) and \
                                                            self.drop_procs(harvester, x, 
                                                            chan, to_drop)\
                                                        else False
                                        )
                            )
        
        
    def apply_validation(self, harvester,  eras = [".*"], \
                            channels = [".*"], bins = [".*"]):
        harvester.SetFlag("filters-use-regex", True)
        if self.verbosity >= 50:
            print("input to 'apply_validation':")
            print("\teras: {}".format(", ".join(eras)))
            print("\tchannels: {}".format(", ".join(channels)))
            print("\tbins: {}".format(", ".join(bins)))
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
                        file in '{}'".format(outputpath))
    
    
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
