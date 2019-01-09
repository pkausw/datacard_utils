import numpy as np
from ROOT import TH2F, TCanvas, gStyle, TLatex, TAxis, TLine, TGraphErrors, TGraphAsymmErrors, TLegend, kGreen, kYellow, TPaveText

nchannels = 5
fontsize = 0.04


def get_cms_label():
    label = TPaveText(
        gStyle.GetPadLeftMargin()+0.03,
        1.-gStyle.GetPadTopMargin()-0.12,
        1.-gStyle.GetPadRightMargin(), 1.#,
#        "NDC"
    )
    #label.AddText("#scale[1.5]{#bf{CMS}}")
    label.AddText("#scale[1.5]{#bf{CMS}} #scale[1.1]{#it{Preliminary}}")
    label.SetFillColor(0)
    label.SetFillStyle(0)
    label.SetBorderSize(0)
    label.SetTextFont(43)
    label.SetTextSize(26)
    label.SetMargin(0.)
    label.SetTextAlign(13)

    return label

    

def bestfit():
    
    xmin = -1.0
    xmax = 7

    c,h = draw_canvas_histo( xmin, xmax, "Best-fit #hat{#mu} = #hat{#sigma}/#sigma_{SM}" )

    # line at SM expectation of mu = 1
    l = TLine()
    l.SetLineStyle( 2 )
    l.DrawLine( 1.0, 0, 1.0, 3*nchannels+0.5 )


    if nchannels == 4:
        # FH, SL, DL, comb
        mu    = np.array( [ 1.00, 1.00, 1.00, 1.00 ] )
        upper = np.array( [ 1.22, 0.41, 0.85, 0.36 ] )
        lower = np.array( [ 1.27, 0.38, 0.80, 0.33 ] )
        upper_stat = np.array( [ 0., 0., 0., 0. ] )
        lower_stat = np.array( [ 0., 0., 0., 0. ] )
        upper_syst = np.array( [ 0., 0., 0., 0. ] )
        lower_syst = np.array( [ 0., 0., 0., 0. ] )
        channels = np.array( [ 10.5, 7.5, 4.5, 1.5 ] )
        zero    = np.zeros( nchannels )

    elif nchannels == 5:
        # FH, SL, DL, comb, comb16+17
        mu    = np.array( [ 1.00, 1.00, 1.00, 1.00, 1.00 ] )
        upper = np.array( [ 1.22, 0.41, 0.85, 0.36, 0.30 ] )
        lower = np.array( [ 1.27, 0.38, 0.80, 0.33, 0.27 ] )
        upper_stat = np.array( [ 0., 0., 0., 0., 0. ] )
        lower_stat = np.array( [ 0., 0., 0., 0., 0. ] )
        upper_syst = np.array( [ 0., 0., 0., 0., 0. ] )
        lower_syst = np.array( [ 0., 0., 0., 0., 0. ] )
        channels = np.array( [ 13.5, 10.5, 7.5, 4.5, 1.5 ] )
        zero    = np.zeros( nchannels )

    gmu_tot = TGraphAsymmErrors( nchannels, mu, channels, lower, upper, zero, zero )
    gmu_tot.SetMarkerStyle( 1 )
    gmu_tot.SetMarkerSize( 1 )
    gmu_tot.SetMarkerColor( 4 )
    gmu_tot.SetLineColor( 4 )
    gmu_tot.SetLineWidth( 2 )
    gmu_tot.Draw( "p" )

    gmu = TGraphAsymmErrors( nchannels, mu, channels, lower_stat, upper_stat, zero, zero )
    gmu.SetMarkerStyle( 21 )
    gmu.SetMarkerSize( 1.5 )
    gmu.SetMarkerColor( 1 )
    gmu.SetLineColor( 2 )
    gmu.SetLineWidth( 2 )
    gmu.Draw( "pe1same" )


    leg = TLatex();
    leg.SetTextFont( 42 )
    leg.SetTextSize( 0.035 )
    leg.SetTextAlign( 11 )
    leg.DrawLatex( 3.5, 3.1*nchannels, "#mu      #color[4]{tot}    #color[2]{stat}    syst" )

    for ich,channel in enumerate(channels):
        res = TLatex();
        res.SetTextFont( 42 )
        res.SetTextSize( 0.045 )
        res.SetTextAlign( 31 )
        res.DrawLatex( 6.75, channel-0.2,
                       ("%.2f #color[4]{{}^{+%.2f}_{ -%.2f}} #color[2]{{}^{+%.2f}_{ -%.2f}} {}^{+%.2f}_{ -%.2f}"
                        %
                        (mu[ich],upper[ich],lower[ich],
                         upper_stat[ich],lower_stat[ich],
                         upper_syst[ich],lower_syst[ich])) )

  
    
    #draw_disclaimer()

    c.RedrawAxis()    
    c.Modified()
    c.Update()
    if nchannels == 4:
        c.SaveAs( "HIG-18-030_bestfit_2017.pdf" )
    elif nchannels == 5:
        c.SaveAs( "HIG-18-030_bestfit_2016p2017.pdf" )
                
        #c.SaveAs( "HIG-18-030_bestfit.png" ) 

def draw_canvas_histo( xmin, xmax, title ):
    c = TCanvas( "c", "Canvas",800,750)
    c.Draw()
    
    h = TH2F( "h", "", 10, xmin, xmax, 3*nchannels+2, 0, 3*nchannels+2 )
    h.Draw()
    h.SetStats( 0 )
    h.SetXTitle( title )

    yaxis = h.GetYaxis()
    yaxis.SetLabelSize( 0.065 )
    if nchannels == 4:
        yaxis.SetBinLabel( 11, "Fully-hadronic" )
        yaxis.SetBinLabel(  8, "Single-lepton" )
        yaxis.SetBinLabel(  5, "Dilepton" )
        yaxis.SetBinLabel(  2, "Combined" )
    elif nchannels == 5:
        yaxis.SetBinLabel( 14, "Fully-hadronic" )
        yaxis.SetBinLabel( 11, "Single-lepton" )
        yaxis.SetBinLabel(  8, "Dilepton" )
        yaxis.SetBinLabel(  5, "Combined" )
        yaxis.SetBinLabel(  2, "2016+2017" )

    # separating combined result
    l1 = TLine()
    l1.SetLineStyle( 1 )
    l1.DrawLine( xmin, 3, xmax, 3 )
    if nchannels == 5:
        l2 = TLine()
        l2.SetLineStyle( 1 )
        l2.DrawLine( xmin, 6, xmax, 6 )

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
    if nchannels == 4:
        lumi.DrawLatex( 1-gStyle.GetPadRightMargin(), 0.965, "41.5 fb^{-1} (13 TeV)" )
    elif nchannels == 5:
        lumi.DrawLatex( 1-gStyle.GetPadRightMargin(), 0.965, "77.4 fb^{-1} (13 TeV)" )


    return c,h

def draw_disclaimer():
    # disclaimer
    t = TLatex();
    t.SetNDC()
    t.SetTextSize( 0.1 )
    t.SetTextAlign( 22 )
    t.SetTextAngle( 45 )
    t.DrawText( 0.5, 0.5, "FAKE VALUES" )
    
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
    bestfit()
