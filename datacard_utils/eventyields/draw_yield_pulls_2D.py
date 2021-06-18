import os
import sys
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.TH1.AddDirectory(False)

from optparse import OptionParser

def parse_arguments():
    parser = OptionParser()
    parser.add_option("-o", "--outputpath",
                        help = " ".join("""
                            Save final plot in this directory.
                            Default is here (.)
                            """.split()),
                        dest = "outpath",
                        default = ".",
                        type = "str"
                    )
    parser.add_option("-p", "--prefix",
                        help = " ".join("""
                            Use this prefix when saving the final plot.
                            This is prepended to the file name of the input
                            root file. Default: yield_pulls
                            """.split()),
                        dest = "prefix",
                        default = "yield_pulls",
                        type = "str"
                    )
    parser.add_option("-e", "--extension",
                        help = " ".join("""
                            Save the plot in these file formats.
                            Default: [png, pdf]
                            """.split()),
                        dest = "extensions",
                        default = "png pdf".split(),
                        action = "append"
                    )
    
    options, args = parser.parse_args()
    options.extensions = list(set(options.extensions))
    return options, args

def find_yield_objects(rdir):
    keys = [x.GetName() for x in rdir.GetListOfKeys() \
                if x.GetName().startswith("yield_")]
    # remove the yield prefix
    keys = [x.replace("yield_", "") for x in keys]
    # filter out separate channels
    keys = [x for x in keys if not any(x.startswith(f) or x.endswith(e)\
            for f in """tHq_ tHW_ ttbarW ttbarZ wjets 
                    zjets ttH_ TotalSig data_obs"""\
                .split()\
            for e in ["""_CR"""]
                )
            ]
    return keys

def load_yields(rfile, category, process):
    """load yields for process 'process' in the category 'category'.
    If process is not found, return 0. Current implementation
    relies on yield objects in RooRealVar format

    Args:
        rfile (ROOT.TFile): ROOT file containing the categories with
                            the yield objects
        category (str):     name of pre fit/ post fit category to load
                            yield for
        process (str):      name of process to load

    Returns:
        [float]:            yield for process in category. Defaults to 0

    """
    # load category
    # rdir = rfile.Get(category)
    # rfile.ls()
    # access yield information for process.
    # If yield is not in RooRealVar format, return 0
    # rdir.ls()
    object_name = "{}/yield_{}".format(category,process)
    # print("loading object '{}'".format(object_name))
    y = rfile.Get(object_name)
    # print(y)
    if isinstance(y, ROOT.RooRealVar):
        return y.getVal()
    else:
        print("Could not load process '{}' for category '{}'"\
                .format(process, category))
    return 0.


def collect_information(rfile):
    """Collect necessary information to draw yield pull histogram.
    Necessary information includes
      - the names of categories to show
      - the list of processes to draw

    Args:
        rfile (ROOT.TFile): ROOT file containing the categories with 
                            the yield objects

    Returns:
        [dict]: dictionary with relevant information of format
                {
                    "categories": {
                        "category name":{
                            "prefit": name/of/prefit/dir
                            "postfit": name/of/postfit/dir
                        }
                    },
                    "processes": set of all processes in different categories
                }
    """    
    # define final dictionary that will contain all the information
    infos = {}
    # list that will contain all processes
    processes = []
    # load directories, i.e. pre fit and post fit categories
    keys = [x.GetName() for x in rfile.GetListOfKeys() if x.IsFolder()]

    # loop through all prefit categories and look for the corresponding
    # post fit counter part
    prefit_keys = [x for x in keys if x.endswith("_prefit")]
    # look for post fit counter parts
    category_dic = {}
    for k in prefit_keys:
        postfit_key = k.replace("_prefit", "_postfit")
        # if match is found, safe this category for later
        if postfit_key in keys:
            name = k.replace("_prefit", "")
            category_dic[name] = {
                "prefit": k,
                "postfit": postfit_key
            }
        # update list of processes
        rdir = rfile.Get(k)
        processes = list(set(processes + find_yield_objects(rdir)))
    # save information and return it
    infos["categories"] = category_dic
    infos["processes"] = processes
    return infos

def construct_histogram(rfile, infos):
    """Construct histogram with yield pulls.
    Function first load information from 'infos' dictionary.
    Then a ROOT.TH2D histogram is initialized with the number
    of categories as x bins and the number of processes as y bins.
    If a process is not available for a given category, the 
    corresponding entry is 0. Otherwise, the ratio 
    (yield_postfit - yield_prefit)/yield_prefit is filled.

    Args:
        rfile (ROOT.TFile): ROOT File containing the information
        infos (dict): Dictionary containing the information about what to draw.
                    Format:
                    {
                        "categories": {
                            "category name":{
                                "prefit": name/of/prefit/dir
                                "postfit": name/of/postfit/dir
                            }
                        },
                        "processes": set processes in different categories
                    }

    Returns:
        [type]: [description]

    Yields:
        [type]: [description]
    """    
    # load necessary information
    category_dict = infos["categories"]
    categories = sorted(category_dict)
    processes = sorted(infos["processes"])

    # construct Histogram. x axis will show categories, 
    # y axis will show processes, z axis will show ratio (postfit - prefit)/prefit
    ncategories = len(categories)
    nprocs = len(processes)
    h = ROOT.TH2D("yield_pulls", "yield_pulls", nprocs, 0, nprocs,\
                    ncategories, 0, ncategories)
    h.SetStats(False)
    # setup names for bins
    for i, cat in enumerate(categories, 1):
        h.GetYaxis().SetBinLabel(i, cat)
    for i, proc in enumerate(processes, 1):
        h.GetXaxis().SetBinLabel(i, proc)

    # setup axis names
    ztitle = "#frac{yield_{postfit} - yield_{prefit}}{yield_{prefit}} in %"
    h.GetZaxis().SetTitle(ztitle)
    h.GetZaxis().SetTitleOffset(1.7)
    h.GetZaxis().SetRangeUser(-100, 100)
    # loop through the categories
    for y, cat in enumerate(categories, 1):
        for x, proc in enumerate(processes, 1):
            # load yields
            prefit_name = category_dict[cat]["prefit"]
            postfit_name = category_dict[cat]["postfit"]
            prefit_yield = load_yields(rfile = rfile, category = prefit_name, 
                                process = proc)
            postfit_yield = load_yields(rfile = rfile, category = postfit_name, 
                                process = proc)
            # if process is not available for given category,
            # prefit_yield is 0. In that case, avoid division
            # by 0 by filling a 0
            ratio = (postfit_yield - prefit_yield)/prefit_yield \
                        if not prefit_yield == 0. else 0.
            
            # finally, fill histogram
            h.SetBinContent(x, y, ratio*100)
    return h
        

def construct_yield_pulls(infile, **kwargs):
    """draw yield pull histogram for given input root file.
    First, the information to setup the histogram is collected.
    Afterwards, the histogram is constructed using this information.
    Finally, the plot is saved according to the specifications the
    user can give using the available options.

    Args:
        infile (ROOT.TFile):        ROOT File containing the information
        **kwargs (key word args):   pass through for options from
                                    option parser

    Return:
        None

    """
    infos = collect_information(infile)
    histogram = construct_histogram(rfile=infile, infos = infos)

    # get file name
    filename = os.path.basename(infile.GetName())
    # remove extension
    filename = ".".join(filename.split(".")[:-1])

    # build output file name for plot
    prefix = kwargs.get("prefix", "")
    outpath = kwargs.get("outpath", ".")
    extensions = kwargs.get("extensions", "png pdf".split())

    filename = "_".join([prefix, filename]) if not prefix == ""\
                else filename
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    outname = os.path.join(outpath, filename)

    # in order to save final plot, first draw histogram to canvas

    c = ROOT.TCanvas("yield_pull", "yield_pulls", 2200, 1600)
    ROOT.gStyle.SetPaintTextFormat("2.1f")
    c.SetRightMargin(0.2)
    c.SetLeftMargin(0.35)

    histogram.Draw("coltzTEXT")
    for ext in extensions:
        final_name = ".".join([outname, ext])
        c.SaveAs(final_name, ext)
    


def main(*files, **kwargs):
    for f in files:
        if not os.path.exists(f):
            print("Found no file with name '{}'".format(f))
            continue
        print("Consider {}".format(f))
        rfile = ROOT.TFile.Open(f)
        construct_yield_pulls(infile = rfile, **kwargs)

if __name__ == '__main__':
    options, files = parse_arguments()
    main(*files, **vars(options))