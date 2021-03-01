import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from sys import argv, path as spath
import os
from os import path as opath, getcwd, remove, environ
from math import ceil
thisfile = opath.abspath(opath.realpath(__file__))
thisdir = opath.dirname(thisfile)
basedir = opath.join(thisdir, "..", "..", "base")
if not basedir in spath:
    spath.append(basedir)
from helperClass import helperClass
from batchConfig import batchConfig
helper = helperClass()
batch = batchConfig()
from optparse import OptionParser
from math import ceil, floor
import subprocess
import json
verbosity = 0


head = """#!/bin/sh
ulimit -s unlimited
targetdir="%(TARGETDIR)s"
cmd="%(CMD)s"
"""

cmssw_base = os.environ["CMSSW_BASE"]
if not os.path.exists(cmssw_base):
    raise ValueError("Please setup the CMSSW environment!")

body = """
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export CMSSW_BASE={CMSSW_BASE}

if [[ -d $CMSSW_BASE ]]; then
    cd $CMSSW_BASE
    eval `scram runtime -sh`
    cd -

    if [[ -d $targetdir ]]; then
        cd $targetdir
        echo $cmd
        eval $cmd
        cd -
    else
        echo "could not change into directory $targetdir"
    fi
else
    echo "Could not find CMSSW_BASE in $CMSSW_BASE!"
fi
""".format(CMSSW_BASE = cmssw_base)
shell_template = head + body

cmd_template = "python " + thisfile + " -i %(INPUTFILE)s -o %(OUTPUTFILE)s -k %(KEYLIST)s --binJson %(BINJSON)s"

def rebin_histo(h, division_factor = 2):
    bins_x = h.GetNbinsX()
    bins_y = h.GetNbinsY()
    new_bins_x = int(ceil(bins_x/float(division_factor)))
    new_bins_y = int(ceil(bins_y/float(division_factor)))

    x_min = h.GetXaxis().GetBinLowEdge(1)
    x_max = h.GetXaxis().GetBinUpEdge(bins_x)

    y_min = h.GetYaxis().GetBinLowEdge(1)
    y_max = h.GetYaxis().GetBinUpEdge(bins_y)

    print ("Creating new histogram with n_x = %s, n_y = %s" % (str(new_bins_x), str(new_bins_y)))
    new_h = ROOT.TH2D("rebinned_" + h.GetName(), h.GetTitle(), new_bins_x, x_min, x_max, new_bins_y, y_min, y_max)
    for x in range(1, bins_x+1, division_factor):
        for y in range(1, bins_y+1, division_factor):
            content = 0
            error = 0
            for i in range(0, division_factor):
                for j in range(0, division_factor):
                    if not x+i > bins_x and not y+j > bins_y: 
                        print ("\tadding from ({0}, {1}) value {2}, {3}".format(x+i, y+j, h.GetBinContent(x+i, y+j), (h.GetBinError(x+i, y+j))**2))
                        content += h.GetBinContent(x+i, y+j)
                        error += (h.GetBinError(x+i, y+j))**2
            error = error**(1./2)
            new_x = int(ceil(x/float(division_factor)))
            new_y = int(ceil(y/float(division_factor)))
            if not new_x > new_bins_x and not new_y > new_bins_y:
                print ("filling bins ({0}, {1}) with {2} +- {3}".format(new_x, new_y, content, error))
                new_h.SetBinContent(new_x, new_y, content)
                new_h.SetBinError(new_x, new_y, error)

    return new_h


def rebin_histo_new(h, division_factor = 2):
    bins_x = h.GetNbinsX()
    bins_y = h.GetNbinsY()
    # new_bins_x = int(ceil(bins_x/float(division_factor)))
    # new_bins_y = int(ceil(bins_y/float(division_factor)))
    new_bins_x = int(floor(bins_x/float(division_factor)))
    new_bins_y = int(floor(bins_y/float(division_factor)))

    x_min = h.GetXaxis().GetBinLowEdge(1)
    x_max = h.GetXaxis().GetBinUpEdge(bins_x)

    y_min = h.GetYaxis().GetBinLowEdge(1)
    y_max = h.GetYaxis().GetBinUpEdge(bins_y)

    print ("Creating new histogram with n_x = %s, n_y = %s" % (str(new_bins_x), str(new_bins_y)))
    name = h.GetName()
    if not "rebinned" in name:
        name = "rebinned_" + h.GetName()
    new_h = ROOT.TH2D(name, h.GetTitle(), new_bins_x, x_min, x_max, new_bins_y, y_min, y_max)

    xProblem = False
    yProblem = False
    if bins_x % 2 != 0:
        xProblem = True
    if bins_y % 2 != 0:
        yProblem = True
    # print(xProblem,yProblem)

    for x in range(1, bins_x+1, division_factor):
        for y in range(1, bins_y+1, division_factor):
            content = 0
            error = 0
            xOffset = 0
            yOffset = 0
            for i in range(0, division_factor):
                for j in range(0, division_factor):
                    if not (yProblem and y == bins_y) and not (xProblem and x == bins_x):
                        if  verbosity > 0:
                            print ("\tadding from ({0}, {1}) value {2}, {3}".format(x+i, y+j, h.GetBinContent(x+i, y+j), (h.GetBinError(x+i, y+j))**2))
                        content += h.GetBinContent(x+i, y+j)
                        error += (h.GetBinError(x+i, y+j))**2

                if xProblem and x == bins_x and y != bins_y:
                    xOffset = -1
                    content += h.GetBinContent(x, y+i)
                    error += (h.GetBinContent(x, y+i))**2 

                if yProblem and y == bins_y and x != bins_x:
                    yOffset = -1
                    content += h.GetBinContent(x+i, y)
                    error += (h.GetBinContent(x+i, y))**2 

                if xProblem and yProblem and x == bins_x and y == bins_y:
                    xOffset = -1
                    yOffset = -1
                    content += h.GetBinContent(x+i, y+i)
                    error += (h.GetBinContent(x+i, y+i))**2 

            new_x = int(ceil(x/float(division_factor)))+xOffset
            new_y = int(ceil(y/float(division_factor)))+yOffset
            # new_x = int(floor(x/float(division_factor)))+xOffset
            # new_y = int(floor(y/float(division_factor)))+yOffset

            if not (yProblem and y == bins_y) and not (xProblem and x == bins_x):
                new_h.SetBinContent(new_x, new_y, content)
                new_h.SetBinError(new_x, new_y, error**(1./2))
            elif (yProblem and y == bins_y and x != bins_x):
                new_h.SetBinContent(new_x, new_y-1, new_h.GetBinContent(new_x, new_y-1)+ content)
                new_h.SetBinError(new_x, new_y-1, (new_h.GetBinError(new_x, new_y-1)**2 + error**2)**(1./2))
            elif (xProblem and x == bins_x and y != bins_y):
                new_h.SetBinContent(new_x-1, new_y, new_h.GetBinContent(new_x-1, new_y) + content)
                new_h.SetBinError(new_x, new_y-1, (new_h.GetBinError(new_x-1, new_y)**2 + error**2)**(1./2))
            elif (xProblem and yProblem and x == bins_x and y == bins_y):
                new_h.SetBinContent(new_x, new_y, new_h.GetBinContent(new_x, new_y) + content)
                new_h.SetBinError(new_x, new_y, (new_h.GetBinError(new_x, new_y)**2 + error**2)**(1./2))
    return new_h



def cross_check(orig, unrolled):
    bins = unrolled.GetNbinsX()
    x = ROOT.Long(0)
    y = ROOT.Long(0)
    z = ROOT.Long(0)
    for b in range(1, bins+1):
        unrolled.GetBinXYZ(b, x, y, z)
        orig_val = orig.GetBinContent(x, y)
        unrolled_val = unrolled.GetBinContent(b)
        print ("origval({2},{3}) = {0}\tunrolled val({4}) = {1}".format(orig_val, unrolled_val, x, y, b))

def do_unrolling(h):
    bins_x = h.GetNbinsX()+2 #also count over and underflow bins
    bins_y = h.GetNbinsY()+2
    allbins = bins_x*bins_y
    hist = ROOT.TH1D("unrolled_" + h.GetName(), "", allbins, 0, allbins)
    hist.Sumw2()
    hist.SetDirectory(0)
    bins = []
    for x in range(0, bins_x):
        for y in range(0, bins_y):
            # print "x={0}\ty={1}".format(x, y)
            current_bin = h.GetBin(x, y)
            bins.append(current_bin)
            current_val = h.GetBinContent(current_bin)
            current_error = h.GetBinError(current_bin)
            # print "\tbin = {0}\tval = {1}\terr = {2}".format(current_bin, current_val, current_error)
            if current_bin > allbins:
                print ("WARNING: global bin is in overflow of unrolled histo {}".format( hist.GetName()))
            hist.SetBinContent(current_bin, current_val)
            hist.SetBinError(current_bin, current_error)
    norm = hist.Integral()
    if norm <= 0:
        print("WARNING: HISTOGRAM HAS NEGATIV INTEGRAL ({})! Will skip {}".format(norm, h.GetName()))
        return None
    # print "allbins = {0}\tcounted bins = {1}".format(allbins, len(bins))
    # cross_check(orig = h, unrolled = hist)
    return hist

counter = 0
def write_file(input_lines, outname):
    global counter
    print ("WRITING LIST OF BROKEN HISTS TO '%s'!" % outname)
    with open(outname,"w") as f:
        f.write("\n".join(input_lines))
    counter += 1

def unroll_histos(path_to_file, outfilepath, keylist, binJson):
    infile = ROOT.TFile.Open(path_to_file)
    with open(binJson) as json_file: 
        rebinDict = json.load(json_file) 

    if not helper.intact_root_file(infile):
        print ("ERROR: file '%s' is corrupted!" % path_to_file)
        return None
    
    dirname = getcwd()
    filename = opath.basename(path_to_file)

    if opath.exists(outfilepath):
        print ("Removing file '%s'" % outfilepath)
        remove(outfilepath)

    outfile = ROOT.TFile.Open(outfilepath, "RECREATE")
    keys = keylist
    nkeys = len(keys)
    broken = []
    broken_counter = 0
    nomName = ""
    nRebins = 0
    for keycounter, key in enumerate(keys):
        if key.count("__") == 2:
            nomName = "".join(key.split("__", 2)[1:2])
        else:
            nomName = key.split("__")[1].strip("_")
        try:
            nRebins = rebinDict[nomName]["Nrebins"]
        except:
            print("Could't find entry in BinJson for {}".format(nomName))
            broken.append(key)
            
        print("Rebinning {n} times for {key}".format(n=nRebins, key = key))
        
        if keycounter % 100 == 0:
            print ("reading key {0}/{1}".format(keycounter, nkeys))
        if isinstance(key, str):
            keyname = key
        else:
            keyname = key.GetName()
        h = infile.Get(keyname)
        if isinstance(h, ROOT.TH2):
            for i in range(nRebins):
                h = rebin_histo_new(h)
            tmp = do_unrolling(h)
            if not tmp is None: 
                outfile.WriteTObject(tmp, keyname)
            else:
                broken.append(keyname)
        # if len(broken) > 300:
        #     basename = 
        #     write_file(input_lines = broken, outname = "")
        #     broken = []

    infile.Close()
    outfile.Close()

    if len(broken) > 0:
        base = opath.basename(outfilepath)
        outdirname = opath.dirname(outfilepath)
        write_file(input_lines = broken, 
            outname = opath.join(outdirname, "broken_histograms_"+base + ".txt"))

def write_skript(cmd, outname, targetdir):
    code = shell_template % ({
            "TARGETDIR": targetdir,
            "CMD": cmd,
        })
    print ("writing script here: {}".format( outname))
    with open(outname, "w") as f:
        f.write(code)
    if os.path.exists(outname):
        return outname
    return None

def split_unrolling(infilepath, outfilepath, nHists, binJson, runLocally = False, veto = None):
    infile = ROOT.TFile.Open(infilepath)
    keys = [x.GetName() for x in infile.GetListOfKeys()]
    if veto:
        keys = [x for x in keys if not veto in x]

    outfiledir = opath.dirname(outfilepath)
    basename = opath.basename(outfilepath)
    parts_folder = opath.join(outfiledir, "parts_" + ".".join(basename.split(".")[:-1]))
    print ("will save output parts here: {}".format(parts_folder))
    if not opath.exists(parts_folder):
        os.mkdir(parts_folder)
    startfolder = getcwd()
    os.chdir(parts_folder)
    n_parts = int(ceil(float(len(keys))/nHists))
    parts = outfilepath.split(".")
    scripts = []

    for i in range(0, n_parts):
        if not i == n_parts:
            keylist = keys[nHists*i:nHists*(i+1)]
        else:
            keylist = keys[(i-1)*nHists:]

        outpartname = ".".join(parts[:-1])+ "_%s.%s" %(str(i), parts[-1])
        outpartname = os.path.join(parts_folder, os.path.basename(outpartname)) 
        print( outpartname)
        cmd = cmd_template % ({
                    "INPUTFILE": infilepath,
                    "OUTPUTFILE": outpartname,
                    "KEYLIST" : ",".join(keylist),
                    "BINJSON": binJson
                })
        skriptpath = os.path.join(parts_folder, ".".join(outpartname.split(".")[:-1])+".sh")
        tmp = write_skript(cmd = cmd, outname = skriptpath, targetdir = parts_folder)
        if not tmp is None:
            scripts.append(tmp)

    if len(scripts) > 0:
        if not runLocally:
            #submit scripts as array job to batch
            batchdir = "job_infos"
            if not os.path.exists(batchdir):
                os.mkdir(batchdir)
            os.chdir(batchdir)
            suffix = os.path.basename(parts_folder)
            arrayscriptname = "arrayScript_%s.sh" % suffix
            option = "periodic_hold = ((JobStatus == 2) && (time() - EnteredCurrentStatus) > {})".format(60*60*3-1)
            batch.addoption(option)
            option = "periodic_release = ((JobStatus == 5) && (time() - EnteredCurrentStatus) > 5)"
            batch.addoption(option)
            batch.submitArrayToBatch(   scripts = scripts, 
                                    arrayscriptpath = arrayscriptname)
        else:
            for script in scripts:
                cmd = "source " + script
                # subprocess.call([cmd], shell=True)
    else:
        print ("ERROR: Could not generate any scripts for {}".format(infilepath))

def parse_arguments():
    usage = """
    usage: %prog [options] path/to/datacards OR path/to/workspaces
    """

    parser = OptionParser(usage=usage)

    
    parser.add_option(  "--input" , "-i",
                        help = """unroll histograms from this file 
                        (can be called multiple times)""",
                        dest = "inputs",
                        metavar = "/path/to/root/file:object_to_read_from",
                        type = "str",
                        action = "append",
                        # require = True
                    )
    parser.add_option( "--keys", "-k",
                        help = """only unroll these histograms.
                                Can be a comma-seperated list,
                                can be called multiple times
                            """,
                        dest = "target_keys",
                        metavar = "histokey_in_input_file",
                        type = "str",
                        action = "append"
                    )
    parser.add_option( "--output", "-o",
                        help = """save histograms in this file""",
                        dest = "outfile",
                        metavar = "path_to_output_file",
                        type = "str",
                        # require = True
                    )
    parser.add_option( "-n", "--nHistPerJob",
                        help = """number of histograms to unroll per job
                                (default = 1000)
                                """,
                        dest = "nHists",
                        type = "int",
                        default = 1000
                    )
    parser.add_option(  "--runLocally", "-r",
                        help="""run scripts locally instead of submitting them
                        to cluster""",
                        action="store_true",
                        dest = "runLocally",
                        default= False
                    )
    parser.add_option(  "--veto", "-v",
                        help="""skip histograms containing this string""",
                        dest = "veto",
                        default= "Weight_pdf",
                        type = "str"
                    )
    
    parser.add_option(  "--binJson", "-b",
                        help="""fjson with information regarding the number of rebins""",
                        dest = "binJson",
                        type= "str",
                        default= ""
                    )

    (options, args) = parser.parse_args()

    return options, args

def main(options, args):
    outfile = opath.abspath(options.outfile)
    histokeys = options.target_keys
    if not histokeys is None and not len(histokeys) == 0:
        tmp = []
        for key in histokeys:
            tmp += key.split(",")
        histokeys = tmp
    inputs = options.inputs
    for path in inputs:
        if not opath.exists(path):
            print ("ERROR: path '%s' does not exist!" % path)
            continue
        path = opath.abspath(path)

        if histokeys is None or len(histokeys) == 0:
            split_unrolling(infilepath = path,
                            outfilepath = outfile,
                            nHists = options.nHists,
                            binJson = options.binJson,
                            runLocally = options.runLocally,
                            veto = options.veto
                            )
        else:
            unroll_histos(  path_to_file = path, 
                        outfilepath = outfile,
                        keylist = histokeys,
                        binJson = options.binJson)





if __name__ == '__main__':
    options, args = parse_arguments()
    main(options, args)
