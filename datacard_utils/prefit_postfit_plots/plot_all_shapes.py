import os
import sys

import ROOT
from subprocess import call

thisdir = os.path.dirname(os.path.realpath(__file__))
plotscript_path = os.path.join(thisdir, "PlotScript.py")
#plot_config_path = os.path.join(thisdir, "plotconfig_FHCRs.py")
plot_config_path = os.path.join(thisdir, "plotconfig_STXS.py")
cmd_base_parts = "python {scriptpath} -p {plotconfigpath}".split()
cmd_base_parts += "-w . --drawFromHarvester".split()
cmd_base_parts += "--combineflag {flag} -r {rootfile}".split()
cmd_base_parts += "--channelname {channel}".split()
# cmd_base_parts += "--combineDatacard {datacard}".split()
cmd_base_parts += "--pdfname {pdf_name}".split()
cmd_base_parts += '--xLabel "{xLabel}"'.split()
cmd_base_parts += ['--multisignal']
cmd_base_parts += ['--divideByBinWidth']
#cmd_base_parts += ["--plot-blind"]
cmd_base = " ".join(cmd_base_parts)

def main(infilepath, lumi, xLabel = ""):
    if not os.path.exists(infilepath):
        sys.exit("ERROR: could not find file in path '{}'".format(infilepath))
    fname = os.path.basename(infilepath)
    fname = ".".join(fname.split(".")[:-1])
    infile = ROOT.TFile.Open(infilepath)
    categories = [x.GetName() for x in infile.GetListOfKeys() if x.IsFolder()]

    for cat in categories:
        # for flag in "shapes_prefit shapes_fit_s".split():
        # if not cat.startswith("total"): continue
        name = "_".join(cat.split("_")[:-1])
        # pdf_name = "{}_total".format(fname)
        pdf_name = name
        if cat.endswith("prefit"):
            flag = "shapes_prefit"
        else:
            flag = "shapes_fit_s"
        cmd = cmd_base.format(scriptpath = plotscript_path,
                                    plotconfigpath = plot_config_path,
                                    flag = flag,
                                    rootfile = infilepath,
                                    channel = name,
                                    xLabel = xLabel,
                                    pdf_name=pdf_name
                                )
        if lumi:
            cmd += " --lumilabel {}".format(lumi)
        print(cmd)
        call([cmd], shell=True)
if __name__ == '__main__':
    infilepath = sys.argv[1]
    lumi = None
    xLabel=""
    if len(sys.argv) > 2:
        xLabel = sys.argv[2]
    if len(sys.argv) > 3:
        lumi = sys.argv[3]
    main(infilepath = infilepath, lumi = xLabel, xLabel = lumi)
