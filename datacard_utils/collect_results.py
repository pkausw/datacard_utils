import os
import sys
import ROOT
import json

from fnmatch import filter
from optparse import OptionParser
from copy import deepcopy

skip_fit_status = False
def parse_arguments():
    
    parser = OptionParser()
    parser.add_option("--skipBestfit",
                      dest = "do_bestfit",
                      default = True,
                      action = "store_false",
                      help = " ".join("""Do not add fit results 
                                        from fit with 
                                        uncertainties""".split()
                                    )
                      )
    parser.add_option("--skipStatOnly",
                      dest = "do_statonly",
                      default = True,
                      action = "store_false",
                      help = """Do not add fit results from
                      fit w/o uncertainties (stat-only)"""
                      )
    parser.add_option("--skipSignificance",
                      dest = "do_signi",
                      default = True,
                      action = "store_false",
                      help = """Do not add results for
                      significance"""
                      )
    parser.add_option("-o", "--outputfile",
                      help = """Name of the output file""",
                      dest = "outfile",
                      type = "str"
                      )
    parser.add_option("--bestFitKey",
                      help = """Use this key to identify
                      .root files from bestfit with 
                      uncertainties (default = 'bestfit')""",
                      default = "bestfit",
                      type = "str",
                      dest = "bestFitKey"
                      )
    parser.add_option("--statOnlyKey",
                      help = """Use this key to identify
                      .root files from bestfit w/o
                      uncertainties (default = 'stat_only')""",
                      default = "stat_only",
                      type = "str",
                      dest = "statOnlyKey"
                      )
    parser.add_option("--signiKey",
                      help = """Use this key to identify
                      .root files from significance
                      calculation (default = 'significance')""",
                      default = "significance",
                      type = "str",
                      dest = "signiKey"
                      )
    parser.add_option("-p", "--parameter",
                      help = """collect results for these
                      parameters. Parameter names should
                      also be part of the respective file
                      name. Can be user multiple times""",
                      action = "append",
                      dest = "parameters"
                      )
    parser.add_option("--skip-fit-status",
                      help = " ".join("""
                        skipt the check for the fit status.
                        WARNING: if you read out parameters
                        that are not POIs and there were 
                        problems in calculating the uncertainties
                        for all parameters, the uncertainties
                        are likely not trustworthy!
                        Default: False
                      """.split()),
                      action = "store_true",
                      dest = "skip_fit_status",
                      default = False
                      )
    
    options, files = parser.parse_args()
    if options.outfile is None:
        parser.error("""
                     ===============
                     ERROR: please define the name of the 
                     outputfile!
                     ===============
                     """)
    if not options.parameters is None:
        if isinstance(options.parameters, list) and len(options.parameters) == 0:
            options.parameters = ["r"]
    else: options.parameters = ["r"]
    if options.skip_fit_status is True:
        print("WARNING: will skip the check for the fit status!")
    global skip_fit_status
    skip_fit_status = options.skip_fit_status
    return options, files

def is_good_fit(result):
    if result.status() == 0 and result.covQual() == 3:
        return True
    print "WARNING: This is not a good fit!"
    print "\tStatus: {0}\tQuality: {1}".format(result.status(), result.covQual())
    if skip_fit_status:
        print "skipping fit status is active, will ignore warning"
    print "skip_fit_status: ", skip_fit_status
    return skip_fit_status #DANGERZONE!

def load_roofitresult(rfile, fitres = "fit_s"):
    result = rfile.Get(fitres)
    if not isinstance(result, ROOT.RooFitResult):
        result = rfile.Get("fit_mdf")
        if not isinstance(result, ROOT.RooFitResult):
            result = None
    if result and not is_good_fit(result):
        result = None
    
    return result

def load_variable(result, parname):
    var = result.floatParsFinal().find(parname)
    if isinstance(var, ROOT.RooRealVar):
        return var

def load_bestfit(files, paramname, results, keyword):
    print("Loading from files:")
    print(files)
    for fpath in files:
        # if not paramname in fpath:
        #     print("WARNING: Could not find '{param}' in path name '{fpath}'! Skipping".format(
        #         param = paramname,
        #         fpath = fpath
        #     ))
        #     continue
        if not os.path.exists(fpath):
            print("WARNING: file {} does not exist!".format(fpath))
            continue
        f = ROOT.TFile.Open(fpath)
        if not (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
            print("File '{}' is broken, skipping".format(fpath))
            continue
        fit = load_roofitresult(rfile = f)
        if fit is None:
            print("Fit in file '{}' is broken, skipping".format(fpath))
            continue
        par = load_variable(result = fit, parname = paramname)
        if par is None:
            print(" ".join(
                """WARNING: Could not load parameter '{par}'
                from file {file}""".format(par=paramname, file = fpath).split()
                    )   
                  )
            continue
        if keyword in results:
            print("WARNING: keyword '{}' is already in results dict!".format(keyword))
            keyword += "_new"
        results[keyword] = {"value" : par.getVal(), "down" : par.getErrorLo(), "up" : par.getErrorHi()}

def load_significance(files, paramname, results, keyword):
    print("Loading from files:")
    print(files)
    for fpath in files:
        if not paramname in fpath:
            print("WARNING: Could not find '{param}' in path name '{fpath}'! Skipping".format(
                param = paramname,
                fpath = fpath
            ))
            continue
        if not os.path.exists(fpath):
            print("WARNING: file {} does not exist!".format(fpath))
            continue
        f = ROOT.TFile.Open(fpath)
        if not (f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered)):
            print("File '{}' is broken, skipping".format(fpath))
            continue
        sigtree = f.Get("limit")
        if not isinstance(sigtree, ROOT.TTree):
            print("Significance in file '{}' is broken, skipping".format(fpath))
            continue
        signi = "--"
        for e in sigtree:
            signi = sigtree.limit
        if keyword in results:
            print("WARNING: keyword '{}' is already in results dict!".format(keyword))
            keyword += "_new"
        results[keyword] = signi

def dump_json(outname, allvals):
    if len(allvals) > 0:
        print "opening file", outname
        with open(outname, "w") as outfile:
            json.dump(allvals, outfile, indent = 4, separators = (',', ': '))
    else:
        print "given dictionary is empty, will not create '%s'" % outname

def prepare_files(infiles):
    return_dict = {}
    for f in infiles:
        tmp = os.path.basename(f)
        #remove root extension
        tmp = tmp.split(".")[0]
        if tmp.endswith("2D"):
            tmp = "_".join(tmp.split("_")[:-4])
        return_dict[f] = tmp
    return return_dict

def filter_files(infiles, exclude_crits, must_include = []):
    print("FILTER_FILES: input")
    print(infiles)
    tmp = prepare_files(infiles)
    l = [f for f in tmp if not any(c in tmp[f] for c in exclude_crits)]
    l = [f for f in l if all(c in tmp[f] for c in must_include)]
    print("FILTER_FILES: output")
    print(l)
    return l

def main(options, files):
    #load options
    parameters = options.parameters
    do_bestfits = options.do_bestfit
    do_statonly = options.do_statonly
    do_signi = options.do_signi
    key_bestfit = options.bestFitKey
    key_statonly = options.statOnlyKey
    key_signi = options.signiKey
    outname = options.outfile
    
    #initialize dictionary for results
    results = {}
    for p in parameters:
        print("="*130)
        print("Collecting results for param {}".format(p))
        print("="*130)
        # if not p in results:
        #     results[p] = {}
        others = [par for par in parameters if not par == p]
        if "r" in others:
            others.pop(others.index("r"))
        #load bestfits
        # infiles = filter_files(infiles = files, exclude_crits = others, must_include= [p])
        infiles = filter_files(infiles = files, exclude_crits = others)
        pardict = dict()
        if do_bestfits:
            print("="*130)
            print("Collecting bestfits")
            print("="*130)
            files_bestfit = filter(infiles, "*{}*".format(key_bestfit))
            files_bestfit = filter_files(infiles = files_bestfit, exclude_crits = [key_statonly, key_signi])
            load_bestfit(files = files_bestfit, paramname = p, results = pardict, keyword = "bestfit")
        if do_statonly:
            print("="*130)
            print("Collecting stat-only")
            print("="*130)
            files_statonly = filter(infiles, "*{}*".format(key_statonly))
            files_statonly = filter_files(infiles = files_statonly, exclude_crits = [key_bestfit, key_signi])
            load_bestfit(files = files_statonly, paramname = p, results = pardict, keyword = "stat_only")
        if do_signi:
            print("="*130)
            print("Collecting significances")
            print("="*130)
            files_signi = filter(infiles, "*{}*".format(key_signi))
            files_signi = filter_files(infiles = files_signi, exclude_crits = [key_bestfit, key_statonly])
            load_significance(files = files_signi, paramname = p, results = pardict, keyword = "significance")
        if not len(pardict) == 0:
            results[p] = deepcopy(pardict)
    dump_json(outname = outname, allvals = results)

if __name__ == '__main__':
    options, files = parse_arguments()
    main(options, files)
    