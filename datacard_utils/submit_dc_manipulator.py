import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from optparse import OptionParser

pwd = os.path.realpath(os.path.dirname(__file__))
basedir = os.path.join(pwd, "base")
if not basedir in sys.path:
    sys.path.append(basedir)
from batchConfig import batchConfig
from helperClass import helperClass

batch = batchConfig()
helper = helperClass()

dc_manipulator_path = os.path.join(pwd, "dc_manipulator.py")


cmd_template = helper.JOB_PREFIX
cmd_template += "python {}".format(dc_manipulator_path)
cmd_template += """ -i '{input}' --directory {directory} {additional}
"""
def parse_arguments():
    print("setup parser")
    usage = "python %prog [options]"
    parser = OptionParser(usage = usage)

    parser.add_option("-i", "--input",
                        help = " ".join(
                            """
                            use this string as input for the '-i'
                            option of the dc_manipulator.
                            Can be called multiple times
                            """.split()
                        ),
                        dest = "inputs",
                        action = "append"                
                    )
    parser.add_option("-d", "--directory",
                        help = " ".join(
                            """
                            save modified datacards hier. This will
                            be parsed to the '--directory' option of the dc_manipulator
                            """.split()
                        ),
                        dest = "directory",
                        type = "str"
                    )
    parser.add_option("-a", "--additionalCMD",
                        help = " ".join(
                            """
                            parse these additional commands to the dc_manipulator.
                            Can be called multiple times
                            """.split()
                        ),
                        dest = "additional_cmds",
                        action = "append"
                    )
    parser.add_option("--dry-run",
                      help = " ".join(
                            """
                            just create shell scripts, do not submit anything to
                            batch system
                            """.split()
                      ),
                      dest = "dry_run",
                      action = "store_true",
                      default = False
                    )
    options, args = parser.parse_args()
    if not options.inputs:
        parser.error("You need to provide an input for the dc_manipulator!")
    
    if not options.directory:
        parser.error("You need to provide an output directory for the dc_manipulator!")

    return options, args

def create_script(input, outdir, additional_cmds = []):

    name = helper.check_for_twin("dc_manipulator.sh")
    script = cmd_template.format(input = input, directory = outdir, 
                                additional = " ".join(additional_cmds))
    print("writing script at {}".format(os.path.abspath(name)))
    with open(name, "w") as f:
        f.write(script)
    return name


def main(**kwargs):
    inputs = kwargs.get("inputs")
    outdir = kwargs.get("directory")
    dry_run = kwargs.get("dry_run", False)
    additional_cmds = kwargs.get("additional_cmds", [])
    if not additional_cmds:
        additional_cmds = []
    
    scripts = []
    for i in inputs:
        s = create_script(input = i, outdir= outdir, 
                        additional_cmds = additional_cmds)
        scripts.append(s)
    
    
    if len(scripts) > 0:
        if not dry_run:
            arrayname = "arrayJob.sh"
            arrayname = helper.check_for_twin(arrayname)
            batch.submitArrayToBatch(scripts = scripts, arrayscriptpath = arrayname)
    else:
        print("Could not generate any dc_manipulator scripts!")
    
    print("done")

if __name__ == "__main__":
    print("hello there")
    options, args = parse_arguments()
    main(**vars(options))
