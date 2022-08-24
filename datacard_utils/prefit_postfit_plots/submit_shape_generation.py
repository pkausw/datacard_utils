import os
import sys
import stat
import ROOT

thisdir = os.path.realpath(os.path.dirname(__file__))
basedir = os.path.join(thisdir, "..", "utilities", "base")
if not basedir in sys.path:
    sys.path.append(basedir)

from optparse import Option, OptionParser
from helperClass import helperClass
from batchConfig import batchConfig

helper = helperClass()
batch = batchConfig()

try:
    print("importing CombineHarvester")
    import CombineHarvester.CombineTools.ch as ch
    print("done")
except:
    msg = " ".join("""Could not find package 'CombineHarvester'. 
            Are you sure you installed it?""".split())
    raise ImportError(msg)

prefit_template = helper.JOB_PREFIX
prefit_template_binned = prefit_template

CMD_BASE="""    
    cmd="PostFitShapesFromWorkspace -w $inputfile -o ${{outfile}}.root"
    cmd="$cmd -p 'tH=tH.*' -p 'vjets=(w|z)jets' -p 'ttbarV=ttbar(W|Z)' -p 'multijet=.*_CR'"
    cmd="$cmd -p 'tHq=tHq_.*' -p 'tHW=tHW_.*' {additional_commands}"
"""

CMD_BASE_BINNED="""    
    cmd="PostFitShapesFromWorkspace -w $inputfile -o ${{outfile}}_${{bin}}.root --bin ${{bin}}"
    cmd="$cmd -p 'tH=tH.*' -p 'vjets=(w|z)jets' -p 'ttbarV=ttbar(W|Z)' -p 'multijet=.*_CR'"
    cmd="$cmd -p 'tHq=tHq_.*' -p 'tHW=tHW_.*' {additional_commands}"
"""
CMD_BASE_STXS="""    
    cmd="PostFitShapesFromWorkspace -w $inputfile -o ${{outfile}}.root"
    cmd="$cmd -p 'tH=tH.*' -p 'vjets=(w|z)jets' -p 'ttbarV=ttbar(W|Z)' -p 'multijet=.*_CR'"
    cmd="$cmd -p 'tHq=tHq_.*' -p 'tHW=tHW_.*'"
    cmd="$cmd -p 'ttH_PTH_0_60=ttH_PTH_0_60_.*'"
    cmd="$cmd -p 'ttH_PTH_60_120=ttH_PTH_60_120_.*'"
    cmd="$cmd -p 'ttH_PTH_120_200=ttH_PTH_120_200_.*'"
    cmd="$cmd -p 'ttH_PTH_200_300=ttH_PTH_200_300_.*'"
    cmd="$cmd -p 'ttH_PTH_GT300=ttH_PTH_(300_450|GT300|GT450)_.*' {additional_commands}"
"""

CMD_BASE_STXS_BINNED="""    
    cmd="PostFitShapesFromWorkspace -w $inputfile -o ${{outfile}}_${{bin}}.root --bin ${{bin}}"
    cmd="$cmd -p 'tH=tH.*' -p 'vjets=(w|z)jets' -p 'ttbarV=ttbar(W|Z)' -p 'multijet=.*_CR'"
    cmd="$cmd -p 'tHq=tHq_.*' -p 'tHW=tHW_.*'"
    cmd="$cmd -p 'ttH_PTH_0_60=ttH_PTH_0_60_.*'"
    cmd="$cmd -p 'ttH_PTH_60_120=ttH_PTH_60_120_.*'"
    cmd="$cmd -p 'ttH_PTH_120_200=ttH_PTH_120_200_.*'"
    cmd="$cmd -p 'ttH_PTH_200_300=ttH_PTH_200_300_.*'"
    cmd="$cmd -p 'ttH_PTH_GT300=ttH_PTH_(300_450|GT300|GT450)_.*' {additional_commands}"
"""


prefit_template += """
    outpath=$1
    outfile=$2
    inputfile=$3

    {CMD_BASE}
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

prefit_template_binned += """
    outpath=$1
    outfile=$2
    inputfile=$3
    bin=$4

    {CMD_BASE}
    if [ "$#" -eq 5 ] ; then
        inputdatacard=$5
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
postfit_template_binned = postfit_template
postfit_template_binned += """
    outpath=$1
    outfile=$2
    nsamples=$3
    fitresult=$4
    inputfile=$5
    bin=$6
    

    {CMD_BASE}
    cmd="$cmd -f $fitresult"
    cmd="$cmd --skip-prefit --postfit --sampling --samples $nsamples"
    cmd="$cmd --skip-proc-errs"

    
    if [ "$#" -eq 7 ]; then
            inputdatacard=$7
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

postfit_template += """
    outpath=$1
    outfile=$2
    nsamples=$3
    fitresult=$4
    inputfile=$5
    

    {CMD_BASE}
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

def check_fitobject(fit, path):
    rfile = ROOT.TFile.Open(path)
    if not rfile.IsOpen() or rfile.IsZombie() or rfile.TestBit(ROOT.TFile.kRecovered):
        raise ValueError("File '{}' is broken!".format(path))
    # next, test fit object itself
    f = rfile.Get(fit)
    if not isinstance(f, ROOT.RooFitResult):
        raise ValueError("Could not load '{}' from '{}'".format(fit, path))
    if not ((f.covQual() == 3 or f.covQual() == -1) and f.status() == 0 ):
        raise ValueError("Fit in '{}' in file '{}' is broken, please check!".format(fit, path))

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
    parser.add_option( "--stxs",
                        help = " ".join(
                            """
                            Adjust commands to generate all process relevant for STXS.
                            Defaults to False
                            """.split()
                        ),
                        action = "store_true",
                        default = False,
                        dest = "stxs"
        )
    parser.add_option("-v", "--verbose",
                        help= " ".join(
                            """
                            generate shapes with the verbose output option.
                            Careful: This can generate very large log files,
                            use only for debug with small number of toys
                            """.split()
                        )
        )
    parser.add_option("-t", "--runtime",
                        help= " ".join(
                            """
                            request this run time (in seconds) for the post-fit
                            generation. Default is the standard run time of the
                            HTCondor schedd
                            """.split()
                        ),
                        type="int",
                        dest = "runtime"
        )
    parser.add_option("-a", "--add-command",
                        help= " ".join(
                            """
                            add this command to the PostFitShapesFromWorkspace
                            command. Can be called multiple times
                            """.split()
                        ),
                        action="append",
                        dest = "add_commands",
                        default=[],
        )
    parser.add_option("-s", "--split-bins",
                        help= " ".join(
                            """
                            generate a job for each bin (i.e. channel) in the
                            workspace. This will speed up the shape generation,
                            but you will not be able to use the `--total` option
                            reasonably. Default: False
                            """.split()
                        ),
                        action="store_true",
                        dest = "split_bins",
                        default=False,
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
            check_fitobject(fitobject, path)
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

def load_bins_from_workspace(filepath, data="data_obs"):
    f = ROOT.TFile.Open(filepath)
    ws = f.Get("w")
    cmb = ch.CombineHarvester()
    cmb.SetFlag("workspaces-use-clone", True)
    cmb.SetFlag("filters-use-regex", True)
    ch.ParseCombineWorkspace(cmb, ws, "ModelConfig", data, False)

    return cmb.bin_set()

def generate_scripts(
    outpath, 
    files, 
    template, 
    script_name, 
    prefix,
    additional_options=None,
    runtime=None,
    split_bins=False
):
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
        bins = load_bins_from_workspace(f) if split_bins else [None]
        basename = os.path.basename(f)
        basename = ".".join(basename.split(".")[:-1])
        for b in bins:
            outputfile = "{}_{}".format(prefix, basename)
            cmdparts = [scriptpath, outpath, outputfile]
            if additional_options:
                cmdparts += additional_options
            cmdparts += [ f]
            if b:
                cmdparts.append(b)
            datacard = find_datacard(f)
            if datacard:
                cmdparts.append(datacard)
            cmds.append("'{}'".format(" ".join(cmdparts)))
    print("\n".join(cmds))
    arrayscriptpath = "arrayJobs_{}.sh".format(prefix)
    arrayscriptpath = os.path.join(srcpath, arrayscriptpath)
    if runtime:
        batch.runtime = runtime
    # batch.submitArrayToBatch(scripts = cmds, arrayscriptpath = arrayscriptpath)
    
        

def generate_postfit_scripts(outpath, fitresult, nsamples, files):
    pass

def load_cmd_base(split_bin, stxs):
    """
    load the right command base based on *split_bin* and *stxs*.
    For explanation of these input features, see the argument parser.
    """
    if split_bin:
        return CMD_BASE_BINNED if not stxs else CMD_BASE_STXS_BINNED
    else:
        return CMD_BASE if not stxs else CMD_BASE_STXS

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
    stxs = kwargs.get("stxs", False)
    outpath = kwargs.get("outputpath", ".")
    fitresult = kwargs.get("fitresult")
    nsamples = kwargs.get("nsamples", 300)
    runtime = kwargs.get("runtime")
    split_bins = kwargs.get("split_bins", False)
    additional_commands = kwargs.get("add_commands", [])

    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outpath = os.path.abspath(outpath)
    this_cmd_base = load_cmd_base(split_bins, stxs)
    this_cmd_base = this_cmd_base.format(additional_commands = " ".join(additional_commands))
    if not skip_prefit:
        template = prefit_template_binned if split_bins else prefit_template
        generate_scripts(outpath = outpath, files = files, 
                            template = template.format(CMD_BASE=this_cmd_base), 
                            script_name = "generate_prefit_shapes.sh",
                            prefix = "shapes_prefit",
                            split_bins=split_bins,
                        )

    if not skip_postfit:
        additional_cmds = [str(nsamples), fitresult]
        template = postfit_template_binned if split_bins else postfit_template
        generate_scripts(outpath = outpath, files = files, 
                            template = template.format(CMD_BASE = this_cmd_base), 
                            script_name = "generate_postfit_shapes.sh",
                            prefix = "shapes_postfit",
                            additional_options=additional_cmds,
                            runtime = runtime,
                            split_bins=split_bins,
                        )
    

if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))
