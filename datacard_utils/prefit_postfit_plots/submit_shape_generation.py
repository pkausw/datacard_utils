import os
import sys
import stat

thisdir = os.path.realpath(os.path.dirname(__file__))
basedir = os.path.join(thisdir, "..", "utilities", "base")
if not basedir in sys.path:
    sys.path.append(basedir)

from optparse import Option, OptionParser
from helperClass import helperClass
from batchConfig import batchConfig

helper = helperClass()
batch = batchConfig()


prefit_template = helper.JOB_PREFIX

prefit_template += """
    outpath=$1
    outfile=$2
    inputfile=$3

    cmd="PostFitShapesFromWorkspace -w $inputfile -o $outfile"
    cmd="$cmd -p 'tH=tH.*' -p 'vjets=(w|z)jets' -p 'ttbarV=ttbar(W|Z)' -p 'multijet=.*_CR'"
    cmd="$cmd -p 'tHq=tHq_.* -p 'tHW=tHW_.*"

    if [ "$#" -eq 4 ] ; then
        inputdatacard=$4
        cmd="$cmd -d $inputdatacard"
    fi


    if [[ -d "$outpath" ]]; then
        cd $outpath
        echo "$cmd"
        eval "$cmd"
    else
        echo "Could not find folder '$outpath'"
    fi
        
"""

postfit_template = helper.JOB_PREFIX
postfit_template += """
    outpath=$1
    outfile=$2
    nsamples=$3
    fitresult=$4
    inputfile=$5
    

    cmd="PostFitShapesFromWorkspace -w $inputfile -o $outfile "
    cmd="$cmd -p 'tH=tH.*' -p 'vjets=(w|z)jets' -p 'ttbarV=ttbar(W|Z)' -p 'multijet=.*_CR'"
    cmd="$cmd -p 'tHq=tHq_.* -p 'tHW=tHW_.*"
    cmd="$cmd -f $fitresult"
    cmd="$cmd --skip-prefit --postfit --sampling --samples $nsamples"
    cmd="$cmd --skip-proc-errs"

    
    if [ "$#" -eq 6 ]; then
            inputdatacard=$6
            cmd="$cmd -d $inputdatacard"
    fi


    if [[ -d "$outpath" ]]; then
        cd $outpath
        echo "$cmd"
        eval "$cmd"
        cd -
    else
        echo "Could not find folder '$outpath'"
    fi
        
"""

def parse_arguments():
    usage = """
    python %prog [options] paths/to/workspaces.root

    """
    usage += " ".join("""
            Tool to split the generation of pre-fit and post-fit
            shapes and submit them to a computing cluster.
            This tool uses the 'PostFitShapesFromWorkspace' tool
            that comes with the CombineHarvester package.
            Please make also sure that the parameters in the workspace
            and in the fit result you want to use for the
            post-fit shapes have the same names (including the
            autoMCStat uncertainties) - otherwise, the uncertainty
            band is not fully consistent.
            """.split()
        )
    parser = OptionParser(usage = usage)

    parser.add_option( "-o", "--outputpath",
                        help = " ".join(
                            """
                            path you want to save the shapes in.
                            This folder will also contain the 
                            scripts for the shape generation itself.
                            Defaults to "." (outputpath is current path)
                            """.split()
                        ),
                        dest = "outputpath",
                        type = "str",
                        default = "."
        )
    parser.add_option( "-f", "--fitresult",
                        help = " ".join(
                            """
                            Use this fit result to generate post-fit shapes.
                            Format is path/to/file.root:FIT_OBJECT,
                            where path/to/file.root is e.g. the path to a
                            fitDiagnostics.root file and FIT_OBJECT is the
                            RooFitResult object in that file (e.g. fit_s)
                            """.split()
                        ),
                        metavar = "path/to/file.root:FIT_OBJECT",
                        dest = "fitresult",
                        type = "str"
        )
    parser.add_option( "-n", "--nToys",
                        help = " ".join(
                            """
                            generate post-fit uncertainty band with 
                            this number of toys. Defaults to 300
                            """.split()
                        ),
                        dest = "nsamples",
                        type = "int",
                        default = 300
        )
    parser.add_option( "--skip-prefit",
                        help = " ".join(
                            """
                            skip generation of pre-fit shapes.
                            Defaults to False
                            """.split()
                        ),
                        action = "store_true",
                        default = False,
                        dest = "skip_prefit"
        )
    parser.add_option( "--skip-postfit",
                        help = " ".join(
                            """
                            skip generation of post-fit shapes.
                            Defaults to False
                            """.split()
                        ),
                        action = "store_true",
                        default = False,
                        dest = "skip_postfit"
        )
    
    options, files = parser.parse_args()

    if not options.skip_postfit and not options.fitresult:
        msg = " ".join("""
            You need to provide a path to a fit result in order to
            generate post-fit shapes!
        """.split())
        parser.error(msg)

    if options.fitresult:
        path, fitobject = options.fitresult.split(":")
        path = os.path.abspath(path)
        if os.path.exists(path):
            options.fitresult = ":".join([path, fitobject])
        else:
            parser.error("Could not find file '{}'".format(path))

    return options, files

def find_datacard(workspace):
    dirname = os.path.dirname(workspace)
    basename = os.path.basename(workspace)
    basename = ".".join(basename.split(".")[:-1])
    datacard = os.path.join(dirname, basename+".txt")
    if os.path.exists(datacard):
        return datacard
    print("Could not find datacard for file '{}'".format(workspace))
    return None
    

def generate_scripts(outpath, files, template, script_name, prefix,\
                            additional_options = None):
    srcpath = os.path.join(outpath, "temp")
    if not os.path.exists(srcpath):
        os.mkdir(srcpath)
    
    scriptpath = os.path.join(srcpath, script_name)
    with open(scriptpath, "w") as f:
        f.write(template)
    # make script executable
    st = os.stat(scriptpath)
    os.chmod(scriptpath, st.st_mode | stat.S_IEXEC)
    cmds = []
    for f in files:
        f = os.path.abspath(f)
        basename = os.path.basename(f)
        basename = ".".join(basename.split(".")[:-1])
        outputfile = "{}_{}.root".format(prefix, basename)
        cmdparts = [scriptpath, outpath, outputfile]
        if additional_options:
            cmdparts += additional_options
        cmdparts += [ f]
        datacard = find_datacard(f)
        if datacard:
            cmdparts.append(datacard)
        cmds.append("'{}'".format(" ".join(cmdparts)))
    print("\n".join(cmds))
    arrayscriptpath = "arrayJobs_{}.sh".format(prefix)
    arrayscriptpath = os.path.join(srcpath, arrayscriptpath)
    batch.submitArrayToBatch(scripts = cmds, arrayscriptpath = arrayscriptpath)
    
        

def generate_postfit_scripts(outpath, fitresult, nsamples, files):
    pass

def main(*files, **kwargs):
    """
    Main function. Generates the shell scripts to produce pre-fit
    and post-fit shapes

    Args:
    - files (list): list of paths to input workspaces to generate shapes for
    - kwargs (dict): options from option parser
    """             

    skip_prefit = kwargs.get("skip_prefit", False)
    skip_postfit = kwargs.get("skip_postfit", False)
    outpath = kwargs.get("outputpath", ".")
    fitresult = kwargs.get("fitresult")
    nsamples = kwargs.get("nsamples", 300)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outpath = os.path.abspath(outpath)
    if not skip_prefit:
        generate_scripts(outpath = outpath, files = files, 
                            template = prefit_template, 
                            script_name = "generate_prefit_shapes.sh",
                            prefix = "shapes_prefit"    
                        )

    if not skip_postfit:
        additional_cmds = [str(nsamples), fitresult]
        generate_scripts(outpath = outpath, files = files, 
                            template = postfit_template, 
                            script_name = "generate_postfit_shapes.sh",
                            prefix = "shapes_postfit",
                            additional_options=additional_cmds    
                        )
    

if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))