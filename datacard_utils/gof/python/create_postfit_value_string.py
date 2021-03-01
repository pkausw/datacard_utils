import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import sys


changedict = {
    "CMS_ttHbb_FSR_ttbarOther_2017" : "CMS_ttHbb_FSR_ttbarOther",
    "CMS_ttHbb_FSR_ttbarPlus2B_2017": "CMS_ttHbb_FSR_ttbarPlus2B",
    "CMS_ttHbb_FSR_ttbarPlusB_2017" : "CMS_ttHbb_FSR_ttbarPlusB",
    "CMS_ttHbb_FSR_ttbarPlusBBbar_2017" : "CMS_ttHbb_FSR_ttbarPlusBBbar",
    "CMS_ttHbb_FSR_ttbarPlusCCbar_2017": "CMS_ttHbb_FSR_ttbarPlusCCbar",
    "CMS_ttHbb_ISR_ttbarOther_2017": "CMS_ttHbb_ISR_ttbarOther",
    "CMS_ttHbb_ISR_ttbarPlus2B_2017": "CMS_ttHbb_ISR_ttbarPlus2B",
    "CMS_ttHbb_ISR_ttbarPlusB_2017" : "CMS_ttHbb_ISR_ttbarPlusB",
    "CMS_ttHbb_ISR_ttbarPlusBBbar_2017" : "CMS_ttHbb_ISR_ttbarPlusBBbar",
    "CMS_ttHbb_ISR_ttbarPlusCCbar_2017" : "CMS_ttHbb_ISR_ttbarPlusCCbar",
    "CMS_ttHbb_PDF_2017" : "CMS_ttHbb_PDF",
    "CMS_ttHbb_bgnorm_ttbarPlus2B_2017" : "CMS_ttHbb_bgnorm_ttbarPlus2B",
    "CMS_ttHbb_bgnorm_ttbarPlusBBbar_2017" : "CMS_ttHbb_bgnorm_ttbarPlusBBbar",
    "CMS_ttHbb_bgnorm_ttbarPlusB_2017" : "CMS_ttHbb_bgnorm_ttbarPlusB",
    "CMS_ttHbb_bgnorm_ttbarPlusCCbar_2017" : "CMS_ttHbb_bgnorm_ttbarPlusCCbar"
}

def load_roofitresult(rfile, results = "fit_s"):
    result = rfile.Get(results)
    if not isinstance(result, ROOT.RooFitResult):
        result = rfile.Get("fit_mdf")
        if not isinstance(result, ROOT.RooFitResult):
            return None
    if not (result.status() == 0 and result.covQual() == 3):
        print "Detected problems with fit in %s!\n" % rfile.GetName()
        print "\tFit Status (should be 0): %s\n" % str(result.status())
        print "\tCovariance Matrix Quality (should be 3): %s\n" % str(result.covQual())
    return result

def load_variable(result, parname):
    var = result.floatParsFinal().find(parname)
    if isinstance(var, ROOT.RooRealVar):
        return var

def getValues(f, results = "fit_s"):
    result = load_roofitresult(rfile = f, results = results)
    vals = []
    if result:
        variables = result.floatParsFinal().contentsString().split(",")
        for var in variables:
            if "prop_bin" in var: continue
            v = load_variable(result = result, parname = var)
            if v:
                if var in changedict: var = changedict[var]
                vals.append("{0}={1}".format(var, v.getVal()))
            else:
                print "could not load %s from %s" % (var, f.GetName())
    else:
        print "could not load fit_s from %s" % f.GetName()
    return vals

def create_postfit_input_cmd(rfile, fit = "fit_s"):
    r = None
    allvals = getValues(f = rfile, results = fit)
    vals = []
    s = ""
    for v in allvals:
        parts = v.split("=")
        vname = parts[0]
        if vname == "r":
            r = parts[1]
        else:
            vals.append(v)
    if len(vals) > 0:
        s = "--setParameters %s --freezeParameters all" % ",".join(vals)
        if not r is None:
            s += " --fixedSignalStrength " + str(r)
    else:
        print "ERROR: Did not find any values in file", rfile.GetName()
    return s

def main(args = sys.argv[1:]):
    postfit_filepath = args[0]
    fit = "fit_b"
    if len(args)>1:
        fit = args[1]
    if not os.path.exists(postfit_filepath):
        sys.exit("Path '%s' does not exist!")
    rfile = ROOT.TFile(postfit_filepath)
    if not rfile.IsOpen() or rfile.IsZombie() or rfile.TestBit(ROOT.TFile.kRecovered):
        sys.exit("File '%s' is corrupted!" % postfit_filepath)

    s = create_postfit_input_cmd(rfile = rfile, fit = fit)
    if not s == "":
        print "use the following string in your fit command to set all nuisances to their postfit value and fix them there:"
        print s

if __name__ == '__main__':
    main()