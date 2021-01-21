import numpy as np
from ROOT import TH2F, TCanvas, gStyle, TLatex, TAxis, TLine, TGraphErrors, TGraphAsymmErrors, TLegend, kGreen, kYellow, TPaveText, gROOT
import json
from pprint import pprint
import sys

gROOT.SetBatch(1)

# results_json = "ParamEvolution.json"
# results_json = "ParamEvolutionfromImpacts.json"
results_json = sys.argv[1]

# Which result? Options: "17", "16p17"
# result_version = "17" 
#result_version = "16p17" 

poi_selection = "r"
fontsize = 0.04

paramsToDraw=[
    "CMS_ttHbb_bgnorm_ttbb",
    "CMS_ttHbb_bgnorm_ttcc",
    "CMS_btag_lf",
    "CMS_ttHbb_scaleMuF_ttbbNLO",
    "CMS_ttHbb_scaleMuR_ttbbNLO",
    "CMS_btag_cferr2",
    "CMS_eff_e_2018",
    "QCDscale_VV"
]
with open( results_json, "r" ) as in_file:
    paramsToDraw = json.load(in_file)["allParams"]
paramsToDraw = [ x for x in paramsToDraw if "prop_bin" not in x ]
print(paramsToDraw)
# exit()


combinationsToDraw = [

    "combined_DL_2016_DNN",
    "combined_DL_2017_DNN",
    "combined_DL_2018_DNN",
    "combined_DL_all_years_DNN",

    "combined_FH_2016_DNN",
    "combined_FH_2017_DNN",
    "combined_FH_2018_DNN",
    "combined_FH_all_years_DNN",

    "combined_SL_2016_DNN",
    # "combined_SL_2016_DNN_ge4j_3t",
    # "combined_SL_2016_DNN_ge4j_ge4t",
    "combined_SL_2017_DNN",
    # "combined_SL_2017_DNN_ge4j_3t",
    # "combined_SL_2017_DNN_ge4j_ge4t",
    "combined_SL_2018_DNN",
    # "combined_SL_2018_DNN_ge4j_3t",
    # "combined_SL_2018_DNN_ge4j_ge4t",
    "combined_SL_all_years_DNN",
    # "combined_SL_all_years_DNN_ge4j_3t",
    # "combined_SL_all_years_DNN_ge4j_ge4t",

    "combined_full_2016_baseline_v01",
    "combined_full_2017_baseline_v01",
    "combined_full_2018_baseline_v01",
    "combined_full_all_years_baseline_v01",

    "combined_DLFHSL_2016_baseline_v01",
    "combined_DLFHSL_2017_baseline_v01",
    "combined_DLFHSL_2018_baseline_v01",
    "combined_DLFHSL_all_years_baseline_v01",
    # "combined_DLSL_2016_baseline_v01",
    # "combined_DLSL_2017_baseline_v01",
    # "combined_DLSL_2018_baseline_v01",
    # "combined_DLSL_all_years_baseline_v01",
]



naming = {
    "combined_DLFHSL_2016_baseline_v01": "DL+FH+SL 2016",
    "combined_DLFHSL_2017_baseline_v01": "DL+FH+SL 2017",
    "combined_DLFHSL_2018_baseline_v01": "DL+FH+SL 2018",
    "combined_DLFHSL_all_years_baseline_v01": "DL+FH+SL all years",
    "combined_DLSL_2016_baseline_v01": "DL+SL 2016",
    "combined_DLSL_2017_baseline_v01": "DL+SL 2017",
    "combined_DLSL_2018_baseline_v01": "DL+SL 2017",
    "combined_DLSL_all_years_baseline_v01": "DL+SL all years",
    "combined_DL_2016_DNN": "DL 2016",
    "combined_DL_2017_DNN": "DL 2017",
    "combined_DL_2018_DNN": "DL 2018",
    "combined_DL_all_years_DNN": "DL all years",
    "combined_FH_2016_DNN": "FH 2016",
    "combined_FH_2017_DNN": "FH 2017",
    "combined_FH_2018_DNN": "FH 2018",
    "combined_FH_all_years_DNN": "FH all years",
    "combined_SL_2016_DNN": "SL 2016",
    "combined_SL_2016_DNN_ge4j_3t": "SL 2016 4j3b",
    "combined_SL_2016_DNN_ge4j_ge4t": "SL 2016 4j4b",
    "combined_SL_2017_DNN": "SL 2017",
    "combined_SL_2017_DNN_ge4j_3t": "SL 2017 4j3b",
    "combined_SL_2017_DNN_ge4j_ge4t":"SL 2017 4j4b",
    "combined_SL_2018_DNN": "SL 2018",
    "combined_SL_2018_DNN_ge4j_3t": "SL 2018 4j3b",
    "combined_SL_2018_DNN_ge4j_ge4t": "SL 2018 4j4b",
    "combined_SL_all_years_DNN": "SL all years",
    "combined_SL_all_years_DNN_ge4j_3t": "SL all years 4j3b",
    "combined_SL_all_years_DNN_ge4j_ge4t": "SL all years 4j3b",
    "combined_full_2016_baseline_v01": "DL+FH+SL+DLCR 2016",
    "combined_full_2017_baseline_v01": "DL+FH+SL+DLCR 2017",
    "combined_full_2018_baseline_v01": "DL+FH+SL+DLCR 2018",
    "combined_full_all_years_baseline_v01": "DL+FH+SL+DLCR all years"
}

def draw_Evolution( results_json, paramToDraw = "CMS_ttHbb_bgnorm_ttbb"):

    with open( results_json, "r" ) as in_file:
        res = json.load(in_file)[poi_selection]
    # pprint(res)
    combs = []
    nCombs = 0
    channels = []
    bestfit = []
    upper = []
    lower = []

    print("############")
    print("Drawing param: {}".format(paramToDraw))
    print("############")

    for i,combination in enumerate(combinationsToDraw):
        try:
            bestfit.append(res[combination][paramToDraw]["bestfit"]["value"])
            upper.append(res[combination][paramToDraw]["bestfit"]["up"])
            lower.append(abs(res[combination][paramToDraw]["bestfit"]["down"]))
            channels.append(2+3*nCombs-0.5)
            combs.append(combination)
            nCombs=nCombs+1

        except:
            print("skipping {}".format(combination))
            continue



    # upper, bestfit, combs, lower = zip(*sorted(zip(upper, bestfit, combs, lower)))
    # combs, upper, bestfit,lower = zip(*sorted(zip(combs, upper, bestfit, lower)))
    zero = np.zeros(nCombs)
    # print(nCombs)
    # print(combs)
    # print(bestfit)
    # print(upper)
    # print(lower)
    # print(channels)
    xmin = -1.5
    xmax = 3.0

    bestfit = np.array(bestfit)
    upper = np.array(upper)
    lower = np.array(lower)
    channels = np.array(channels)

    # c,h = draw_canvas_histo( combs, xmin, xmax, "#hat{#theta}" )
    c,h = draw_canvas_histo( combs, xmin, xmax, paramToDraw )

    # line at SM expectation of mu = 1
    l = TLine()
    l.SetLineStyle( 2 )
    l.DrawLine( 1.0, 0, 1.0, 3*nCombs+0.5 )

    l0 = TLine()
    l0.SetLineStyle( 2 )
    l0.DrawLine( 0.0, 0, 0.0, 3*nCombs+0.5 )

    lmin1 = TLine()
    lmin1.SetLineStyle( 2 )
    lmin1.DrawLine( -1.0, 0, -1.0, 3*nCombs+0.5 )

    gmu_tot = TGraphAsymmErrors( nCombs, bestfit, channels, lower, upper, zero, zero )
    gmu_tot.SetMarkerStyle( 1 )
    gmu_tot.SetMarkerSize( 1 )
    gmu_tot.SetMarkerColor( 4 )
    gmu_tot.SetLineColor( 4 )
    gmu_tot.SetLineWidth( 2 )
    gmu_tot.Draw( "p" )
    # gmu_tot.Print()

    # gmu = TGraphAsymmErrors( nchannels, mu, channels, lower_stat, upper_stat, zero, zero )
    # gmu.SetMarkerStyle( 21 )
    # gmu.SetMarkerSize( 1.5 )
    # gmu.SetMarkerColor( 1 )
    # gmu.SetLineColor( 2 )
    # gmu.SetLineWidth( 2 )
    # gmu.Draw( "pe1same" )

    # leg = TLatex();
    # leg.SetTextFont( 42 )
    # leg.SetTextSize( 0.035 )
    # leg.SetTextAlign( 11 )
    # leg.DrawLatex( 4.5, 3.1*nCombs, "#mu      #color[4]{tot}    #color[2]{stat}    syst" )

    for ich,channel in enumerate(channels):
        res = TLatex();
        res.SetTextFont( 42 )
        res.SetTextSize( 0.045 )
        res.SetTextSize( 0.03 )
        res.SetTextAlign( 31 )
        res.DrawLatex( xmax-0.05*xmax, channel-0.25,
                        ("%.2f #color[4]{+%.2f -%.2f}"
                        %
                        (bestfit[ich],upper[ich],lower[ich]) ))
                        # ("%.2f #color[4]{{}^{+%.2f}_{ -%.2f}}"
                    #    ("{bestfit}{}^{+ {upper} }_{- {lower} }".format(bestfit = round(bestfit[ich],2), upper=round(upper[ich],2), lower=round(lower[ich],2)) ))
                    #    ("{bestfit} {upper} {lower}".format(bestfit = round(bestfit[ich],2), upper=round(upper[ich],2), lower=round(lower[ich],2)) ))
                    #  ("{bestfit} #color[4]{{}^{+ {upper} }_{- {lower} }}".format(bestfit = bestfit[ich],upper=upper[ich],lower=lower[ich])))

  
    
    #draw_disclaimer()

    c.RedrawAxis()    
    c.Modified()
    c.Update()
                
    c.SaveAs( "paramEvo/HIG-19-011_Evo_"+ paramToDraw +".png" ) 
    c.SaveAs( "paramEvo/HIG-19-011_Evo_"+ paramToDraw +".pdf" ) 

def draw_canvas_histo( combinations, xmin, xmax, title ):
    c = TCanvas( "c", "Canvas",800,750)
    c.Draw()
    nCombs = len(combinations)
    #h = TH2F( "h", "", 10, xmin, xmax, 3*nCombs+2, 0, 3*nCombs+2 )
    h = TH2F( "h", "", 10, xmin, xmax, int(3.5*nCombs), 0, int(3.5*nCombs) )
    # h = TH2F( "h", "", 10, xmin, xmax, int(nCombs), 0, int(nCombs) )
    h.Draw()
    h.SetStats( 0 )
    h.SetXTitle( title )

    yaxis = h.GetYaxis()
    # yaxis.SetLabelSize( 0.065 )
    yaxis.SetLabelSize( 0.03 )
    for i, comb in enumerate(combinations):
        yaxis.SetBinLabel(int(2+3*(i)), naming[comb] )
        # print(comb)
        # print(yaxis.GetBinCenter(int(2+3*(i))))


    pub = TLatex();
    pub.SetNDC()
    pub.SetTextFont( 42 )
    pub.SetTextSize( 0.05 )
    pub.SetTextAlign( 13 )
    pub.DrawLatex( gStyle.GetPadLeftMargin()+0.03,
                   1.-gStyle.GetPadTopMargin()-0.033,
                   #"#bf{CMS}" )
                   "#bf{CMS} #it{Preliminary}")

    lumi = TLatex();
    lumi.SetNDC()
    lumi.SetTextFont( 42 )
    lumi.SetTextSize( 0.035 )
    lumi.SetTextAlign( 31 )
    lumi.DrawLatex( 1-gStyle.GetPadRightMargin(), 0.965, "(13 TeV)" )
    # if result_version == "17":
    #     lumi.DrawLatex( 1-gStyle.GetPadRightMargin(), 0.965, "41.5 fb^{-1} (13 TeV)" )
    # elif result_version == "16p17":
    #     lumi.DrawLatex( 1-gStyle.GetPadRightMargin(), 0.965, "35.9 fb^{-1} (2016) + 41.5 fb^{-1} (2017) (13 TeV)" )


    return c,h


def my_style():
    
#    gStyle.SetLabelSize( fontsize, "x" );
#    gStyle.SetLabelSize( fontsize, "y" );
#    gStyle.SetLabelSize( fontsize, "z" );
#
#    gStyle.SetTitleSize( fontsize, "x" );
#    gStyle.SetTitleSize( fontsize, "y" );
#    gStyle.SetTitleSize( fontsize, "z" );
#
    gStyle.SetTitleOffset( 1.5, "xy" );
    gStyle.SetTitleFont( 62, "bla" );

    gStyle.SetFrameLineWidth(2)
    gStyle.SetPadLeftMargin(0.26);
    gStyle.SetPadBottomMargin(0.14)
    gStyle.SetPadTopMargin(0.05)
    gStyle.SetPadRightMargin(0.02)

    gStyle.SetTitleColor(1,"XYZ")
    gStyle.SetLabelColor(1,"XYZ")
    gStyle.SetLabelFont(42,"XYZ")
    gStyle.SetLabelOffset(0.007,"XYZ")
    gStyle.SetLabelSize(0.038,"XYZ")
    gStyle.SetTitleFont(42,"XYZ")
    gStyle.SetTitleSize(0.05,"XYZ")
    gStyle.SetTitleXOffset(1.3)
    gStyle.SetTitleYOffset(1.3)

    gStyle.SetStatX( 0.88 );
    gStyle.SetStatY( 0.87 );
    gStyle.SetNdivisions( 505 );
    gStyle.SetTickLength(0.04,"XZ")
    gStyle.SetTickLength(0,"Y");
    gStyle.SetPadTickX(1)
    gStyle.SetEndErrorSize(6)

    gStyle.SetCanvasColor(-1); 
    gStyle.SetPadColor(-1); 
    gStyle.SetFrameFillColor(-1); 
    gStyle.SetTitleFillColor(-1); 
    gStyle.SetFillColor(-1); 
    gStyle.SetFillStyle(4000); 
    gStyle.SetStatStyle(0); 
    gStyle.SetTitleStyle(0); 
    gStyle.SetCanvasBorderSize(0); 
    gStyle.SetFrameBorderSize(0); 
    gStyle.SetLegendBorderSize(0); 
    gStyle.SetStatBorderSize(0); 
    gStyle.SetTitleBorderSize(0); 
    
if __name__ == '__main__':
    my_style()
    #limits()
    # for param in reversed(paramsToDraw):
    for param in paramsToDraw:
        draw_Evolution(results_json,param)
