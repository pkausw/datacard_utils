#!/usr/bin/env python2
import ROOT
import math
import json
import argparse
import CombineHarvester.CombineTools.plotting as plot
import CombineHarvester.CombineTools.combine.rounding as rounding
import numpy as np
import pdb
import sys, os
sys.path.append(os.getcwd())

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.AddDirectory(0)

#-- Arguments
# //--------------------------------------------
parser = argparse.ArgumentParser()
#MAIN ARGS
parser.add_argument('--input' ,'-i', help='Input json file for observed results')
parser.add_argument('--asimov-input', help='Input json file for asimov/expected results')
parser.add_argument('--output', '-o', help='Name of output file to create (without .pdf extension)')
parser.add_argument('--translate', '-t', help='json file for remapping of parameter names')
parser.add_argument('--POI', default=None, help='Specify a POI to draw') #E.g. 'r'
parser.add_argument('--blind', action='store_true', help='Do not print best fit signal strength')
#OTHERS
parser.add_argument("--onlyfirstpage", metavar="onlyfirstpage", default=False, help="Only display the first page", nargs='?', const=1)
parser.add_argument('--units', default=None, help='Add units to the best-fit parameter value')
parser.add_argument('--per-page', type=int, default=30, help='Number of parameters to show per page')
parser.add_argument('--cms-label', default='', help='Label next to the CMS logo')
parser.add_argument("--pullDef",  default=None, help="Choose the definition of the pull, see HiggsAnalysis/CombinedLimit/python/calculate_pulls.py for options")
args = parser.parse_args()

# //--------------------------------------------
# //--------------------------------------------

externalPullDef = False
if args.pullDef is not None:
    externalPullDef = True
    import HiggsAnalysis.CombinedLimit.calculate_pulls as CP

#-- Returns translated name if key found in json dict, else returns arg
def Translate(name, ndict):
    return ndict[name] if name in ndict else name

#-- Rounding nominal, uperror, downerror
def GetRounded(nom, e_hi, e_lo):
    if e_hi < 0.0:
        e_hi = 0.0
    if e_lo < 0.0:
        e_lo = 0.0
    rounded = rounding.PDGRoundAsym(nom,
            e_hi if e_hi != 0.0 else 1.0,
            e_lo if e_lo != 0.0 else 1.0)
    s_nom = rounding.downgradePrec(rounded[0],rounded[2])
    s_hi = rounding.downgradePrec(rounded[1][0][0],rounded[2]) if e_hi != 0.0 else '0'
    s_lo = rounding.downgradePrec(rounded[1][0][1],rounded[2]) if e_lo != 0.0 else '0'
    return (s_nom, s_hi, s_lo)

#Load json output of combineTool.py -M Impacts (observed)
data = {}
with open(args.input) as jsonfile:
    data = json.load(jsonfile)

#Load json output of combineTool.py -M Impacts (expected/asimov)
asidata = {}
with open(args.asimov_input) as asifile:
    asidata = json.load(asifile)

#Set global plotting style
plot.ModTDRStyle(l=0.4, b=0.1, width=900,height=700)
# plot.ModTDRStyle(l=0.4, b=0.1, width=1300,height=1000)

# We will assume the first POI is the one to plot
POIs = [ele['name'] for ele in data['POIs'] if not "MASS" in ele['name']]
POIs_fit = [ele['fit'] for ele in data['POIs'] if not "MASS" in ele['name']]

# sort
sortPOIs = np.argsort(POIs)
POIs = [POIs[i] for i in sortPOIs]
POIs_fit = [POIs_fit[i] for i in sortPOIs]

nPOIs = len(POIs)

print POIs,nPOIs

#json dictionary to translate parameter names
translate = {}
if args.translate is not None:
    with open(args.translate) as jsonfile:
        translate = json.load(jsonfile)
poi_translated = [Translate(poi,translate) for poi in POIs] #Get translated POI name (if available)

bestfitvalues={}
for i, (POI, POI_fit) in enumerate(zip(POIs, POIs_fit)):
    s_nom, s_hi, s_lo = GetRounded(POI_fit[1], POI_fit[2] - POI_fit[1], POI_fit[1] - POI_fit[0])
    bestfitvalues[POI]=POI_fit[1]

data['params'].sort(key=lambda x: abs(sum([(abs(x['impact_%s' % poi])/bestfitvalues[poi])**2. for poi in POIs]))**0.5, reverse=True)

#Set the number of parameters per page (show) and the number of pages (n)
show = args.per_page
n = int(math.ceil(float(len(data['params'])) / float(show)))
if args.onlyfirstpage == True: n = 1

colors = {
    'Gaussian': 1,
    'Poisson': 8,
    'AsymmetricGaussian': 9,
    'Unconstrained': 39,
    'Unrecognised': 2
}
color_hists = {}
color_group_hists = {}
for name, col in colors.iteritems():
    color_hists[name] = ROOT.TH1F()
    plot.Set(color_hists[name], FillColor=col, Title=name)

seen_types = set()


# //--------------------------------------------
# //--------------------------------------------

for page in xrange(n):
    canv = ROOT.TCanvas(args.output, args.output)
    n_params = len(data['params'][show * page:show * (page + 1)])
    pdata = data['params'][show * page:show * (page + 1)]
    asipdata = asidata["params"]
    print '>> Doing page %i, have %i parameters' % (page, n_params)

    #-- Set top/bottom margins
    # ROOT.gStyle.SetPadBottomMargin(0.075)
    ROOT.gStyle.SetPadBottomMargin(0.1)
    ROOT.gStyle.SetPadTopMargin(0.10 if args.blind else 0.15) #If not displaying best-fit poi, reduce top margin

    #-- Set bkg color of every other line to gray
    boxes = []
    for i in xrange(n_params):
        y1 = ROOT.gStyle.GetPadBottomMargin()
        y2 = 1. - ROOT.gStyle.GetPadTopMargin()
        h = (y2 - y1) / float(n_params)
        y1 = y1 + float(i) * h
        y2 = y1 + h
        x1 = 0 #Start from canvas' left border
        x2 = 0.985 #Fine-tuned such that gray bkg (for every other param) stops at vertical black line #or 1 to reach right-end of canvas
        box = ROOT.TPaveText(x1, y1, x2, y2, 'NDC')
        plot.Set(box, TextSize=0.01, BorderSize=0, FillColor=0, TextAlign=12, Margin=0.005)
        if i % 2 == 0: box.SetFillColor(18) #Gray
        box.Draw()
        boxes.append(box)

    #-- Pad style
    x_pulls=0.45     # fraction of the canvas used for names and pulls, rest is for impacts
    pads = plot.MultiRatioSplitColumns([x_pulls]+[(1.-x_pulls)/nPOIs*0.98 for j in range(nPOIs)], [0. for j in range(nPOIs+2)], [0. for j in range(nPOIs+2)])
    for j in range(nPOIs+1):
        pads[j].SetGrid(1, 0)
        pads[j].SetTickx(1)

    #-- Define main objects
    h_pulls = ROOT.TH2F("pulls", "pulls", 1, -1.99, 1.99, n_params, 0, n_params) #TH2F defining the frame, bkg style, etc.
    g_pulls = ROOT.TGraphAsymmErrors(n_params) #Pulls obs
    g_pullsA = ROOT.TGraphAsymmErrors(n_params) #Pulls exp
    g_impacts_hi = ROOT.TGraphAsymmErrors(n_params) #Obs impact
    g_impacts_lo = ROOT.TGraphAsymmErrors(n_params) #Obs impact
    g_impactsA_hi = ROOT.TGraphAsymmErrors(n_params) #Exp impact
    g_impactsA_lo = ROOT.TGraphAsymmErrors(n_params) #Exp impact
    g_check = ROOT.TGraphAsymmErrors()

    g_impacts_hi = [ROOT.TGraphAsymmErrors(n_params) for j in range(nPOIs)]
    g_impacts_lo = [ROOT.TGraphAsymmErrors(n_params) for j in range(nPOIs)]
    g_impactsA_hi = [ROOT.TGraphAsymmErrors(n_params) for j in range(nPOIs)]
    g_impactsA_lo = [ROOT.TGraphAsymmErrors(n_params) for j in range(nPOIs)]

    max_impact = [0. for j in range(nPOIs)]
    max_impactA = [0. for j in range(nPOIs)]
    text_entries = []
    redo_boxes = []
    #-- Read values, fill pull histogram
    for p in xrange(n_params):
        i = n_params - (p + 1)
        thisname = pdata[p]['name']
        asipnum = -1
        asipnumfound = False
        while not asipnumfound:
            asipnum +=1
            if asipnum >= len(asipdata)-1:
                print "too many vars in asimov data ", thisname,asipnum,p,i
                break
                # raise Exception('ERROR: the parameter with name {}'.format(thisname)
                #        +' has no counterpart in the expected results!')
            if asipdata[asipnum]["name"]==thisname:
                 asipnumfound = True
        pre = pdata[p]['prefit']
        fit = pdata[p]['fit']
        preA = asipdata[asipnum]['prefit']
        fitA = asipdata[asipnum]['fit']
        tp = pdata[p]['type']
        seen_types.add(tp)

        if pdata[p]['type'] != 'Unconstrained':
            pre_err_hi = (pre[2] - pre[1])
            pre_err_lo = (pre[1] - pre[0])

            if externalPullDef:
                fit_err_hi = (fit[2] - fit[1])
                fit_err_lo = (fit[1] - fit[0])
                pull, pull_hi, pull_lo = CP.returnPullAsym(args.pullDef,fit[1],pre[1],fit_err_hi,pre_err_hi,fit_err_lo,pre_err_lo)
            else:
                pull = fit[1] - pre[1]
                pull = (pull/pre_err_hi) if pull >= 0 else (pull/pre_err_lo)
                pull_hi = fit[2] - pre[1]
                pull_hi = (pull_hi/pre_err_hi) if pull_hi >= 0 else (pull_hi/pre_err_lo)
                pull_hi = pull_hi - pull
                pull_lo = fit[0] - pre[1]
                pull_lo = (pull_lo/pre_err_hi) if pull_lo >= 0 else (pull_lo/pre_err_lo)
                pull_lo =  pull - pull_lo

            g_pulls.SetPoint(i, pull, float(i) + 0.5)
            g_pulls.SetMarkerSize(0.3)
            g_pulls.SetPointError(i, pull_lo, pull_hi, 0., 0.)

            pre_err_hi = (preA[2] - preA[1])
            pre_err_lo = (preA[1] - preA[0])
            if externalPullDef:
                fit_err_hi = (fit[2] - fit[1])
                fit_err_lo = (fit[1] - fit[0])
                pull, pull_hi, Apull_lo = CP.returnPullAsym(args.pullDef,fit[1],pre[1],fit_err_hi,pre_err_hi,fit_err_lo,pre_err_lo)
            else:
                pull = fitA[1] - preA[1]
                pull = (pull/pre_err_hi) if pull >= 0 else (pull/pre_err_lo)
                pull_hi = fitA[2] - preA[1]
                pull_hi = (pull_hi/pre_err_hi) if pull_hi >= 0 else (pull_hi/pre_err_lo)
                pull_hi = pull_hi - pull
                pull_lo = fitA[0] - preA[1]
                pull_lo = (pull_lo/pre_err_hi) if pull_lo >= 0 else (pull_lo/pre_err_lo)
                pull_lo =  pull - pull_lo

            g_pullsA.SetPoint(i, pull, float(i) + 0.5)
            g_pullsA.SetPointError(
                i, pull_lo, pull_hi, 0.5, 0.5)

        else: #Unconstrained, hide point
            g_pulls.SetPoint(i, 0., 9999.)
            y1 = ROOT.gStyle.GetPadBottomMargin()
            y2 = 1. - ROOT.gStyle.GetPadTopMargin()
            x1 = ROOT.gStyle.GetPadLeftMargin()
            h = (y2 - y1) / float(n_params)
            y1 = y1 + ((float(i)+0.5) * h)
            x1 = x1 + (1 - pads[0].GetRightMargin() -x1)/2.
            s_nom, s_hi, s_lo = GetRounded(fit[1], fit[2] - fit[1], fit[1] - fit[0])
            text_entries.append((x1, y1, '%s #scale[0.7]{#kern[-0.1]{#lower[-0.7]{#plus%s}}} #scale[0.7]{#kern[-1.25]{#lower[0.2]{#minus%s}}}' % (s_nom, s_hi, s_lo)))
            redo_boxes.append(i)

        for j in range(nPOIs):
            g_impacts_hi[j].SetPoint(i, 0, float(i) + 0.5)
            g_impacts_lo[j].SetPoint(i, 0, float(i) + 0.5)
            g_impactsA_hi[j].SetPoint(i, 0, float(i) + 0.5)
            g_impactsA_lo[j].SetPoint(i, 0, float(i) + 0.5)

        imp = [pdata[p][poi] for poi in POIs]
        impA = [asipdata[asipnum][poi] for poi in POIs]

        for j in range(nPOIs):
            max_impact[j] = max(max_impact[j], abs(imp[j][1] - imp[j][0]), abs(imp[j][2] - imp[j][1]))
            max_impactA[j] = max(max_impactA[j], abs(impA[j][1] - impA[j][0]), abs(impA[j][2] - impA[j][1]))
            col = colors.get(tp, 2)
            if impA[j][2]-impA[j][1]>0:
                g_impactsA_hi[j].SetPointError(i, 0, impA[j][2] - impA[j][1], 0.49, 0.49)
                g_impactsA_lo[j].SetPointError(i, impA[j][1] - impA[j][0], 0, 0.49, 0.49)
            else:
                g_impactsA_hi[j].SetPointError(i,  impA[j][1] - impA[j][2],0, 0.49, 0.49)
                g_impactsA_lo[j].SetPointError(i, 0, impA[j][0] - impA[j][1],  0.49, 0.49)
            if imp[j][2]-imp[j][1]>0:
                g_impacts_hi[j].SetPointError(i, 0, imp[j][2] - imp[j][1], 0.,0.)
                g_impacts_lo[j].SetPointError(i, imp[j][1] - imp[j][0], 0, 0.,0.)
            else:
                g_impacts_hi[j].SetPointError(i,  imp[j][1] - imp[j][2],0,0.,0.)
                g_impacts_lo[j].SetPointError(i, 0, imp[j][0] - imp[j][1],  0.,0.)

        thisname = Translate(thisname,translate)
        h_pulls.GetYaxis().SetBinLabel(i + 1, ('#color[%i]{%s}'% (col, thisname)))

    #-- Style and draw the pulls histo
    if externalPullDef:
        plot.Set(h_pulls.GetXaxis(), TitleSize=0.02, LabelSize=0.02, Title=CP.returnTitle(args.pullDef))
    else:
        # plot.Set(h_pulls.GetXaxis(), TitleSize=0.035, LabelSize=0.02, Title='(#hat{#theta} - #theta_{0}) / #Delta #theta')
        plot.Set(h_pulls.GetXaxis(), TitleSize=0.035, LabelSize=0.03, Title='(#hat{#theta} #minus #theta_{0}) / #Delta#theta', Ndivisions=505)
        # h_pulls.GetXaxis().SetTitleOffset(0.85)
        h_pulls.GetXaxis().SetTitleOffset(1.2)
        h_pulls.GetXaxis().CenterTitle(ROOT.kTRUE)
    # plot.Set(h_pulls.GetYaxis(), LabelSize=0.03, TickLength=0.0)
    plot.Set(h_pulls.GetYaxis(), LabelSize=0.03, TickLength=0.0)
    h_pulls.GetYaxis().LabelsOption('v')
    h_pulls.Draw()

    #-- Draw impacts histogram
    for i in redo_boxes:
        newbox = boxes[i].Clone()
        newbox.Clear()
        newbox.SetY1(newbox.GetY1()+0.005)
        newbox.SetY2(newbox.GetY2()-0.005)
        newbox.SetX1(ROOT.gStyle.GetPadLeftMargin()+0.001)
        newbox.SetX2(0.4-0.001)
        newbox.Draw()
        boxes.append(newbox)
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(42)
    latex.SetTextSize(0.02)
    latex.SetTextAlign(22)
    latex.SetTextColor(ROOT.kBlack)
    for entry in text_entries:
        latex.DrawLatex(*entry)


	ndivs = [505, 505, 404, 505]
	# ratioAxis = [1.35, 1.5, 1.65, 1.065]
	ratioAxis = [1.35, 1.5, 1.65, 1.05]

    h_impacts = []
    for j, poi in enumerate(POIs):
        # Go to the other pad and draw the impacts histo
        pads[j+1].cd()
        if max_impact[j] == 0.:
            max_impact[j] = 1E-6  # otherwise the plotting gets screwed up

        # h_impact = ROOT.TH2F("impacts_%s" % poi, "impacts", 6, -max_impact[j] * 1.31, max_impact[j] * 1.31, n_params, 0, n_params)
        h_impact = ROOT.TH2F("impacts_%s" % poi, "impacts", 6, -max_impact[j] * ratioAxis[j], max_impact[j] * ratioAxis[j], n_params, 0, n_params)
        # plot.Set(h_impact.GetXaxis(), LabelSize=0.02, TitleSize=0.035, Ndivisions=505, Title='#Delta#hat{%s}' % (Translate(poi, translate)))
        plot.Set(h_impact.GetXaxis(), LabelSize=0.03, TitleSize=0.035, Ndivisions=ndivs[j], Title='#Delta#hat{%s}' % (Translate(poi, translate)))
        h_impact.GetXaxis().CenterTitle(ROOT.kTRUE)
        h_impact.GetXaxis().SetTitleOffset(1.2)
        plot.Set(h_impact.GetYaxis(), LabelSize=0, TickLength=0.0)
        h_impact.Draw()
        h_impacts.append(h_impact)

    #-- Draw the pulls graph
    pads[0].cd()
    alpha = 0.7
    plot.Set(g_pulls, MarkerSize=0.5, LineWidth=2)
    g_pullsA.SetLineWidth(0)
    g_pullsA.SetFillColor(plot.CreateTransparentColor(15, alpha))
    g_pullsA.Draw('2SAME')
    g_pulls.Draw('PSAME')

    #-- Draw impacts graphs
    pads[1].cd()
    alpha = 0.5
    for j in range(nPOIs):
        pads[j+1].cd()
        g_impactsA_hi[j].SetFillColor(plot.CreateTransparentColor(46, alpha))
        g_impactsA_hi[j].SetLineWidth(0)
        g_impactsA_lo[j].SetLineWidth(0)
        g_impactsA_lo[j].SetFillColor(plot.CreateTransparentColor(38, alpha))
        g_impacts_hi[j].SetLineWidth(2)
        g_impacts_lo[j].SetLineWidth(2)
        g_impacts_hi[j].SetLineStyle(1)
        g_impactsA_hi[j].SetMarkerSize(0)
        g_impacts_hi[j].SetLineColor(ROOT.kRed+1)
        g_impacts_lo[j].SetLineColor(ROOT.kAzure+4)
        g_impactsA_lo[j].SetLineStyle(1)
        g_impactsA_lo[j].SetLineWidth(0)
        g_impacts_lo[j].SetMarkerSize(0)
        g_impacts_hi[j].SetMarkerSize(0)
        g_impactsA_hi[j].Draw('2 SAME')
        g_impactsA_lo[j].Draw('2 SAME')
        g_impacts_hi[j].Draw('E SAME')
        g_impacts_lo[j].Draw('E SAME')
        pads[j+1].RedrawAxis()
    pads[j+1].RedrawAxis()
    pads[j+1].RedrawAxis()

    #-- Legend, CMS logo, best-fit value
    legendbox = [0.001, 0.91, 0.999, 0.999] #x1, y1, x2, y2
    legendtextsize = 0.03
    legend = ROOT.TLegend(legendbox[0], legendbox[1], legendbox[2], legendbox[3], '', 'NBNDC')
    legend.SetFillStyle(0)
    legend.SetTextSize(legendtextsize)
    legend.SetNColumns(3)
    legend.AddEntry(g_pulls, 'Fit constraint (obs.)', 'LP')
    legend.AddEntry(g_impacts_hi[0], '+1#sigma Impact (obs.)', 'l')
    legend.AddEntry(g_impacts_lo[0], '-1#sigma Impact (obs.)', 'l')
    legend.AddEntry(g_pullsA, 'Fit constraint (exp.)', 'F')
    legend.AddEntry(g_impactsA_hi[0], '+1#sigma Impact (exp.)', 'F')
    legend.AddEntry(g_impactsA_lo[0], '-1#sigma Impact (exp.)', 'F')
    legend.Draw()

    #-- Draw CMS logo
    docmslogo = True
    cmslogopad = pads[0]
    left = 0.15; top = 0.87 #Position of 'CMS' label
    if args.blind:
        left = 0.87; top = 0.92
        if args.cms_label != "": left = 0.78

    if docmslogo:

        #-- Use built-in CombineHarvester function
        #-- Draw labels manually (more flexible)
        CMS_text = ROOT.TLatex(left, top, "CMS")
        CMS_text.SetNDC()
        CMS_text.SetTextColor(ROOT.kBlack)
        CMS_text.SetTextFont(61)
        CMS_text.SetTextAlign(11)
        CMS_text.SetTextSize(0.05)

        extraText = ROOT.TLatex(left+0.09, top, args.cms_label)
        extraText.SetNDC()
        extraText.SetTextFont(52)
        extraText.SetTextSize(0.04)

        CMS_text.Draw('same') #Draw 'CMS'
        extraText.Draw('same') #Draw extra label, if any

    #-- Draw best-fit value and uncertainties
    for i, (POI, POI_fit) in enumerate(zip(POIs, POIs_fit)):
        s_nom, s_hi, s_lo = np.round(POI_fit[1],2), np.round(POI_fit[2] - POI_fit[1],2), np.round(POI_fit[1] - POI_fit[0],2)
        if not args.blind:
            # plot.DrawTitle(pad=pads[i+1], text='%s' % ( '#hat{%s}' % poi_translated[i] ) +' = %s^{ #plus%s}_{ #minus%s}%s' % (s_nom, s_hi, s_lo, '' if args.units is None else ' '+args.units ), align=2, textOffset=0.1, textSize=0.22)
            plot.DrawTitle(pad=pads[i+1], text='%s' % ( '#hat{%s}' % poi_translated[i] ) +' = %s^{ #plus%s}_{ #minus%s}%s' % (s_nom, s_hi, s_lo, '' if args.units is None else ' '+args.units ), align=2, textOffset=0.1, textSize=0.2)

    #-- Write to .pdf file
    extra = ''
    if page == 0:
        extra = '('
    if page == n - 1:
        extra = ')'
    canv.Print('.pdf%s' % extra)
# //--------------------------------------------
# //--------------------------------------------
