import ROOT
import glob
from argparse import ArgumentParser
import os
import sys
import json

thisdir = os.path.realpath(os.path.dirname(__file__))
if not thisdir in sys.path:
    sys.path.append(thisdir)

from base.CMS_pad import CMS_pad

ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gStyle.SetPaintTextFormat(".3f")

#ROOT.gStyle.SetOptTitle(0)


def create_matrix(
    fitResult,
    params,
    name,
    outpath,
    param_names,
    xlabelsize=0.03,
    ylabelsize=0.03,
    textsize=1.8,
):
    # canvas = ROOT.TCanvas(name, "", 2524, 2524)
    canvas = CMS_pad(extraText="", left_margin=0.12,
                     right_margin=0.14, bottom_margin=0.15, top_margin=0.1,
                     width=2524, height=2524
                     )
    # canvas.getCanvas().SetRightMargin(.15)
    # canvas.SetLeftMargin(0.15)
    # canvas.SetBottomMargin(0.15)
    corr_mat = ROOT.TH2F("cor_{}".format(name),"",len(params),0,len(params),len(params),0,len(params))
    corr_mat.SetStats(0)
    corr_mat.GetXaxis().SetLabelSize(xlabelsize)
    corr_mat.GetYaxis().SetLabelSize(ylabelsize)



    for i,p1 in enumerate(params, 1):

        corr_mat.GetXaxis().SetBinLabel(i,param_names.get(p1, p1))
        for j,p2 in enumerate(params, 1):
            corr_mat.GetYaxis().SetBinLabel(j,param_names.get(p2, p2))
            corr_mat.SetBinContent(i,j,fitResult.correlation(p1, p2))

    # corr_mat.GetXaxis().LabelsOption("v")
    corr_mat.SetMarkerColor(ROOT.kWhite)
    corr_mat.GetZaxis().SetRangeUser(-1,1)
    # corr_mat.SetTitle(name)
    if len(params)<10:
        corr_mat.SetMarkerSize(textsize)
        corr_mat.Draw("colz text1")
    else:
        corr_mat.Draw("colz")
    outname = os.path.join(outpath, name)
    canvas.saveCanvas(outname=outname)
    return corr_mat


def main():
    """
    USE: python corrMat.py --fit=TYPE OF FIT
    """


    # parser = optparse.OptionParser(usage=usage)

    parser = ArgumentParser()

    parser.add_argument("-f", "--fit", dest="fit",default="fit_s",
            help="TYPE of the used fit (fit_s, fit_b, fit_mdf). Defaults to 'fit_s'",
            metavar="fit"
        )

    parser.add_argument("-o","--outPath", dest="outpath",
            help="saves copy of Correlation Matrix to given path. Defaults to '.'",
            metavar="outPath", default = "."
        )
    parser.add_argument("results", metavar="path/to/results.root",
                        help=" ".join("""
                        paths to root files containing the RooFitResult objects
                        containing the postfit correlation matrices
                        """.split()),
                        nargs="+",
                    )
    parser.add_argument("-t", "--translation-file", dest="translation_file",
                        help=" ".join(
                            """
                            path to .json file containing map of the form
                            {
                                PARAMETER_NAME: PARAMETER_CLEAR_NAME
                            }
                            """.split()
                        )
                    )
    parser.add_argument("-a", "--additional-parameters",
                        metavar="list of parameters to draw correlation for",
                        nargs="+",
                        help=" ".join("""
                            draw an additional correlation matrix for these parameters
                            """.split()),
                        dest="additional_parameters",
                    )

    args = parser.parse_args()


    #path_to_file = '/nfs/dust/cms/user/jschindl/combine/Masterarbeit/*/*/powheg_vs_OL*/sig*/PseudoExperiment1/fitDiagnostics.root'
    list_of_paths = args.results
    fit_name = args.fit
    outpath = args.outpath

    param_names = dict()
    if args.translation_file:
        with open(args.translation_file) as f:
            param_names = json.load(f)

    additional_params = args.additional_parameters
    for diagnostics_file in list_of_paths:
        print(diagnostics_file)
        ROOT_file = ROOT.TFile(diagnostics_file)
        name=os.path.basename(diagnostics_file)
        name = ".".join(name.split(".")[:-1])
        name = "_".join(["corMat", name, fit_name])
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        outrootpath = os.path.join(outpath, name+".root")
        outroot = ROOT.TFile.Open(outrootpath, "RECREATE")

        fit_s = ROOT_file.Get(fit_name)
        params = fit_s.floatParsFinal().contentsString().split(",")
        #params = [a for a in params if a.endswith("ttbbCR") or "bgnorm" in a]
        params = [a for a in params if not "prop_bin" in a]
        print(params)
        sigparams = fit_s.floatParsFinal().contentsString().split(",")
        sigparams = [a for a in sigparams if ('prop_bin' not in a and a.startswith("r"))]
        sigparams = sorted(sigparams)
        if any("_" in x for x in sigparams):
            sigparams = sorted(sigparams, key = lambda x: int(x.split("_")[-2]) if x.count("_") == 4 else x.split("_")[-1])
        print(sigparams)

        corr_mat = create_matrix(fitResult = fit_s, params = params, name = name, outpath = outpath, param_names=param_names)    
        # outroot.WriteTObject(corr_mat, corr_mat.GetName())
        outroot.WriteTObject(corr_mat, corr_mat.GetName())

        corrMat = create_matrix(
            fitResult=fit_s,
            params=sigparams,
            name=name+"_Sig",
            outpath=outpath,
            param_names=param_names,
            xlabelsize=0.1,
            ylabelsize=0.1
        )
        
        # outroot.WriteTObject(corrMat, corrMat.GetTitle())
        outroot.WriteTObject(corrMat, corrMat.GetTitle())

        if additional_params:
            print(additional_params)
            these_params = [x for x in additional_params if x in params]
            print(these_params)
            corrMat = create_matrix(
                fitResult = fit_s,
                params = these_params,
                name = name+"_add_params",
                outpath = outpath,
                param_names=param_names
            )
            outroot.WriteTObject(corrMat, corrMat.GetTitle())

        outroot.Close()
        ROOT_file.Close()

if __name__ == '__main__':
    main()
