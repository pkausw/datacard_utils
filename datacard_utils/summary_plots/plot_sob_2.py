#!/usr/bin/env python
import argparse, os, array, math, random, ROOT

ROOT.PyConfig.IgnoreCommandLineOptions = True

SOB_BIN_EDGES = [

  -2.90,
  -2.15,
  -1.90,
  -1.65,
  -1.40,
  -1.15,
  -0.90,
  -0.65,
  -0.20,
]

def get_mu_value(tf, tree_key='tree_fit_sb'):

    _mu = None

    _tree = tf.Get(tree_key)
    if _tree and _tree.InheritsFrom('TTree') and (_tree.GetEntries() == 1):
       for _evt in _tree: _mu = _evt.r; break;

    return _mu

def KILL(log):
    raise SystemExit('\n '+'\033[1m'+'@@@ '+'\033[91m'+'FATAL'  +'\033[0m'+' -- '+log+'\n')

def WARNING(log):
    print '\n '+'\033[1m'+'@@@ '+'\033[93m'+'WARNING'+'\033[0m'+' -- '+log+'\n'

def rand_name(pre):
    return pre+str(random.randint(0,1000))

def graph_to_hist(d, isData=False):

    h = ROOT.TH1D(rand_name('graph_to_hist'), '', d.GetN(), 0, d.GetN())

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

class FitBin:
    def __init__(self):
        self.index = 0

        self.sob = 0.

        self.s  = 0.
        self.es = 0.

        self.b  = 0.
        self.eb = 0.

        self.t  = 0.
        self.et = 0.

        self.d  = 0.
        self.ed = 0.

def get_fitBins(tf, fit_type):

    sig_prefit = tf.Get('shapes_prefit/total_signal')
    bkg_prefit = tf.Get('shapes_prefit/total_background')

    sig = tf.Get(fit_type+'/total_signal')
    bkg = tf.Get(fit_type+'/total_background')
    tot = tf.Get(fit_type+'/total_overall')

    data = graph_to_hist(tf.Get(fit_type+'/total_data'))

    fitBins = []

    for ibin in range(1, sig.GetNbinsX()+1):

        if tot.GetBinContent(ibin) > 0.01: # some empty bins contain epsilon entries (or numerical problem at reading)  

           a_bin = FitBin()

           a_bin.index = ibin

           a_bin.s = sig .GetBinContent(ibin)
           a_bin.b = bkg .GetBinContent(ibin)
           a_bin.t = tot .GetBinContent(ibin)
           a_bin.d = data.GetBinContent(ibin)

           s_prefit = sig_prefit.GetBinContent(ibin)
           b_prefit = bkg_prefit.GetBinContent(ibin)

           a_bin.sob = math.log10(s_prefit/b_prefit) if (b_prefit > 0 and ((s_prefit/b_prefit) > 0)) else -10.

           a_bin.es = sig .GetBinError(ibin)
           a_bin.eb = bkg .GetBinError(ibin)
           a_bin.et = tot .GetBinError(ibin)
           a_bin.ed = data.GetBinError(ibin)

           fitBins += [a_bin]

    # sort by pre-fit log(S/B)
    fitBins_sorted = sorted(fitBins, key=lambda x: x.sob, reverse=True)

    return fitBins_sorted

def get_correlation_matrix(tf, fit_type):

    h1_tot = tf.Get(fit_type+'/total_overall')
    h2_cov = tf.Get(fit_type+'/overall_total_covar')

    _corr_mat = [[None for _tmpy in range(h2_cov.GetNbinsY())] for _tmpx in range(h2_cov.GetNbinsX())]
    for _tmpx in range(h2_cov.GetNbinsX()):

        for _tmpy in range(h2_cov.GetNbinsY()):

            _corr_val = 0.0
            if (h1_tot.GetBinError(_tmpx+1) > 0.) and (h1_tot.GetBinError(_tmpy+1) > 0.):
               _corr_val = h2_cov.GetBinContent(_tmpx+1, _tmpy+1) / (h1_tot.GetBinError(_tmpx+1) * h1_tot.GetBinError(_tmpy+1))

            _corr_mat[_tmpx][_tmpy] = _corr_val

            if ((abs(_corr_val) - 1.) >= 1e4):
               KILL(log_prx+'logic error: value of correlation matrix outside of [-1,1] interval (value='+str(_corr_val)+', binX='+str(_tmpx+1)+', binY='+str(_tmpy+1)+')')

    return _corr_mat

### def add_entry(h,ibin,val,err):
### 
###     val_orig = h.GetBinContent(ibin)
###     h.SetBinContent( ibin, val_orig + val )
###     err_orig = h.GetBinError(ibin)
###     h.SetBinError( ibin, math.sqrt( err_orig*err_orig + err*err ) )
### #    h.SetBinError( ibin, ( err_orig + err ) )

def create_sob_hist(name):

    edges = SOB_BIN_EDGES
    edges_array = array.array('f', edges)
    nbins = len(edges_array)-1

    return ROOT.TH1D(name, '', nbins, edges_array)

def fill_sob_hist(th1, fit_bins, val_str, err_str, correlation_matrix=None):

    _th1_new = th1.Clone()

    sob_bin_containers = [[] for _tmp in range(th1.GetNbinsX() + 2)]

    for i_fitbin in fit_bins:

        i_bin = th1.FindBin(i_fitbin.sob)

        sob_bin_containers[i_bin] += [i_fitbin]

    for i_sobbin in range(len(sob_bin_containers)):

        _th1_new_val = 0.
        _th1_new_err = 0.

        for _tmp_idx1 in range(len(sob_bin_containers[i_sobbin])):

            _th1_new_val += getattr(sob_bin_containers[i_sobbin][_tmp_idx1], val_str)

            for _tmp_idx2 in range(len(sob_bin_containers[i_sobbin])):

                corr_fact = None

                if correlation_matrix == None:
                   corr_fact = (1. if (_tmp_idx1 == _tmp_idx2) else  0.) # uncorrelated
#                   corr_fact = (1. if (_tmp_idx1 == _tmp_idx2) else +1.) # fully correlated

                else:
                   corr_fact = correlation_matrix[sob_bin_containers[i_sobbin][_tmp_idx1].index-1][sob_bin_containers[i_sobbin][_tmp_idx2].index-1]

                _th1_new_err += (corr_fact * getattr(sob_bin_containers[i_sobbin][_tmp_idx1], err_str) * getattr(sob_bin_containers[i_sobbin][_tmp_idx2], err_str))

        _th1_new_err = math.sqrt(_th1_new_err)

        _th1_new.SetBinContent(i_sobbin, _th1_new_val)
        _th1_new.SetBinError  (i_sobbin, _th1_new_err)

    return _th1_new

def fitBins_to_hist(fitBins, correlation_matrix=None):

    h_sig  = create_sob_hist(rand_name('sig'))
    h_bkg  = create_sob_hist(rand_name('bkg'))
    h_tot  = create_sob_hist(rand_name('tot'))
    h_data = create_sob_hist(rand_name('data'))  

    h_sig  = fill_sob_hist(h_sig , fitBins, 's', 'es', correlation_matrix)
    h_bkg  = fill_sob_hist(h_bkg , fitBins, 'b', 'eb', correlation_matrix)
    h_tot  = fill_sob_hist(h_tot , fitBins, 't', 'et', correlation_matrix)
    h_data = fill_sob_hist(h_data, fitBins, 'd', 'ed', correlation_matrix)

    # re-fill data hist for Poisson errors
    h_data_p = create_sob_hist(rand_name('data_poisson'))
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
    frame = h.Clone(rand_name('frame'))
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
    pad = ROOT.TPad(rand_name('rpad'),'',0,0,1,1)
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
        'NDC'
    )

#    label.AddText('#scale[1.5]{#bf{CMS}}')
    label.AddText('#scale[1.5]{#bf{CMS}} #scale[1.1]{#it{Preliminary}}')

    label.SetFillColor(0)
    label.SetFillStyle(0)
    label.SetBorderSize(0)
    label.SetTextFont(43)
    label.SetTextSize(26)
    label.SetMargin(0.)
    label.SetTextAlign(13)

    return label

def get_lumi_label():

    label = ROOT.TPaveText(0.7, 1.0-ROOT.gStyle.GetPadTopMargin()+0.04, 1.0-ROOT.gStyle.GetPadRightMargin(), 1.0, 'NDC')

#    label.AddText('35.9 fb^{-1} (13 TeV)')
#    label.AddText('41.5 fb^{-1} (13 TeV)')
    label.AddText('77.4 fb^{-1} (13 TeV)')
#    label.AddText('35.9 fb^{-1} (2016) + 41.5 fb^{-1} (2017) (13 TeV)')
#    label.AddText('35.9 + 41.5 fb^{-1} (13 TeV)')

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
    y2 = 1.0 - ROOT.gStyle.GetPadTopMargin()   - ROOT.gStyle.GetTickLength()
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
    
    ROOT.gStyle.SetAxisColor(1,'XYZ')
    ROOT.gStyle.SetTickLength(0.03,'XYZ')
    ROOT.gStyle.SetNdivisions(510,'XYZ')
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)
    ROOT.gStyle.SetErrorX(0)
    ROOT.gStyle.SetEndErrorSize(0)
    ROOT.gStyle.SetStripDecimals(False)
    
    ROOT.gStyle.SetTitleColor(1,'XYZ')
    ROOT.gStyle.SetLabelColor(1,'XYZ')
    ROOT.gStyle.SetLabelFont(42,'XYZ')
    ROOT.gStyle.SetLabelOffset(0.007,'XYZ')
    ROOT.gStyle.SetLabelSize(0.038,'XYZ')
    ROOT.gStyle.SetTitleFont(42,'XYZ')
    ROOT.gStyle.SetTitleSize(0.05,'XYZ')
    ROOT.gStyle.SetTitleXOffset(1.3)
    ROOT.gStyle.SetTitleYOffset(1.3)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetLegendBorderSize(0)

    return

#### main
if __name__ == '__main__':
    ### args --------------
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', dest='input', required=True, action='store', default=None,
                        help='path to input ROOT file')

    parser.add_argument('-o', '--output', dest='output', required=True, action='store', default='',
                        help='path to output ROOT file')

    parser.add_argument('--fit-dir', dest='fit_dir', action='store', choices=['shapes_fit_b', 'shapes_fit_s'], default='shapes_fit_s',
                        help='name of input directory with postfit shapes (must be "shapes_fit_b" or "shapes_fit_s")')

    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='enable verbose mode')

    opts, opts_unknown = parser.parse_known_args()
    ### -------------------

    ROOT.gROOT.SetBatch()

    log_prx = os.path.basename(__file__)+' -- '

    ### args validation ---
    if not opts.input:
       KILL(log_prx+'unspecified path to input .root file [-i]')
    elif not os.path.isfile(opts.input):
       KILL(log_prx+'invalid path to input .root file [-i]: '+opts.input)

    if not opts.output:
       KILL(log_prx+'unspecified path to output .root file [-o]')
    elif os.path.exists(opts.output):
       KILL(log_prx+'target path to output .root file already exists [-o]: '+opts.output)

    tf = ROOT.TFile.Open(opts.input)
    if not tf: raise SystemExit(1)

    set_gStyle()

    mu_val = get_mu_value(tf, ('tree_fit_sb' if opts.fit_dir == 'shapes_fit_s' else 'tree_fit_b'))
    mu_str = ('NaN' if (mu_val == None) else '{:3.2f}'.format(mu_val))

    bins_prefit  = get_fitBins(tf, 'shapes_prefit')
    bins_postfit = get_fitBins(tf, opts.fit_dir)

    corr_matrix = get_correlation_matrix(tf, opts.fit_dir)

    h_sig_p, h_bkg_p, _      , _      = fitBins_to_hist(bins_prefit , corr_matrix)
    h_sig_s, h_bkg_s, h_tot_s, h_data = fitBins_to_hist(bins_postfit, corr_matrix)

#    n_tot = h_tot_s.Integral(0,h_tot_s.GetNbinsX()+1)
#    n_sig = h_sig_s.Integral(0,h_sig_s.GetNbinsX()+1)
#    n_sig_p = h_sig_p.Integral(0,h_sig_p.GetNbinsX()+1)
#    n_bkg = h_bkg_s.Integral(0,h_bkg_s.GetNbinsX()+1)
#    print ' D=',h_data.Integral(0,h_data.GetNbinsX()+1)
#    print ' S=',n_sig, ' B=',n_bkg, ' :',(n_tot-n_bkg)
#    print ' r=',(n_sig/n_sig_p)

    set_style_data(h_data)

    h_data.GetYaxis().SetTitle('Events / Bin')
    h_data.GetYaxis().SetRangeUser(2, 9E6)
    h_data.GetYaxis().SetTickLength(0.04)

    set_style_hist(h_sig_s, ROOT.kCyan)
    set_style_hist(h_bkg_s)

    h_tot_sm = h_sig_p.Clone('h_tot_sm')
    h_tot_sm.Add(h_bkg_s)
    h_tot_sm.SetLineColor(ROOT.kRed)
    h_tot_sm.SetLineWidth(2)

    stack_sb = ROOT.THStack('stack','s+b')
    stack_sb.Add(h_bkg_s)
    stack_sb.Add(h_sig_s)

    stack_eb = get_errorband(h_bkg_s)
    set_style_errorband(stack_eb)

    ratio_f = get_ratio_frame(h_bkg_s)
    ratio_f.GetXaxis().SetTitle('Pre-fit expected log_{10}(S/B)')
#    ratio_f.GetXaxis().SetTitle('Post-fit log_{10}(S/B)')
    ratio_f.GetYaxis().SetTitle('Data / Bkg.')
    ratio_f.GetYaxis().SetRangeUser(0.42,1.58)
    ratio_f.GetYaxis().SetTickLength(0.1)

    ratio_db = get_ratio_graph(h_data, h_bkg_s)
    ratio_eb = get_ratio_errorband(h_tot_s, h_tot_s)
    set_style_errorband(ratio_eb)

    ratio_sb = h_tot_s.Clone(rand_name('ratio_sb'))
    ratio_sb.Divide(h_bkg_s)
    set_style_hist(ratio_sb,ROOT.kCyan)

    ratio_sm = h_tot_sm.Clone(rand_name('ratio_sp'))
    ratio_sm.Divide(h_bkg_s)
    ratio_sm.SetLineColor(ROOT.kRed)

    can = ROOT.TCanvas('can','sob',800,850)
    can.SetBottomMargin(0.3 + 0.7*can.GetBottomMargin()-0.3*can.GetTopMargin())

    h_data.Draw('PE')
    h_tot_sm.Draw('HISTsame][')
    stack_sb.Draw('HISTsame][')
    stack_eb.Draw('E2same][')
    h_data.Draw('PE0same')

    label_cms = get_cms_label()
    label_cms.Draw('same')
    label_lumi = get_lumi_label()
    label_lumi.Draw('same')

    leg = get_legend()
    leg.AddEntry(h_data,'Data','P')
    leg.AddEntry(h_bkg_s,'Background','L')
    leg.AddEntry(h_sig_s,'Signal (#mu = '+mu_str+')', 'F')
    leg.AddEntry(h_tot_sm,'SM (#mu = 1)','l')
    leg.Draw('same')

    can.SetLogy()
    ROOT.gPad.RedrawAxis()

    ratio_pad = get_ratio_pad()
    ratio_pad.Draw()
    ratio_pad.cd()

    ratio_f.Draw('HIST][')
    ratio_sb.Draw('HISTsame][')
    ratio_f.Draw('HISTsame][')
    ratio_eb.Draw('E2same][')
    ratio_sm.Draw('HISTsame][')
    ratio_db.Draw('PEsame')

    ROOT.gPad.RedrawAxis()

    can.SaveAs(opts.output)
