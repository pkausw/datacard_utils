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
        self.__validation_dict = None
        self.__do_smallShapeEff = True
        self.__do_smallSigCut = True
        self.__cmd_template = " ".join("ValidateDatacards.py -p 3 \
            --mass 125.38 --jsonFile {outpath} {input_path}".split())
        
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
                s = json.dumps(self.__validation_dict, 
                               indent = 4, separators = (",", ":"))
                print(s)

            else:
                print("ERROR: file '{}' does not exist!".format(path))
        else:
            print("ERROR: path to validation json has to be a string!")
    
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
        drop = proc.process() in drop_list and proc.bin() == bin_name
        if(drop):
            chob.FilterSysts(lambda sys: self.matching_proc(proc,sys)) 
        return drop
    
    def load_rate_values(self, harvester, uncertainty, channel, process):
        vals = []
        harvester.cp().bin([str(channel)]).process([str(process)]).\
            syst_name([str(uncertainty)]).ForEachSyst(\
                lambda x: vals.append([x.value_u(), x.value_d()]))
        # print(vals)
        vals = vals[0]
        if all(v <= 1. for v in vals):
            print("Found purely down fluctuation!")
            val_u = vals[0]
            val_d = vals[1]

            vals[0] = 1.
            vals[1] = (val_u + val_d)/2.
            vals[0] = vals[1]
        elif all(v >= 1. for v in vals):
            print("Found purely up fluctuation!")
            val_u = vals[0]
            val_d = vals[1]

            vals[1] = 1.
            vals[0] = (val_u + val_d)/2.
            vals[1] = vals[0]
        return vals

    def ratify(self, harvester, change_dict):
        for unc in change_dict:
            print("Uncertainty: {}".format(unc))
            dict_unc = change_dict[unc]
            for channel in dict_unc:
                print("\tChannel: {}".format(channel))
                dict_chan = dict_unc[channel]
                for process in dict_chan:
                    print("\t\tProcess: {}".format(process))
                    vals = self.load_rate_values(    harvester = harvester, 
                                                uncertainty = unc,
                                                channel = channel,
                                                process = process)
                    # print(vals)
                    # harvester.bin([str(channel)]).process([str(process)]).syst_name([str(unc)], False)
                    # harvester.PrintAll()
                    harvester.cp().bin([str(channel)]).process([str(process)]).\
                        syst_name([str(unc)]).ForEachSyst(lambda x: x.set_type("lnN"))

                    harvester.cp().bin([str(channel)]).process([str(process)]).\
                        syst_name([str(unc)]).ForEachSyst(lambda x: x.set_value_u(vals[0]))
                    harvester.cp().bin([str(channel)]).process([str(process)]).\
                        syst_name([str(unc)]).ForEachSyst(lambda x: x.set_value_d(vals[1]))

                    # harvester.PrintSysts()
                    # sys.exit()
        return harvester
    
    def drop_small_signals(self, harvester, change_dict):
        for chan in change_dict:
            to_drop = change_dict[chan].keys()
            harvester.FilterProcs(lambda x: self.drop_procs(harvester, x, chan, to_drop))
        
        
    def apply_validation(self, harvester):
        if "smallShapeEff" in self.validation_dict and self.__do_smallShapeEff:
            subdict = self.validation_dict["smallShapeEff"]
            harvester = self.ratify(harvester = harvester, change_dict = subdict)
        if "smallSignalProc" in self.validation_dict and self.__do_smallSigCut:
            subdict = self.validation_dict["smallSignalProc"]
            self.drop_small_signals(harvester, change_dict = subdict)
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
