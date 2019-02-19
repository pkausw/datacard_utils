import ROOT
import array
import math
import random

def rand_name(pre):
    return pre+str(random.randint(0,1000))


def graph_to_hist(d,isData=False):
    h = ROOT.TH1D(rand_name("graph_to_hist"),"",d.GetN(), 0, d.GetN())
    if isData:
        h.Sumw2(False)
        
    for i in range(0,d.GetN()):
        x = d.GetX()[i]
        y = d.GetY()[i]
        e = d.GetEYhigh()[i]

        if isData:
            for k in range(int(round(y))):# rounding necessary if used with asimov dataset because entries can be non-integer in this case
                h.Fill(i+0.5)
        else:
            h.SetBinContent(i+1,y)
            h.SetBinError(i+1,e)

    if isData:
        histo.SetBinErrorOption(ROOT.TH1.kPoisson)
        
    return h


def get_bins(tf, fit_type):
    sig_prefit = tf.Get("shapes_prefit/total_signal")
    bkg_prefit = tf.Get("shapes_prefit/total_background")
        
    sig = tf.Get(fit_type+"/total_signal")
    bkg = tf.Get(fit_type+"/total_background")
    tot = tf.Get(fit_type+"/total_overall")

    data = graph_to_hist(tf.Get(fit_type+"/total_data"))

    bins = []
    for ibin in range(1, sig.GetNbinsX()+1):
        s_prefit = sig_prefit.GetBinContent(ibin)
        b_prefit = bkg_prefit.GetBinContent(ibin)
        
        s = sig.GetBinContent(ibin)
        b = bkg.GetBinContent(ibin)
        t = tot.GetBinContent(ibin)
        d = data.GetBinContent(ibin)
        
        es = sig.GetBinError(ibin)
        eb = bkg.GetBinError(ibin)
        et = tot.GetBinError(ibin)
        ed = data.GetBinError(ibin)

        if t > 0.01: # some empty bins contain epsilon entries (or numerical problem at reading)  
            bins += [(s, b, t, d, math.log10(s_prefit/b_prefit) if b_prefit > 0 and s_prefit/b_prefit>0 else -10, es, eb, et, ed)]
            #bins += [(s, b, t, d, math.log10(s/b) if b > 0 and s/b>0 else -10, es, eb, et, ed)]

    # sort by pre-fit log(S/B)
    bins_sorted = sorted(bins, key=lambda x: x[4], reverse=True)
    
    return bins_sorted


def add_entry(h,ibin,val,err):
    val_orig = h.GetBinContent(ibin)
    h.SetBinContent( ibin, val_orig + val )
    err_orig = h.GetBinError(ibin)
    #h.SetBinError( ibin, math.sqrt( err_orig*err_orig + err*err ) )
    h.SetBinError( ibin, err_orig + err )


def create_sob_hist(name):
#    nbins = 10
#    xmin = -2.9
#    xmax = -0.4
    edges = [ -2.9, -2.15, -1.9, -1.65, -1.4, -1.15, -0.9, -0.65, -0.4 ]
    edges_array = array.array("f",edges)
    nbins = len(edges_array)-1

    return ROOT.TH1D(name,"",nbins,edges_array)
    

def bins_to_hist(bins):

#    h_sig = ROOT.TH1D(rand_name("sig"),"",nbins,xmin,xmax)
#    h_bkg = ROOT.TH1D(rand_name("bkg"),"",nbins,xmin,xmax)
#    h_tot = ROOT.TH1D(rand_name("tot"),"",nbins,xmin,xmax)
#    h_data = ROOT.TH1D(rand_name("data"),"",nbins,xmin,xmax)

    h_sig = create_sob_hist(rand_name("sig"))
    h_bkg = create_sob_hist(rand_name("bkg"))
    h_tot = create_sob_hist(rand_name("tot"))
    h_data = create_sob_hist(rand_name("data"))  
    
    for s, b, t, d, sob, es, eb, et, ed in bins:
        ibin = h_sig.FindBin(sob)

        add_entry(h_sig,ibin,s,es)
        add_entry(h_bkg,ibin,b,eb)
        add_entry(h_tot,ibin,t,et)
        add_entry(h_data,ibin,d,ed)

    # re-fill data hist for Poisson errors
    h_data_p = create_sob_hist(rand_name("data_p"))
    h_data_p.Sumw2(False)
    for ibin in range(1,h_data_p.GetNbinsX()+1):
        x = h_data.GetBinCenter(ibin)
        y = int( round( h_data.GetBinContent(ibin) ) )
        for k in range(y):
            h_data_p.Fill(x)
    h_data_p.SetBinErrorOption(ROOT.TH1.kPoisson)
        
    return h_sig, h_bkg, h_tot, h_data_p


def get_errorband(h):
    g = ROOT.TGraphAsymmErrors(h.GetNbinsX())

    for ibin in range(1,h.GetNbinsX()+1):
        xval  = h.GetBinCenter(ibin)
        yval  = h.GetBinContent(ibin)

        ex   = h.GetBinWidth(ibin)/2.
        eyup = h.GetBinErrorUp(ibin)
        eydn = h.GetBinErrorLow(ibin)
        
        g.SetPoint(ibin-1,xval,yval)
        g.SetPointError(ibin-1,ex,ex,eydn,eyup)

    return g


def get_ratio_errorband(h_nominator,h_denominator):
    g_ratio = ROOT.TGraphAsymmErrors(h_denominator.GetNbinsX())

    for ibin in range(1,h_nominator.GetNbinsX()+1):
        xval  = h_denominator.GetBinCenter(ibin)
        ynom  = h_nominator.GetBinContent(ibin)
        ydnom = h_denominator.GetBinContent(ibin)

        ex = h_denominator.GetBinWidth(ibin)/2.
        eyup = h_nominator.GetBinErrorUp(ibin)/ydnom if ydnom > 0 else 0
        eydn = h_nominator.GetBinErrorLow(ibin)/ydnom if ydnom > 0 else 0
        
        g_ratio.SetPoint(ibin-1,xval,ynom/ydnom if ydnom > 0 else 0)
        g_ratio.SetPointError(ibin-1,ex,ex,eydn,eyup)

    return g_ratio


def get_ratio_graph(h_nominator,h_denominator):
    g_ratio = get_ratio_errorband(h_nominator,h_denominator)
    for i in range(0,g_ratio.GetN()):
        g_ratio.SetPointEXlow(i,0)
        g_ratio.SetPointEXhigh(i,0)
    g_ratio.SetMarkerStyle(20)
    g_ratio.SetMarkerSize(1.4)
    g_ratio.SetLineColor(ROOT.kBlack)
    g_ratio.SetLineWidth(2)

    return g_ratio


def get_ratio_frame(h):
    frame = h.Clone(rand_name("frame"))
    for ibin in range(1,h.GetNbinsX()+1):
        frame.SetBinContent(ibin,1)
        frame.SetBinError(ibin,0)
    frame.SetFillStyle(1001)
    frame.SetFillColor(10)
    #frame.SetLineStyle(2)
    frame.SetLineWidth(2)
    frame.SetLineColor(ROOT.kBlack)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetNdivisions(206)

    return frame


def get_ratio_pad():
    pad = ROOT.TPad(rand_name("rpad"),"",0,0,1,1)
    pad.SetTopMargin(0.7 - 0.7*pad.GetBottomMargin()+0.3*pad.GetTopMargin())
    pad.SetFillStyle(0)
    pad.SetFrameFillColor(10)
    pad.SetFrameBorderMode(0)

    return pad
    

def set_style_errorband(g):
    #g.SetFillStyle(3005)
    g.SetFillStyle(3645)
    g.SetFillColor(ROOT.kBlack)
    g.SetLineColor(ROOT.kBlack)


def set_style_data(h):
    h.SetMarkerStyle(20)
    h.SetMarkerSize(1.4)
    h.SetMarkerColor(ROOT.kBlack)
    h.SetLineColor(h.GetMarkerColor())
    h.SetLabelSize(0)


def set_style_hist(h,color=ROOT.kWhite):
    h.SetFillColor(color)
    h.SetLineColor(ROOT.kBlack)
    h.SetLineWidth(2)


def get_cms_label():
    label = ROOT.TPaveText(
        ROOT.gStyle.GetPadLeftMargin()+0.03,
        1.-ROOT.gStyle.GetPadTopMargin()-0.12,
        1.-ROOT.gStyle.GetPadRightMargin(), 1.,
        "NDC"
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


def get_lumi_label():
    label = ROOT.TPaveText(
        0.7,1.-ROOT.gStyle.GetPadTopMargin()+0.04,
        1.-ROOT.gStyle.GetPadRightMargin(), 1.,
        "NDC"
    )
    label.AddText("41.5 fb^{-1} (13 TeV)")
    #label.AddText("77.4 fb^{-1} (13 TeV)")
    #label.AddText("35.9 fb^{-1} (2016) + 41.5 fb^{-1} (2017) (13 TeV)")
    label.SetFillColor(0)
    label.SetFillStyle(0)
    label.SetBorderSize(0)
    label.SetTextFont(43)
    label.SetTextSize(28)
    label.SetMargin(0.)
    label.SetTextAlign(33)

    return label


def get_legend():
    x1 = 0.57
    x2 = 1.0 - ROOT.gStyle.GetPadRightMargin() - ROOT.gStyle.GetTickLength()
    y2 = 1.0 - ROOT.gStyle.GetPadTopMargin() - ROOT.gStyle.GetTickLength()
    y1 = y2 - 0.18
    leg = ROOT.TLegend(x1,y1,x2,y2)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.04)

    return leg


def set_gStyle():
    ROOT.gStyle.SetFrameLineWidth(2)
    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.04)
    ROOT.gStyle.SetPadTopMargin(0.05)
    ROOT.gStyle.SetPadBottomMargin(0.14)

    ROOT.gStyle.SetHistLineColor(ROOT.kBlack)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(1)
    ROOT.gStyle.SetMarkerSize(1.2)
    
    ROOT.gStyle.SetAxisColor(1,"XYZ")
    ROOT.gStyle.SetTickLength(0.03,"XYZ")
    ROOT.gStyle.SetNdivisions(510,"XYZ")
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetEndErrorSize(0)
    ROOT.gStyle.SetStripDecimals(False)
    
    ROOT.gStyle.SetTitleColor(1,"XYZ")
    ROOT.gStyle.SetLabelColor(1,"XYZ")
    ROOT.gStyle.SetLabelFont(42,"XYZ")
    ROOT.gStyle.SetLabelOffset(0.007,"XYZ")
    ROOT.gStyle.SetLabelSize(0.038,"XYZ")
    ROOT.gStyle.SetTitleFont(42,"XYZ")
    ROOT.gStyle.SetTitleSize(0.05,"XYZ")
    ROOT.gStyle.SetTitleXOffset(1.3)
    ROOT.gStyle.SetTitleYOffset(1.3)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLegendBorderSize(0)
    
    
if __name__ == "__main__":
    #tf = ROOT.TFile("fitDiagnostics_2016p2017.root","READ")
    tf = ROOT.TFile("fitDiagnostics_2017.root","READ")

    set_gStyle()

    bins_prefit = get_bins(tf, "shapes_prefit")
    bins_postfit = get_bins(tf, "shapes_fit_s")

#    for s, b, t, d, sob, es, eb, et, ed in bins_postfit:
#        print sob,": ",d," -- ",t,"+/-",et," -- ",b," + ",s

    h_sig_p, h_bkg_p, _, _ = bins_to_hist(bins_prefit)
    h_sig_s, h_bkg_s, h_tot_s, h_data = bins_to_hist(bins_postfit)

#    n_tot = h_tot_s.Integral(0,h_tot_s.GetNbinsX()+1)
#    n_sig = h_sig_s.Integral(0,h_sig_s.GetNbinsX()+1)
#    n_sig_p = h_sig_p.Integral(0,h_sig_p.GetNbinsX()+1)
#    n_bkg = h_bkg_s.Integral(0,h_bkg_s.GetNbinsX()+1)
#    print " D=",h_data.Integral(0,h_data.GetNbinsX()+1)
#    print " S=",n_sig, " B=",n_bkg, " :",(n_tot-n_bkg)
#    print " r=",(n_sig/n_sig_p)

    set_style_data(h_data)
    h_data.GetYaxis().SetTitle("Events / Bin")
    h_data.GetYaxis().SetRangeUser(2,9E6)
    h_data.GetYaxis().SetTickLength(0.04)
    set_style_hist(h_sig_s,ROOT.kCyan)
    set_style_hist(h_bkg_s)

    h_tot_sm = h_sig_p.Clone("h_tot_sm")
    h_tot_sm.Add(h_bkg_s)
    h_tot_sm.SetLineColor(ROOT.kRed)
    h_tot_sm.SetLineWidth(2)
    
    stack_sb = ROOT.THStack("stack","s+b")
    stack_sb.Add(h_bkg_s)
    stack_sb.Add(h_sig_s)

    stack_eb = get_errorband(h_bkg_s)
    set_style_errorband(stack_eb)

    ratio_f = get_ratio_frame(h_bkg_s)
    ratio_f.GetXaxis().SetTitle("Pre-fit expected log_{10}(S/B)")
    #ratio_f.GetXaxis().SetTitle("post-fit log_{10}(S/B)")
    ratio_f.GetYaxis().SetTitle("Data / Bkg.")
    ratio_f.GetYaxis().SetRangeUser(0.42,1.58)
    ratio_f.GetYaxis().SetTickLength(0.1)

    ratio_db = get_ratio_graph(h_data,h_bkg_s)
    ratio_eb = get_ratio_errorband(h_tot_s,h_tot_s)
    set_style_errorband(ratio_eb)

    ratio_sb = h_tot_s.Clone(rand_name("ratio_sb"))
    ratio_sb.Divide(h_bkg_s)
    set_style_hist(ratio_sb,ROOT.kCyan)

    ratio_sm = h_tot_sm.Clone(rand_name("ratio_sp"))
    ratio_sm.Divide(h_bkg_s)
    ratio_sm.SetLineColor(ROOT.kRed)
        
    can = ROOT.TCanvas("can","sob",800,850)
    can.SetBottomMargin(0.3 + 0.7*can.GetBottomMargin()-0.3*can.GetTopMargin())
    
    h_data.Draw("PE")
    h_tot_sm.Draw("HISTsame][")
    stack_sb.Draw("HISTsame][")
    stack_eb.Draw("E2same][")
    h_data.Draw("PE0same")

    label_cms = get_cms_label()
    label_cms.Draw("same")
    label_lumi = get_lumi_label()
    label_lumi.Draw("same")

    leg = get_legend()
    leg.AddEntry(h_data,"Data","P")
    leg.AddEntry(h_bkg_s,"Background","L")
    #leg.AddEntry(h_sig_s,"Signal (#mu = 1.18)","F")
    leg.AddEntry(h_sig_s,"Signal (#mu = 1.53)","F")
    leg.AddEntry(h_tot_sm,"SM (#mu = 1)","l")
    leg.Draw("same")
    
    can.SetLogy()
    ROOT.gPad.RedrawAxis()

    ratio_pad = get_ratio_pad()
    ratio_pad.Draw()
    ratio_pad.cd()

    ratio_f.Draw("HIST][")
    ratio_sb.Draw("HISTsame][")
    ratio_sm.Draw("HISTsame][")
    ratio_f.Draw("HISTsame][")
    ratio_eb.Draw("E2same][")
    ratio_db.Draw("PEsame")

    ROOT.gPad.RedrawAxis()

    can.SaveAs("sob_test.pdf")
