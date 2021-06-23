#!/usr/bin/env python
import argparse
import os
import ROOT
import math
import copy

def KILL(log):
    raise SystemExit('\n '+'\033[1m'+'@@@ '+'\033[91m'+'FATAL'  +'\033[0m'+' -- '+log+'\n')
# --

def EXE(cmd, suspend=True, verbose=False, dry_run=False):
    if verbose: print '\033[1m'+'>'+'\033[0m'+' '+cmd
    if dry_run: return

    _exitcode = os.system(cmd)

    if _exitcode and suspend: raise SystemExit(_exitcode)

    return _exitcode
# --


def cov_value(cov_dc, k1, k2):

    val = None

    if   k1 in cov_dc and k2 in cov_dc[k1]: val = cov_dc[k1][k2]
    elif k2 in cov_dc and k1 in cov_dc[k2]: val = cov_dc[k2][k1]

    if val == None:
        log_msg = 'cov_value -- value not found'
        #KILL(log_msg+': '+ 'key_1='+k1+' '+'key2='+k2+'\n'+str(cov_dc))

    return val
#### ----

def chunks(ls, N):
    for idx in range(0, len(ls), N):
        yield ls[idx:idx+N]
#### ----

#### main
if __name__ == '__main__':
    ### args
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-i', '--inputs', dest='inputs', required=True, nargs='+', default=[],
                        help='path to input RooFit files')

    parser.add_argument('-o', '--output-dir', dest='output_dir', action='store', default='',
                        help='path to output directory')

    parser.add_argument('-p', '--poi', dest='poi', default='r', type=str,
                        help='Name of signal strength parameter (default="r")')

    parser.add_argument('--only-fitB', dest='only_fitB', default=False, action='store_true',
                        help='consider only B-only fit results')

    parser.add_argument('--only-fitS', dest='only_fitS', default=False, action='store_true',
                        help='consider only S+B fit results')

    parser.add_argument('-f', '--format', dest='format', default='text', type=str,
                        help='format of text output file ["text", "latex"]')

    parser.add_argument('-e', '--exts', dest='exts', nargs='+', default=['pdf'],
                        help='list of extensions for output file(s)')

    parser.add_argument('--param-names', dest='param_names', default='', type=str,
                        help='path to .json file with parameter names')

    parser.add_argument('-L', '--text-left', dest='txtTL', default='', type=str,
                        help='text for top-left corner of the plot')

    parser.add_argument('-R', '--text-right', dest='txtTR', default='', type=str,
                        help='text for top-right corner of the plot')

    opts, opts_unknown = parser.parse_known_args()
    ###

    log_prx = os.path.basename(__file__)+' -- '

    ROOT.gROOT.SetBatch()

    # inputs
    INPUT_FILES = []

    for i_inp in opts.inputs:
        INPUT_FILES += (glob.glob(i_inp) if '*' in i_inp else [i_inp])

    INPUT_FILES = sorted(list(set(INPUT_FILES)))

    for i_inp in INPUT_FILES:
        if not os.path.isfile(i_inp):
           KILL(log_prx+'invalid path to input .root file [-i]: '+i_inp)


    if opts.output_dir and os.path.isdir(opts.output_dir):
       KILL(log_prx+'target output directory exists already [-o]: '+opts.output_dir)

    ext_ls = list(set(opts.exts))
    ext_ls = [i_ext for i_ext in ext_ls if i_ext != '']

    if opts.output_dir and not ext_ls:
       KILL(log_prx+'invalid comma-list of extensions for output file(s) [-e]: '+opts.exts)

    if opts.only_fitB and opts.only_fitS:
       KILL(log_prx+'logic error: using "--only-fitB" and "--only-fitS" options simultaneously')

    parkey_dc = (json.load(open(opts.param_names)) if opts.param_names else {})
    ###

    ### load fit covariance matrices in dictionaries
    cov_fitS_dc = {}
    cov_fitB_dc = {}


    ### list of nuisance to look at during unblinding procedure
    unblinded_nuisances = {'scale', 'ISR','FSR', 'HDAMP', 'UE', 'btag', 'eff', 'PU', 'glusplit'}

    ### MLF output plots
    if opts.output_dir:

        EXE('mkdir -p '+opts.output_dir)

        for i_inpf in INPUT_FILES:

            ctg = i_inpf.split("fitDiagnostics_asimov_sig1_r_combined_",1)[1][:-5]

            EXE('mkdir -p '+opts.output_dir+'/'+ctg)

            ### pre/post fit values
            ifile = ROOT.TFile(i_inpf)
            if not ifile: raise SystemExit

            fitB_res = ifile.Get('fit_b')
            fitB_arg = None
            if fitB_res and fitB_res.ClassName() == 'RooFitResult': fitB_arg = fitB_res.floatParsFinal()
            elif opts.only_fitB: KILL(log_prx+'failed to locate RooFitResult object "fit_b"')

            fitS_res = ifile.Get('fit_s')
            fitS_arg = None
            if fitS_res and fitS_res.ClassName() == 'RooFitResult': fitS_arg = fitS_res.floatParsFinal()
            elif opts.only_fitS: KILL(log_prx+'failed to locate RooFitResult object "fit_s"')

            fit0_arg = ifile.Get('nuisances_prefit')
            fit0_arg = (ROOT.RooArgList(fit0_arg) if fit0_arg != None and fit0_arg.ClassName() == 'RooArgSet' else None)
            ### -------------------

            ### load fit values in dictionaries

            # absolute values
            fitB_vabs_dc = {}
            fitS_vabs_dc = {}
            fit0_vabs_dc = {}

            for unblinded_nuisance in  unblinded_nuisances:

                for (i_fitarg, i_vabs_dc) in [(fitB_arg, fitB_vabs_dc), (fitS_arg, fitS_vabs_dc), (fit0_arg, fit0_vabs_dc)]:
                  if i_fitarg == None: continue

                  for idx in range(i_fitarg.getSize()):
                      par_arg = i_fitarg[idx]
                      if not par_arg: continue

                      par_key = par_arg.GetName()

                      if unblinded_nuisance not in par_key: continue

                      # print par_key, 'par_arg.getError()', par_arg.getError()
                      # print par_key, 'par_arg.getErrorHi()', par_arg.getErrorHi()
                      # print par_key, 'par_arg.getErrorLo()', par_arg.getErrorLo()

                      if par_arg.getErrorHi() <= 0:
                         WARNING(log_prx+'getErrorHi() for input parameter "'+par_key+'" returns non-positive value: '+str(par_arg.getErrorHi()))
                         continue

                      if par_arg.getErrorLo() >= 0:
                         WARNING(log_prx+'getErrorLo() for input parameter "'+par_key+'" returns non-negative value: '+str(par_arg.getErrorLo()))
                         continue

                      if par_key in i_vabs_dc:
                         WARNING(log_prx+'key for (absolute) fit-values dictionary already exists: '+par_key)
                         continue

                      i_vabs_dc[par_key] = {
                        'val'  :     par_arg.getVal    () ,
                        'errUP': abs(par_arg.getErrorHi()),
                        'errDN': abs(par_arg.getErrorLo()),
                      }

            cov_fitB_dc[ctg] = {}
            cov_fitS_dc[ctg] = {}

            for (i_fitres, i_val_dc, i_cov_dc) in [(fitB_res, fitB_vabs_dc, cov_fitB_dc[ctg]), (fitS_res, fitS_vabs_dc, cov_fitS_dc[ctg])]:
              if i_fitres == None: continue

              parKeys_fit = sorted(i_val_dc.keys())

              for p_i in range(0, len(parKeys_fit)):
                  parkey_i = parKeys_fit[p_i]

                  if not parkey_i in i_cov_dc: i_cov_dc[parkey_i] = {}

                  for p_j in range(p_i, len(parKeys_fit)):

                      parkey_j = parKeys_fit[p_j]
                      if parkey_j in i_cov_dc[parkey_i]:
                          log_msg = 'target entry for fit covariance matrix already exists'
                          KILL(log_prx+log_msg+': '+'["'+parkey_i+'"]["'+parkey_j+'"]')

                      i_cov_dc[parkey_i][parkey_j] = i_fitres.correlation(parkey_i, parkey_j)
            ### --------------------------------------------

            ### COVARIANCE [B] -------------------------------------------------------------------------

            if not opts.only_fitS:

                   ccov_B = ROOT.TCanvas('ccov_B', 'ccov_B', 1100, 750)

                   L, R = 0.185, 0.110
                   T, B = 0.100, 0.100

                   ccov_B.SetLeftMargin  (L)
                   ccov_B.SetRightMargin (R)
                   ccov_B.SetTopMargin   (T)
                   ccov_B.SetBottomMargin(B)

                   parB_ls = sorted(cov_fitB_dc[ctg].keys())

                   parB_ls = [x for x in parB_ls if "bin" not in x]

                   if opts.poi in parB_ls: parB_ls.append(parB_ls.pop(parB_ls.index(opts.poi)))


                   hcov_B = ROOT.TH2F('hcov_B', '', len(parB_ls), 0, len(parB_ls), len(parB_ls), 0, len(parB_ls))
                   for pk_i in range(0, len(parB_ls)):
                       pk_i_tag = parkey_dc[parB_ls[pk_i]] if parB_ls[pk_i] in parkey_dc else parB_ls[pk_i]

                       hcov_B.GetYaxis().SetBinLabel(len(parB_ls)-pk_i, pk_i_tag)

                       for pk_j in range(0, len(parB_ls)):
                           pk_j_tag = parkey_dc[parB_ls[pk_j]] if parB_ls[pk_j] in parkey_dc else parB_ls[pk_j]

                           if pk_i == 0: hcov_B.GetXaxis().SetBinLabel(pk_j+1, pk_j_tag)

                           vcov = cov_value(cov_fitB_dc[ctg], parB_ls[pk_i], parB_ls[pk_j])*100
                           hcov_B.SetBinContent(pk_j+1, len(parB_ls)-pk_i, vcov)

                   ccov_B.cd()

                   hcov_B.SetTitle(ctg + '_onlyBkgfit')
                   hcov_B.SetStats(0)
                   hcov_B.SetMinimum(-100)
                   hcov_B.SetMaximum(+100)
                   hcov_B.SetMarkerSize          (0.45     if len(parB_ls) > 10 else 1) #max(0.5, 4.0/len(parB_ls)))
                   ROOT.gStyle.SetPaintTextFormat('.1f' if len(parB_ls) > 10 else '.2f')
                   hcov_B.Draw('colz,text')

                   hcov_B.GetXaxis().SetNdivisions(-414)
                   hcov_B.GetYaxis().SetNdivisions(-414)
                   hcov_B.GetXaxis().SetLabelSize  (0.6 * hcov_B.GetXaxis().GetLabelSize  ())
                   hcov_B.GetYaxis().SetLabelSize  (0.6 * hcov_B.GetYaxis().GetLabelSize  ())
                   hcov_B.GetXaxis().SetLabelOffset(2.0 * hcov_B.GetXaxis().GetLabelOffset())
                   hcov_B.GetYaxis().SetLabelOffset(2.0 * hcov_B.GetYaxis().GetLabelOffset())
                   hcov_B.Draw('axis,same')

                   txtTL = ROOT.TLatex(L+(1-R-L)*0.00, (1-T)+T*.150, opts.txtTL)
                   txtTL.SetTextAlign(11)
                   txtTL.SetTextSize(0.015)
                   txtTL.SetTextFont(42)
                   txtTL.SetNDC()
                   txtTL.Draw('same')

                   txtTR = ROOT.TLatex(L+(1-R-L)*1.00, (1-T)+T*.150, opts.txtTR)
                   txtTR.SetTextAlign(31)
                   txtTR.SetTextSize(0.015)
                   txtTR.SetTextFont(42)
                   txtTR.SetNDC()
                   txtTR.Draw('same')

                   for ext in ext_ls: ccov_B.SaveAs(opts.output_dir+'/'+ctg+'/'+ctg+'_postfit_covar_B.'+ext)

                   ccov_B.Close()
            ### ----------------------------------------------------------------------------------------

            ### COVARIANCE [S] -------------------------------------------------------------------------
            if not opts.only_fitB:

                   ccov_S = ROOT.TCanvas('ccov_S', 'ccov_S', 1100, 750)

                   L, R = 0.185, 0.110
                   T, B = 0.100, 0.100

                   ccov_S.SetLeftMargin  (L)
                   ccov_S.SetRightMargin (R)
                   ccov_S.SetTopMargin   (T)
                   ccov_S.SetBottomMargin(B)

                   parS_ls = sorted(cov_fitS_dc[ctg].keys())

                   parS_ls = [x for x in parS_ls if "bin" not in x]

                   if opts.poi in parS_ls: parS_ls.append(parS_ls.pop(parS_ls.index(opts.poi)))

                   hcov_S = ROOT.TH2F('hcov_S', '', len(parS_ls), 0, len(parS_ls), len(parS_ls), 0, len(parS_ls))
                   for pk_i in range(0, len(parS_ls)):
                       pk_i_tag = parkey_dc[parS_ls[pk_i]] if parS_ls[pk_i] in parkey_dc else parS_ls[pk_i]

                       hcov_S.GetYaxis().SetBinLabel(len(parS_ls)-pk_i, pk_i_tag)

                       for pk_j in range(0, len(parS_ls)):
                           pk_j_tag = parkey_dc[parS_ls[pk_j]] if parS_ls[pk_j] in parkey_dc else parS_ls[pk_j]

                           if pk_i == 0: hcov_S.GetXaxis().SetBinLabel(pk_j+1, pk_j_tag)

                           vcov = cov_value(cov_fitS_dc[ctg], parS_ls[pk_i], parS_ls[pk_j]) * 100
                           hcov_S.SetBinContent(pk_j+1, len(parS_ls)-pk_i, vcov)

                   ccov_S.cd()

                   hcov_S.SetTitle(ctg+ '_Signal+Bkgfit')
                   hcov_S.SetStats(0)
                   hcov_S.SetMinimum(-100)
                   hcov_S.SetMaximum(+100)
                   hcov_S.SetMarkerSize          (0.45     if len(parS_ls) > 10 else 1) #max(0.5, 4.0/len(parS_ls)))
                   ROOT.gStyle.SetPaintTextFormat('.1f' if len(parS_ls) > 10 else '.2f')
                   hcov_S.Draw('colz,text')

                   hcov_S.GetXaxis().SetNdivisions(-414)
                   hcov_S.GetYaxis().SetNdivisions(-414)
                   hcov_S.GetXaxis().SetLabelSize  (0.6 * hcov_S.GetXaxis().GetLabelSize  ())
                   hcov_S.GetYaxis().SetLabelSize  (0.6 * hcov_S.GetYaxis().GetLabelSize  ())
                   hcov_S.GetXaxis().SetLabelOffset(1.0 * hcov_S.GetXaxis().GetLabelOffset())
                   hcov_S.GetYaxis().SetLabelOffset(1.0 * hcov_S.GetYaxis().GetLabelOffset())
                   hcov_S.Draw('axis,same')

                   txtTL = ROOT.TLatex(L+(1-R-L)*0.00, (1-T)+T*.150, opts.txtTL)
                   txtTL.SetTextAlign(11)
                   txtTL.SetTextSize(0.015)
                   txtTL.SetTextFont(42)
                   txtTL.SetNDC()
                   txtTL.Draw('same')

                   txtTR = ROOT.TLatex(L+(1-R-L)*1.00, (1-T)+T*.150, opts.txtTR)
                   txtTR.SetTextAlign(31)
                   txtTR.SetTextSize(0.015)
                   txtTR.SetTextFont(42)
                   txtTR.SetNDC()
                   txtTR.Draw('same')

                   for ext in ext_ls: ccov_S.SaveAs(opts.output_dir+'/'+ctg+'/'+ctg+'_postfit_covar_S.'+ext)

                   ccov_S.Close()


            ### COVARIANCE [B] -------------------------------------------------------------------------

        EXE('mkdir -p '+opts.output_dir+'/EvolutionPlots_OnlyB')
        EXE('mkdir -p '+opts.output_dir+'/EvolutionPlots_S+B')

        if not opts.only_fitS:



           parB_ls = []

           for k in cov_fitB_dc.keys():
               parB_ls.extend(cov_fitB_dc[k].keys())

           parB_ls = [x for x in parB_ls if "bin" not in x]

           parB_ls = sorted(set(parB_ls))

           if opts.poi in parB_ls: parB_ls.append(parB_ls.pop(parB_ls.index(opts.poi)))

           for pk_i in range(0, len(parB_ls)):

               pk_i_tag = parkey_dc[parB_ls[pk_i]] if parB_ls[pk_i] in parkey_dc else parB_ls[pk_i]
               ccov_B = ROOT.TCanvas('ccov_B'+pk_i_tag, 'ccov_B'+pk_i_tag, 750, 1500)

               L, R = 0.200, 0.140
               T, B = 0.010, 0.100

               ccov_B.SetLeftMargin  (L)
               ccov_B.SetRightMargin (R)
               ccov_B.SetTopMargin   (T)
               ccov_B.SetBottomMargin(B)

               hcov_B = ROOT.TH2F('hcov_B'+pk_i_tag, '', len(INPUT_FILES), 0, len(INPUT_FILES), len(parB_ls), 0, len(parB_ls))

               for i_cnt, i_inpf in enumerate(INPUT_FILES):

                   ctg = i_inpf.split("fitDiagnostics_asimov_sig1_r_combined_",1)[1][:-5]

                   hcov_B.GetXaxis().SetBinLabel(i_cnt+1, ctg)

                   for pk_j in range(0, len(parB_ls)):

                       pk_j_tag = parkey_dc[parB_ls[pk_j]] if parB_ls[pk_j] in parkey_dc else parB_ls[pk_j]

                       hcov_B.GetYaxis().SetBinLabel(len(parB_ls)-pk_j, pk_j_tag)

                       vcov = cov_value(cov_fitB_dc[ctg], parB_ls[pk_i], parB_ls[pk_j])

                       if vcov:
                           vcov = vcov*100
                           hcov_B.SetBinContent(i_cnt+1, len(parB_ls)-pk_j, vcov)

               ccov_B.cd()

               hcov_B.SetStats(0)
               hcov_B.SetMinimum(-100)
               hcov_B.SetMaximum(+100)
               hcov_B.SetMarkerSize          (0.5     if len(parB_ls) > 10 else 1) #max(0.5, 4.0/len(parB_ls))
               ROOT.gStyle.SetPaintTextFormat('.1f' if len(parB_ls) > 10 else '.2f')
               hcov_B.Draw('colz,text')

               hcov_B.GetXaxis().SetNdivisions(-414)
               hcov_B.GetYaxis().SetNdivisions(-414)
               hcov_B.GetXaxis().SetLabelSize  (0.6 * hcov_B.GetXaxis().GetLabelSize  ())
               hcov_B.GetYaxis().SetLabelSize  (0.7 * hcov_B.GetYaxis().GetLabelSize  ())
               hcov_B.GetXaxis().SetLabelOffset(1.0 * hcov_B.GetXaxis().GetLabelOffset())
               hcov_B.GetYaxis().SetLabelOffset(1.0 * hcov_B.GetYaxis().GetLabelOffset())
               hcov_S.GetXaxis().LabelsOption("v")
               hcov_B.Draw('axis,same')

               txtTL = ROOT.TLatex(L+(1-R-L)*0.00, (1-T)+T*.150, opts.txtTL)
               txtTL.SetTextAlign(11)
               txtTL.SetTextSize(0.015)
               txtTL.SetTextFont(42)
               txtTL.SetNDC()
               txtTL.Draw('same')

               txtTR = ROOT.TLatex(L+(1-R-L)*1.00, (1-T)+T*.150, opts.txtTR)
               txtTR.SetTextAlign(31)
               txtTR.SetTextSize(0.015)
               txtTR.SetTextFont(42)
               txtTR.SetNDC()
               txtTR.Draw('same')

               for ext in ext_ls: ccov_B.SaveAs(opts.output_dir+'/EvolutionPlots_OnlyB/'+pk_i_tag+'_postfit_covar_B.'+ext)

               ccov_B.Close()
       ### ----------------------------------------------------------------------------------------

       ### COVARIANCE [S] -------------------------------------------------------------------------
        if not opts.only_fitB:


            parS_ls = []

            for k in cov_fitS_dc.keys():
                parS_ls.extend(cov_fitS_dc[k].keys())

            parS_ls = [x for x in parS_ls if "bin" not in x]

            parS_ls = sorted(set(parS_ls))

            if opts.poi in parS_ls: parS_ls.append(parS_ls.pop(parS_ls.index(opts.poi)))

            for pk_i in range(0, len(parS_ls)):

                pk_i_tag = parkey_dc[parS_ls[pk_i]] if parS_ls[pk_i] in parkey_dc else parS_ls[pk_i]
                ccov_S = ROOT.TCanvas('ccov_S'+pk_i_tag, 'ccov_S'+pk_i_tag, 750, 1500)

                L, R = 0.330, 0.140
                T, B = 0.020, 0.100

                ccov_S.SetLeftMargin  (L)
                ccov_S.SetRightMargin (R)
                ccov_S.SetTopMargin   (T)
                ccov_S.SetBottomMargin(B)

                hcov_S = ROOT.TH2F('hcov_S'+pk_i_tag, '', len(INPUT_FILES), 0, len(INPUT_FILES), len(parS_ls), 0, len(parS_ls))

                for i_cnt, i_inpf in enumerate(INPUT_FILES):

                    ctg = i_inpf.split("fitDiagnostics_asimov_sig1_r_combined_",1)[1][:-5]

                    hcov_S.GetXaxis().SetBinLabel(i_cnt+1, ctg)

                    for pk_j in range(0, len(parS_ls)):

                        pk_j_tag = parkey_dc[parS_ls[pk_j]] if parS_ls[pk_j] in parkey_dc else parS_ls[pk_j]

                        hcov_S.GetYaxis().SetBinLabel(len(parS_ls)-pk_j, pk_j_tag)

                        vcov = cov_value(cov_fitS_dc[ctg], parS_ls[pk_i], parS_ls[pk_j])

                        if vcov:
                            vcov = vcov*100
                            hcov_S.SetBinContent(i_cnt+1, len(parS_ls)-pk_j, vcov)

                ccov_S.cd()

                hcov_S.SetStats(0)
                hcov_S.SetMinimum(-100)
                hcov_S.SetMaximum(+100)
                hcov_S.SetMarkerSize          (0.5     if len(parS_ls) > 10 else 1) #max(0.5, 4.0/len(parS_ls)))
                ROOT.gStyle.SetPaintTextFormat('.1f' if len(parS_ls) > 10 else '.2f')
                hcov_S.Draw('colz,text')

                hcov_S.GetXaxis().SetNdivisions(-414)
                hcov_S.GetYaxis().SetNdivisions(-414)
                hcov_S.GetXaxis().SetLabelSize  (0.6 * hcov_S.GetXaxis().GetLabelSize  ())
                hcov_S.GetYaxis().SetLabelSize  (0.7 * hcov_S.GetYaxis().GetLabelSize  ())
                hcov_S.GetXaxis().SetLabelOffset(1.0 * hcov_S.GetXaxis().GetLabelOffset())
                hcov_S.GetYaxis().SetLabelOffset(1.0 * hcov_S.GetYaxis().GetLabelOffset())
                hcov_S.GetXaxis().LabelsOption("v")
                hcov_S.Draw('axis,same')

                txtTL = ROOT.TLatex(L+(1-R-L)*0.00, (1-T)+T*.150, opts.txtTL)
                txtTL.SetTextAlign(11)
                txtTL.SetTextSize(0.015)
                txtTL.SetTextFont(42)
                txtTL.SetNDC()
                txtTL.Draw('same')

                txtTR = ROOT.TLatex(L+(1-R-L)*1.00, (1-T)+T*.150, opts.txtTR)
                txtTR.SetTextAlign(31)
                txtTR.SetTextSize(0.015)
                txtTR.SetTextFont(42)
                txtTR.SetNDC()
                txtTR.Draw('same')

                for ext in ext_ls: ccov_S.SaveAs(opts.output_dir+'/EvolutionPlots_S+B/'+pk_i_tag+'_postfit_covar_S.'+ext)

                ccov_S.Close()
