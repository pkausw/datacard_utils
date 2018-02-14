import ROOT
import sys
import os
import CMS_lumi
import re
from array import array
ROOT.gROOT.SetBatch(True)


color_dict = {}
color_dict["ttbarOther"]=ROOT.kRed-7
color_dict["ttbarPlusCCbar"]=ROOT.kRed+1
color_dict["ttbarPlusB"]=ROOT.kRed-2
color_dict["ttbarPlus2B"]=ROOT.kRed+2
color_dict["ttbarPlusBBbar"]=ROOT.kRed+3
color_dict["singlet"]=ROOT.kMagenta
color_dict["zjets"]=ROOT.kGreen-3
color_dict["wjets"]=ROOT.kGreen-7
color_dict["vjets"]=ROOT.kGreen-3
color_dict["ttbarW"]=ROOT.kBlue-10
color_dict["ttbarZ"]=ROOT.kBlue-6
color_dict["ttbarV"]=ROOT.kBlue-10
color_dict["diboson"]=ROOT.kAzure+2
color_dict["QCD"]=ROOT.kYellow
color_signal=ROOT.kCyan
color_dict["ttH_hbb"]=color_signal
color_dict["ttH_hcc"]=color_signal
color_dict["ttH_htt"]=color_signal
color_dict["ttH_hgg"]=color_signal
color_dict["ttH_hgluglu"]=color_signal
color_dict["ttH_hww"]=color_signal
color_dict["ttH_hzz"]=color_signal
color_dict["ttH_hzg"]=color_signal
color_dict["ttH"]=color_signal
color_dict["total_background"]=ROOT.kBlack
color_dict["total_signal"]=color_signal
color_dict["total_covar"]=ROOT.kBlack
color_dict["total"]=ROOT.kBlack
color_dict["data"]=ROOT.kBlack

latex_dict = {}
latex_dict["ttbarOther"]="t#bar{t}+lf"
latex_dict["ttbarPlusCCbar"]="t#bar{t}+c#bar{c}"
latex_dict["ttbarPlusB"]="t#bar{t}+b"
latex_dict["ttbarPlus2B"]="t#bar{t}+2b"
latex_dict["ttbarPlusBBbar"]="t#bar{t}+b#bar{b}"
latex_dict["singlet"]="single t"
latex_dict["zjets"]="Z+jets"
latex_dict["wjets"]="W+jets"
latex_dict["vjets"]="V+jets"
latex_dict["ttbarW"]="t#bar{t}+W"
latex_dict["ttbarZ"]="t#bar{t}+Z"
latex_dict["ttbarV"]="t#bar{t}+V"
latex_dict["diboson"]="diboson"
latex_dict["QCD"]="QCD"
latex_dict["ttH_hbb"]="t#bar{t}H"
latex_dict["ttH_hcc"]="t#bar{t}H"
latex_dict["ttH_htt"]="t#bar{t}H"
latex_dict["ttH_hgg"]="t#bar{t}H"
latex_dict["ttH_hgluglu"]="t#bar{t}H"
latex_dict["ttH_hww"]="t#bar{t}H"
latex_dict["ttH_hzz"]="t#bar{t}H"
latex_dict["ttH_hzg"]="t#bar{t}H"
latex_dict["ttH"]="t#bar{t}H_{SM}"
latex_dict["total_background"]="total background"
latex_dict["total_signal"]="signal"
latex_dict["total_covar"]="bla"
latex_dict["total"]="total s+b"
latex_dict["data"]="data"

tick_length_xaxis = 0.05
tick_length_yaxis = 0.03
tick_length_rxaxis = 0.11
tick_length_ryaxis = 0.04
axis_label_font = 42
axis_label_offset = 0.01
axis_label_size = 0.05

xaxis_title_offset = 1.0
yaxis_title_offset = 0.55
axis_title_font = 42
axis_title_size = 0.14

sf_stack_ratio = 1./2.25

categoy_label_font_size = 0.045


def GetSortedProcesses(processes_histos_dict):
    order = [
        'diboson',
        
        'ttbarW',
        'ttbarZ',
        'ttbarV',
        
        'wjets',
        'zjets',
        'vjets',

        'singlet',

        'ttbarPlusBBbar',
        'ttbarPlus2B',
        'ttbarPlusB',
        'ttbarPlusCCbar',
        'ttbarOther',
        'total_background',

        'ttH_hgg',
        'ttH_hzg',
        'ttH_hcc',
        'ttH_hgluglu',
        'ttH_htt',
        'ttH_hzz',
        'ttH_hww',
        'total_signal',
        
        'data',
        'total',
    ]

    ordered_processes = []
    for proc in order:
        if proc in processes_histos_dict:
            ordered_processes.append( [ proc, processes_histos_dict[proc] ] )

    return ordered_processes


def MergeProcesses(processes_histos_dict, proc_A, proc_B, proc_Sum):
    """
    Merge processes A and B to new process Sum
    
    Removes the individual process A and B from the
    processes_histos_dict and adds a new process A+B.
    Should be safe if any of A or B does not exist.

    Use e.g. to merge ttW and ttZ.
    """

    new_dict = processes_histos_dict

#    intA = new_dict[proc_A].Integral()
#    intB = new_dict[proc_B].Integral()
#    print proc_A, ": ", intA 
#    print proc_B, ": ", intB
#    print  "Sum: ", intA+intB
    
    if proc_A in new_dict or proc_B in new_dict:
        if proc_A in new_dict:
            new_dict[proc_Sum] = new_dict[proc_A].Clone()
            if proc_B in new_dict:
                new_dict[proc_Sum].Add( new_dict[proc_B] )
        else:
            new_dict[proc_Sum] = new_dict[proc_B].Clone()

        if proc_A in new_dict:
            new_dict.pop(proc_A)
        if proc_B in new_dict:
            new_dict.pop(proc_B)

#    print proc_Sum, ": ", new_dict[proc_Sum].Integral()
        
    return new_dict

                                
def ColorizeHistograms(processes_histos_dict):
    for process in processes_histos_dict:
        processes_histos_dict[process].SetLineColor(ROOT.kBlack)
        processes_histos_dict[process].SetFillColor(color_dict[process])
    return 0

def SetPadMargins():
    ROOT.gStyle.SetFrameLineWidth(2);
    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadRightMargin(0.02)
    ROOT.gStyle.SetPadTopMargin(0.08)
    ROOT.gStyle.SetPadBottomMargin(0.0)
    

def GetCanvas(canvas_name):
    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas(canvas_name,"",800,850)
    c.Divide(1,2)
    c.GetPad(1).SetPad(0.0,0.3,1.0,1.0)
    c.GetPad(2).SetPad(0.0,0.0,1.0,0.3)
    c.GetPad(1).SetBottomMargin(0)
    c.GetPad(1).SetTicks(1,1)
    c.GetPad(2).SetTopMargin(0)
    c.GetPad(2).SetBottomMargin(0.32)
    c.GetPad(2).SetTicks(1,1)
    c.cd();
    return c

# returns directory in tfile***    
def GetDirectory(fitfile,directory):
    dir_ = fitfile.Get(directory)
    print "dir ", dir_
    return dir_

#returns a list of all channels in the given directory***
def GetChannels(directory):
    channels = []
    for key in directory.GetListOfKeys():
        if key.IsFolder():
            channels.append(key.GetName())
    return channels

#returns a dictionary with all channels in the directory as keys and a list of all the process in a channel as value***
def GetProcessesInCategories(directory,categories):
    dictt = {}
    for cat in categories:
        processes = []
        cat_dir = directory.Get(cat)
        for key in cat_dir.GetListOfKeys():
            processes.append(key.GetName())
        dictt[cat]=processes
    return dictt

#returns a dictionary with channel -> processes -> and the corresponding histograms, so dict["ch1"]["ttbarOther"]->corresponding histogram
#the histograms only have those bins left where the yield of the total background was greater than 0.1 starting from the right side of its histogram ( this was done to cut away basically "empty" bins )***
def GetHistosForCategoriesProcesses(directory,categories_processes_dict):
    dictt = {}
    # loop over categories ("ch1","ch2",...)
    for cat in categories_processes_dict:
        #print cat
        # get the "chX" category from the mlfit file
        cat_dir = directory.Get(cat)
        # create a dictionary for the category/channel where the process will be the key and its histogram the value
        dictt[cat] = {}
        # starting from the right side of the histogram, find the bin in the "total_background" histogram, where the bin content < 0.1 to cut away "empty" bins
        nbins = FindNewBinNumber(cat_dir.Get("total_background"))
        for process in categories_processes_dict[cat]:
            #print process
            # drop the covariance matrix since its a th2f
            if "covar" in process:
                continue
            # get the original histogram for the cateogry and the process from the mlfit file
            histo = cat_dir.Get(process)
            if process=="data":
                # convert the tgraphasymmerror to a histogram, drop the unnecessary bins, set asymmetric errors and save the resulting histo in the dictionary
                dictt[cat][process] = GetHistoFromTGraphAE(histo,cat,nbins)
            else:
                # drop the unnecessary bins and save the resulting histo in the dictionary
                dictt[cat][process] = GetHistoWithoutZeroBins(histo,cat,nbins)
    return dictt

#starting from the rigth side of the histogram, finds the bin number where the first time the bin content is smaller than 0.1*** 
def FindNewBinNumber(histo):
    nbins_old = histo.GetNbinsX()
    nbins_new = 0
    # loop starting from nbins_old to 1 with stepsize -1, so starting from the right side of a histogram
    for i in range(nbins_old,0,-1):
        # if the first bin with bin content > 0.1 is found, set this value as the new maximum bin number
        if histo.GetBinContent(i)>0.1:
            nbins_new = i
            break
    return nbins_new

# drops all bins in a histogram with binnumber > nbins_new and returns it as a new histogram*** 
def GetHistoWithoutZeroBins(histo_old,category,nbins_new_):
    nbins_old = histo_old.GetNbinsX()
    nbins_new = nbins_new_
    # add category to name of histogram so each histogram has a different name to avoid problems with ROOT
    histo_new = ROOT.TH1F(histo_old.GetName()+"_"+category,histo_old.GetTitle(),nbins_new,0,nbins_new)
    # since we are dealing with histograms, start with bin number 1, so loop goes from 1..nbins_new
    # set bin contents and bin errors for the "new" binning
    for i in range(1,nbins_new+1,1):
        histo_new.SetBinContent(i,histo_old.GetBinContent(i))
        histo_new.SetBinError(i,histo_old.GetBinError(i))
    return histo_new

# converts the TGraphAsymmError data object in the mlfit file to a histogram (therby dropping bins again) and in addition sets asymmetric errors***
def GetHistoFromTGraphAE(tgraph,category,nbins_new_):
    nbins_old = tgraph.GetN()
    nbins_new = nbins_new_
    # add category to name of histogram so each histogram has a different name to avoid problems with ROOT
    histo = ROOT.TH1F("data_"+category,"data",nbins_new,0,nbins_new)
    # set this flag for asymmetric errors in data histogram
    histo.Sumw2(ROOT.kFALSE)
    # loop has to go from 0..nbins_new-1 for a tgraphasymmerror with nbins_new points
    for i in range(0,nbins_new,1):
        # first point (point 0) in tgraphae corresponds to first bin (bin 1 (0..1)) in histogram
        entries = tgraph.GetY()[i]
        for k in range(int(round(entries))):# rounding necessary if used with asimov dataset because entries can be non-integer in this case
            histo.Fill(i+0.5)
    # set this flag for calculation of asymmetric errors in data histogram
    histo.SetBinErrorOption(ROOT.TH1.kPoisson)
    return histo

# converts the TGraphAsymmError data object in the mlfit file to a histogram (therby dropping bins again) and in addition sets asymmetric errors***
def makeAsymErrorsForDataHisto(datahisto):
    oldname=datahisto.GetName()
    datahisto.SetName(oldname+"_old")
    binEdgeArray=array("f",[])
    nBins=datahisto.GetNbinsX()
    for i in range(1,nBins+2,1):
      binEdgeArray.append(datahisto.GetBinLowEdge(i))
      
    newHisto = ROOT.TH1F(oldname,datahisto.GetTitle(),len(binEdgeArray)-1,binEdgeArray)
    # set this flag for asymmetric errors in data histogram
    newHisto.Sumw2(ROOT.kFALSE)
    # loop has to go from 0..nbins_new-1 for a tgraphasymmerror with nbins_new points
    for i in range(1,nBins+1,1):
        # first point (point 0) in tgraphae corresponds to first bin (bin 1 (0..1)) in histogram
        entries = datahisto.GetBinContent(i)
        for k in range(int(round(entries))):# rounding necessary if used with asimov dataset because entries can be non-integer in this case
            newHisto.Fill(datahisto.GetBinCenter(i))
        #print newHisto.GetBinContent(i)  
    # set this flag for calculation of asymmetric errors in data histogram
    newHisto.SetBinErrorOption(ROOT.TH1.kPoisson)
    return newHisto

#def createGraphToDrawFromDataHist(datahisto,SoBCut=0.0):
  #nBins=datahisto.GetNbinsX()
  #theGraph=ROOT.TGraphAsymmErrors()
  
def blindDataHisto(datahisto, signalhisto, backgroundhisto,SoBCut=0.01):
    oldname=datahisto.GetName()
    datahisto.SetName(oldname+"_old")
    binEdgeArray=array("f",[])
    nBins=datahisto.GetNbinsX()
    for i in range(1,nBins+2,1):
      binEdgeArray.append(datahisto.GetBinLowEdge(i))
      
    newHisto = ROOT.TH1F(oldname,datahisto.GetTitle(),len(binEdgeArray)-1,binEdgeArray)
    # set this flag for asymmetric errors in data histogram
    newHisto.Sumw2(ROOT.kFALSE)
    startBlinding=False
    for i in range(1,nBins+1,1):
        # first point (point 0) in tgraphae corresponds to first bin (bin 1 (0..1)) in histogram
        if signalhisto.GetBinContent(i)>0 and backgroundhisto.GetBinContent(i)<=0:
          startBlinding=True
        if signalhisto.GetBinContent(i)/float(backgroundhisto.GetBinContent(i))>SoBCut:
          startBlinding=True
        if startBlinding==True:
          continue
        entries = datahisto.GetBinContent(i)
        for k in range(int(round(entries))):# rounding necessary if used with asimov dataset because entries can be non-integer in this case
            newHisto.Fill(datahisto.GetBinCenter(i))
        #print newHisto.GetBinContent(i)  
    # set this flag for calculation of asymmetric errors in data histogram
    newHisto.SetBinErrorOption(ROOT.TH1.kPoisson)
    return newHisto


# provided a mlfitfile and a directory in this file, this function returns the dict["ch1"]["ttbarOther"]->corresponding histogram dictionary***
def GetHistos(fitfile,directory):
    # get directory in mlfit file
    dirr = GetDirectory(fitfile,directory)
    # get channels/categories in this directory
    categories = GetChannels(dirr)
    # get processes in the different channels/categories as dict["chX"]->[processes]
    categories_processes_dict = GetProcessesInCategories(dirr,categories)
    # get final dictionary, e.g. dict["ch1"]["ttbarOther"]->corresponding histogram
    categories_processes_histos_dict = GetHistosForCategoriesProcesses(dirr,categories_processes_dict)
    print categories_processes_histos_dict
    return categories_processes_histos_dict

def GetDataHistogram(processes_histos_dict):
    data = None
    if "data" in processes_histos_dict:
        data = processes_histos_dict["data"]
        data.SetMarkerStyle(20)
        data.SetFillStyle(0)
    return data

def GetSignal(processes_histos_dict,background_integral):
    signal_unscaled = processes_histos_dict["total_signal"]
    signal=signal_unscaled.Clone()
    signal.SetLineColor(color_dict["total_signal"])
    signal.SetFillStyle(0)
    signal.SetLineWidth(2)
    signal_integral = signal.Integral()
    scaleFactor=0.0
    scaleMode=15
    #print signal_integral
    if signal_integral>0.:
      if scaleMode>0:
        scaleFactor=scaleMode
        signal.Scale(scaleFactor)
        return signal,scaleFactor
      else:
        scaleFactor=background_integral/signal_integral
        signal.Scale(scaleFactor)
        return signal,scaleFactor
    else:
        return None,0.

def GetLegend():
    legend = ROOT.TLegend(0.8,0.5,1.0,0.85)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.025)
    return legend

def getLegendL():
    legend=ROOT.TLegend()
    legend.SetX1NDC(0.68)
    legend.SetX2NDC(0.83)
    legend.SetY1NDC(0.83)
    legend.SetY2NDC(0.88)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.038);
    legend.SetFillStyle(0);
    return legend

def getLegendR():
    legend=ROOT.TLegend()
    legend.SetX1NDC(0.81)
    legend.SetX2NDC(0.96)
    legend.SetY1NDC(0.83)
    legend.SetY2NDC(0.88)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.038);
    legend.SetFillStyle(0);
    return legend

def AddEntry22( self, histo, label, option='L'):
    self.SetY1NDC(self.GetY1NDC()-0.045)
    width=self.GetX2NDC()-self.GetX1NDC()
    ts=self.GetTextSize()
    neglen = 0
    sscripts = re.findall("_{.+?}|\^{.+?}",label)
    for s in sscripts:
	neglen = neglen + 3
    symbols = re.findall("#[a-zA-Z]+",label)
    for symbol in symbols:
	neglen = neglen + len(symbol)-1
    newwidth=max((len(label)-neglen)*0.015*0.05/ts+0.1,width)
#    self.SetX1NDC(self.GetX2NDC()-newwidth)

    self.AddEntry(histo, label, option)
ROOT.TLegend.AddEntry22 = AddEntry22

def GetErrorGraph(histo):
    error_graph = ROOT.TGraphAsymmErrors(histo)
    error_graph.SetFillStyle(3005)
    error_graph.SetFillColor(ROOT.kBlack)
    return error_graph

def GetRatioGraph(nominator,denominator,templateHisto=None):
    ratio = ROOT.TGraphAsymmErrors(nominator.GetNbinsX())
    lowerx=0
    upperx=nominator.GetNbinsX()
    if templateHisto!=None:
      lowerx=templateHisto.GetBinLowEdge(1)
      upperx=templateHisto.GetBinLowEdge(nominator.GetNbinsX())+templateHisto.GetBinWidth(nominator.GetNbinsX())
      for i in range(1,nominator.GetNbinsX()+1,1):
        theCorrectXvalue=templateHisto.GetXaxis().GetBinCenter(i)
        #print theCorrectXvalue
        ratio.SetPoint(i-1,theCorrectXvalue,nominator.GetBinContent(i)/denominator.GetBinContent(i))
        ratio.SetPointError(i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i))
        #print i-1,theCorrectXvalue,nominator.GetBinContent(i),denominator.GetBinContent(i),nominator.GetBinContent(i)/denominator.GetBinContent(i)
        #print i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i)
    else:    
      for i in range(1,nominator.GetNbinsX()+1,1):
          ratio.SetPoint(i-1,i-1+0.5,nominator.GetBinContent(i)/denominator.GetBinContent(i))
          ratio.SetPointError(i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i))
          #print i-1,i-1+0.5,nominator.GetBinContent(i)/denominator.GetBinContent(i)
          #print i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i)
    ratio.SetMarkerStyle(20)

    ratio.GetYaxis().SetRangeUser(0.01,1.99)
    ratio.GetXaxis().SetLimits(lowerx,upperx)

    ratio.SetTitle("")

    ratio.GetYaxis().SetLabelFont(axis_label_font)
    ratio.GetYaxis().SetLabelOffset(axis_label_offset)
    ratio.GetYaxis().SetTickLength(tick_length_ryaxis)
    ratio.GetYaxis().SetLabelSize(axis_label_size/sf_stack_ratio)
    ratio.GetXaxis().SetLabelFont(axis_label_font)
    ratio.GetXaxis().SetLabelOffset(axis_label_offset)
    ratio.GetXaxis().SetLabelSize(axis_label_size/sf_stack_ratio)
    ratio.GetXaxis().SetTickLength(tick_length_rxaxis)

    ratio.GetYaxis().SetTitle("data/MC")
    ratio.GetYaxis().SetTitleFont(axis_title_font)
    ratio.GetYaxis().SetTitleSize(axis_title_size)
    ratio.GetYaxis().SetTitleOffset(yaxis_title_offset)

    ratio.GetXaxis().SetTitle("discriminant value")
    ratio.GetXaxis().SetTitleFont(axis_title_font)
    ratio.GetXaxis().SetTitleSize(axis_title_size)
    ratio.GetXaxis().SetTitleOffset(xaxis_title_offset)
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetNdivisions(506)
    #ratio.GetYaxis().SetNdivisions( 503 )
    #ratio.GetXaxis().SetNdivisions( 510 )
    #ratio.GetXaxis().SetTickLength( line.GetXaxis().GetTickLength() * 2.0 )
    #ratio.GetYaxis().SetTickLength( line.GetYaxis().GetTickLength() * 1.65 )
    
    return ratio

def GetRatioErrorGraph(error_graph,templateHisto=None):
    if templateHisto==None:
      ratio_error_graph = error_graph.Clone()
    else:
      ratio_error_graph = ROOT.TGraphAsymmErrors(error_graph.GetN())
      ratio_error_graph.SetFillStyle(error_graph.GetFillStyle())
      ratio_error_graph.SetFillColor(error_graph.GetFillColor())
      ratio_error_graph.SetMarkerStyle(error_graph.GetMarkerStyle())
      ratio_error_graph.SetMarkerColor(error_graph.GetMarkerColor())
    if templateHisto!=None:
      for i in range(0,error_graph.GetN(),1):
          theCorrectXError=templateHisto.GetBinWidth(i+1)/2.0
          theCorrectXvalue=templateHisto.GetXaxis().GetBinCenter(i+1)
          #print theCorrectXvalue
          #print i, theCorrectXvalue, error_graph.GetY()[i],error_graph.GetErrorYhigh(i),error_graph.GetErrorYlow(i)
          ratio_error_graph.SetPoint(i,theCorrectXvalue,1),
          ratio_error_graph.SetPointEYhigh(i,error_graph.GetErrorYhigh(i)/error_graph.GetY()[i])
          ratio_error_graph.SetPointEYlow(i,error_graph.GetErrorYlow(i)/error_graph.GetY()[i])
          ratio_error_graph.SetPointEXhigh(i,theCorrectXError)
          ratio_error_graph.SetPointEXlow(i,theCorrectXError)
          #print i,i+0.5,1
          #print i,error_graph.GetErrorYhigh(i)/error_graph.GetY()[i]
          #print i,error_graph.GetErrorYlow(i)/error_graph.GetY()[i]
          #print i,theCorrectXError
          #print i,theCorrectXError
    else:    
      for i in range(0,error_graph.GetN(),1):
          ratio_error_graph.SetPoint(i,i+0.5,1)
          ratio_error_graph.SetPointEYhigh(i,error_graph.GetErrorYhigh(i)/error_graph.GetY()[i])
          ratio_error_graph.SetPointEYlow(i,error_graph.GetErrorYlow(i)/error_graph.GetY()[i])
    return ratio_error_graph
    

def SetUpStack(stack):
    stack.GetYaxis().SetLabelFont(axis_label_font)
    stack.GetYaxis().SetLabelOffset(axis_label_offset)
    stack.GetYaxis().SetLabelSize(axis_label_size)
    stack.GetYaxis().SetTickLength(tick_length_yaxis)
    stack.GetXaxis().SetTickLength(tick_length_xaxis)

    stack.GetYaxis().SetTitle("events")
    stack.GetYaxis().SetTitleOffset(yaxis_title_offset / sf_stack_ratio)
    stack.GetYaxis().SetTitleFont(axis_title_font)
    stack.GetYaxis().SetTitleSize(sf_stack_ratio * axis_title_size)

    stack.SetTitle("")

    return 0


# replace this with proper cms label function
def GetCMSandInfoLabels():
    posy = 1.-ROOT.gStyle.GetPadTopMargin()+0.03

    cms = ROOT.TPaveText(
        ROOT.gStyle.GetPadLeftMargin(),posy+0.02,
        1.-ROOT.gStyle.GetPadRightMargin(), 1.,
        "NDC"
    )
    cms.AddText("#scale[1.5]{#bf{CMS}}")
    cms.SetFillColor(0)
    cms.SetTextFont(43)
    cms.SetTextSize(26)
    cms.SetMargin(0.)
    cms.SetTextAlign(13)

    info = ROOT.TPaveText(
        0.7, posy,
        1.-ROOT.gStyle.GetPadRightMargin(), 1.,
        "NDC"
    )
    info.AddText("35.9 fb^{-1} (13 TeV)")
    info.SetFillColor(0)
    info.SetTextFont(43)
    info.SetTextSize(26)
    info.SetMargin(0.)
    info.SetTextAlign(33)

    return cms,info

def GetFitLabel(prepostfitflag):
    category=""
    if "prefit" in prepostfitflag:
        category = "pre-fit expectation"
    elif "fit_s" in prepostfitflag:
        category = "post-fit"
    else:
        category = "background-only post-fit"
    label = ROOT.TLatex(
        ROOT.gStyle.GetPadLeftMargin()+0.05,
        1.-ROOT.gStyle.GetPadTopMargin()-0.13,
        category
    )
    label.SetTextFont(42)
    label.SetTextSize(categoy_label_font_size)
    label.SetNDC()
    return label

def GetDiscriminantLabel(cat,prepostfitflag):
    if cat.find("tt")>0:
        return "DNN discriminant"

    help_array = cat.split("_")
    if "high" in help_array or "low" in help_array:
        return "MEM discriminant"

    return "BDT discriminant"

def GetCatLabel(cat,prepostfitflag):
    category = ""
    cat = cat.replace("ljets","SL")
    cat = cat.replace("mu","#mu")
    cat = cat.replace("ttH125","ttH")
    cat = cat.replace("ttJets","tt")
    dnn_node = ""
    if cat.find("tt")>0:
        #print ">>>>>>>>>>>>>>>> cat: ", cat
        dnn_node = cat[cat.find("tt"):]
        dnn_node += " node"
        dnn_node = dnn_node.replace("_","+")
        dnn_node = dnn_node.replace("ttH+bb","ttH")
        dnn_node = dnn_node.replace("tt","t#bar{t}")
    print dnn_node
    help_array = cat.split("_")
    print help_array
    jets = ""
    btags = ""
    jets_relation = ""
    btags_relation = ""
    bdt_cat = "" # no label in case of pure BDT
    if "high" in help_array:
        bdt_cat = "BDT-high"
    elif "low" in help_array:
        bdt_cat = "BDT-low"
    for part in help_array:
        for character in part:
            if character.isdigit():
                if "j" in part:
                    jets = character
                    if "ge" in part:
                        jets_relation = "#geq"
                    else:
                        jets_relation = ""
                elif ("t" in part or "b" in part) and not "v" in part and len(part)<5:
                    btags = character
                    if "ge" in part:
                        btags_relation = "#geq"
                    else:
                        btags_relation = ""
        if jets!="" and btags!="":
            break
    print jets_relation,jets
    print btags_relation,btags
    #special rules for desy cards
    if "dl_" in cat:
      help_array[0] = "DL"
      jets = ""
      btags = ""
      jets_relation = ""
      btags_relation = ""
      for part in help_array:
        if "j" in part and "t" in part: # now we have the jet-tag part. i hope
          subparts=part.split("j")
          subpart1=subparts[0]
          for character in subpart1:
            if character.isdigit():
              jets = character
            if "ge" in subpart1:
              jets_relation = "#geq"
            else:
              jets_relation = ""
          subpart2=subparts[1]
          for character in subpart2:
            if character.isdigit():
              btags = character
            if "ge" in subpart2:
              btags_relation = "#geq"
            else:
              btags_relation = ""
    cat = help_array[0]+" ("+jets_relation+jets+" jets, "+btags_relation+btags+" b-tags) "
    if dnn_node!="":
        cat+=dnn_node 
    else:
        cat+=bdt_cat
    #if "prefit" in prepostfitflag:
        #category = cat+", pre-fit"
    #elif "fit_s" in prepostfitflag:
        #category = cat+", post-fit s+b"
    #else:
        #category = cat+", post-fit b"
    category=cat
    label = ROOT.TLatex(
        ROOT.gStyle.GetPadLeftMargin()+0.05,
        1.-ROOT.gStyle.GetPadTopMargin()-0.08,
        category
    )
    label.SetTextFont(42)
    label.SetTextSize(categoy_label_font_size)
    label.SetNDC()
    return label


def GetPlots(categories_processes_histos_dict,category,prepostfitflag,templateHisto=None, blind=False,ymax=-1):
    
    # create legend
    #legend = GetLegend()
    legendL=getLegendL()
    legendR=getLegendR()
    
    # get dictionary process->histo dictionary for category
    processes_histos_dict = categories_processes_histos_dict[category]
    #print processes_histos_dict
    
    for process in processes_histos_dict:
      oldh=processes_histos_dict[process]
      processes_histos_dict[process]=rebinToTemplate(oldh,templateHisto)
    
    theTotalBackgroundHisto=processes_histos_dict["total_background"].Clone()
    for process in processes_histos_dict:
      oldh=processes_histos_dict[process]
      processes_histos_dict[process]=stripEmptyBins(oldh,theTotalBackgroundHisto)
    oldTemplate=templateHisto.Clone()
    templateHisto=stripEmptyBins(oldTemplate,theTotalBackgroundHisto)
    
    # fix data histo 
    olddata=processes_histos_dict["data"].Clone()
    processes_histos_dict["data"]=makeAsymErrorsForDataHisto(olddata)
    
    # Set data bin contents to zero if blinding is required
    if blind==True:
      olddata=processes_histos_dict["data"].Clone()
      processes_histos_dict["data"]=blindDataHisto(olddata,processes_histos_dict["total_signal"],processes_histos_dict["total_background"],SoBCut=0.01)

    # merge minor backgrounds
    MergeProcesses(processes_histos_dict,"wjets","zjets","vjets")
    MergeProcesses(processes_histos_dict,"ttbarW","ttbarZ","ttbarV")
    
    # set colors of histograms
    ColorizeHistograms(processes_histos_dict)
    
    # create stack
    stack = ROOT.THStack(category,category)
    
    # get total background or total signal+background prediction
    background = None
    if prepostfitflag=="shapes_fit_s":
        background = processes_histos_dict["total"]
        #print ">>>>> total ", background.GetMaximum()
    else:
        background = processes_histos_dict["total_background"]        
    signal = None
    if prepostfitflag=="shapes_prefit":
        signal,sf = GetSignal(processes_histos_dict,background.Integral())
    
    # get data histogram
    data = GetDataHistogram(processes_histos_dict)
     
   
    # sort histograms in cateogory depending on their integral (first with largest integral, last with smallest) -> to get smallest contributions in the stack plot on top of it
#    sorted_processes_histos_list = sorted(processes_histos_dict.items(),key=lambda x: x[1].Integral(),reverse=False)
    sorted_processes_histos_list = GetSortedProcesses(processes_histos_dict)
    #print "sorted_processes_histos_list: ", sorted_processes_histos_list

    procListForLegend=[] 
    
    # add background histogram to the stackplot
    for process in sorted_processes_histos_list:
        # avoid all total histograms, data and signal processes for background only
        if not "total" in process[0] and not "data" in process[0] and not "ttH" in process[0]:
            stack.Add(process[1])
            procListForLegend.append([process[1],latex_dict[process[0]],"f"])
    procListForLegend.reverse()

    # add signal histogram to the stack (in case of s+b fit)
    if prepostfitflag=="shapes_fit_s":
        for process in sorted_processes_histos_list:
            if process[0] == "total_signal":
                stack.Add(process[1])
                procListForLegend.insert(0,[process[1],latex_dict[process[0]],"f"])
    elif prepostfitflag=="shapes_fit_b":
        procListForLegend.insert(0,[None,"",""]) # add blank line
    elif prepostfitflag=="shapes_prefit" and signal!=None:
        procListForLegend.insert(0,[signal,str(sf)+"#times"+latex_dict["ttH"],"l"])
    if data!=None:
        procListForLegend.insert(0,[data,"data","p"])

    for ileg, leg in enumerate(procListForLegend):
      if ileg%2==0:
        legendL.AddEntry22(leg[0],leg[1],leg[2])
      else:
        legendR.AddEntry22(leg[0],leg[1],leg[2])

    #print ">>>>> stack ", stack.GetMaximum()

        
    # from total background or total background+signal prediction histogram in mlfit file, get the error band
    error_graph = GetErrorGraph(background)
    
    ratio_error_graph = GetRatioErrorGraph(error_graph,templateHisto)
    
    # everything should fit in the plots
    if ymax < 0:
        ymax = error_graph.GetHistogram().GetMaximum() * abs(ymax)
    stack.SetMaximum(ymax)
    stack.SetMinimum(0.9) # suppress showing 0 on y axis
    
    # calculate the ratio between background only or background+signal prediction and data
    ratio_background_data = None
    if data!=None:
        ratio_background_data = GetRatioGraph(data,background,templateHisto)

    
        
    return  stack,ymax,legendL,legendR,error_graph,data,ratio_background_data,signal,ratio_error_graph

def rebinToTemplate(histo,templateHisto=None):
  if templateHisto==None:
    return histo
  outhisto=templateHisto.Clone()
  outhisto.SetName(histo.GetName())
  outhisto.SetTitle(histo.GetTitle())
  nBins=templateHisto.GetNbinsX()
  for i in range(nBins):
    ibin=i+1
    outhisto.SetBinContent(ibin,histo.GetBinContent(ibin))
    outhisto.SetBinError(ibin,histo.GetBinError(ibin))
  return outhisto  

def stripEmptyBins(histo,template):
  firstFilledBin=0
  lastFilledBin=0
  nBinsTemplate=template.GetNbinsX()
  epsilonCutOff=0.00001
  for i in range(1,nBinsTemplate+1,1):
    if template.GetBinContent(i)>epsilonCutOff:
      firstFilledBin=i
      break
  for i in range(nBinsTemplate,0,-1):
    if template.GetBinContent(i)>epsilonCutOff:
      lastFilledBin=i
      break
  # get binEdgeArray  
  binEdgeArray=array("f",[])
  binContents=[]
  binErrors=[]
  for i in range(firstFilledBin,lastFilledBin+2,1):
    binEdgeArray.append(histo.GetBinLowEdge(i))
    binContents.append(histo.GetBinContent(i))
    binErrors.append(histo.GetBinError(i))
  # create new histo without empty bins at the ends                     
  newHisto=ROOT.TH1F(histo.GetName(),histo.GetTitle(),len(binEdgeArray)-1,binEdgeArray)
  newNBins=newHisto.GetNbinsX()
  for i in range(newNBins):
    newHisto.SetBinContent(i+1,binContents[i])
    newHisto.SetBinError(i+1,binErrors[i])
  return newHisto  

def Plot(fitfile_,ch_cat_dict_,prepostfitflag,blind=False,ymax=None):
    
    fitfile = ROOT.TFile.Open(fitfile_,"READ")
    
    dir_ = prepostfitflag
    
    categories_processes_histos_dict = GetHistos(fitfile,dir_)
    
    channels = GetChannels(GetDirectory(fitfile,dir_))

    # list of y-axis ranges
    ymax_per_channel = {}
    if ymax is None:
        for channel in channels:
            
            # depending on MVA method, decide which y-axis SF to use
            catname = ch_cat_dict_[channel]["catname"]
            if "low" in catname:
                ymaxsf = 1.1
            elif "high" in catname:
                ymaxsf = 2.5
            elif  "BDT" in catname:
                ymaxsf = 1.4
            else:
                ymaxsf = 8

            ymax_per_channel[channel] = -1. * ymaxsf

    else:
        ymax_per_channel = ymax
        
    for channel in channels:
    
        canvas = GetCanvas(dir_+channel)
        
        templateRootFilePath=ch_cat_dict_[channel]["histopath"]
        #print templateRootFilePath
        templateHistoExpression=ch_cat_dict_[channel]["histoexpression"]
        #print templateRootFilePath,templateHistoExpression
        templateHisto=None
        if templateRootFilePath!="" and templateHistoExpression!="":
          #print templateRootFilePath
          #print templateHistoExpression.replace("$PROCESS","ttH_hbb")
          templateRootFile=ROOT.TFile(templateRootFilePath,"READ")
          templateHisto=templateRootFile.Get(templateHistoExpression.replace("$PROCESS","ttH_hbb"))

          stack,ymax_this_channel,legendL,legendR,error_band,data,ratio_data_prediction,signal,ratio_error_band = GetPlots(categories_processes_histos_dict,channel,dir_,templateHisto,blind,ymax_per_channel[channel])

        # if y-axis range has not been provided, fill dict to return  
        if ymax_per_channel[channel] < 0:
            ymax_per_channel[channel] = ymax_this_channel
        
        canvas.cd(1)
        
        stack.Draw("hist")
        # unfortunately this has to be done after a first Draw() because only then the axis objects are created ... ROOT ...

        SetUpStack(stack)
        
        stack.Draw("hist")
        
        if data!=None:
            data.Draw("histPEX0same")
        
        if signal!=None:
            signal.Draw("histsame")
        
        error_band.Draw("2same")

        ROOT.gPad.RedrawAxis()
        
        legendL.Draw("same")
        legendR.Draw("same")
               
        catlabel = GetCatLabel(ch_cat_dict_[channel]["catname"],prepostfitflag)
        catlabel.Draw("same")
        fitlabel = GetFitLabel(prepostfitflag)
        fitlabel.Draw("same")

        discriminantLabel = GetDiscriminantLabel(ch_cat_dict_[channel]["catname"],prepostfitflag)
        if "DNN" in discriminantLabel:
            ROOT.gPad.SetLogy()
        
        canvas.cd(2)
        #ratio_background_data.GetXaxis().SetRange(1,background_tot.GetMinimumBin()-1)
        if ratio_data_prediction!=None:
            ratio_data_prediction.GetXaxis().SetTitle(discriminantLabel)
            ratio_data_prediction.Draw("AP2")

        linemin = ratio_error_band.GetX()[0] - ratio_error_band.GetEXlow()[0]
        linemax = ratio_error_band.GetX()[ratio_error_band.GetN()-1] + ratio_error_band.GetEXhigh()[ratio_error_band.GetN()-1]
        ratio_line = ROOT.TLine(linemin,1,linemax,1)
        ratio_line.SetNDC(False)
        ratio_line.SetLineStyle(2)
        ratio_line.Draw("same")
        ratio_error_band.Draw("2same")
        
        canvas.cd(1)
        cms,info = GetCMSandInfoLabels()
        cms.Draw("same")
        info.Draw("same")
        
        # did not get this to display nicely
        #canvas.cd(0)
        ##draw the lumi text on the canvas from this other python module
        #CMS_lumi.lumi_13TeV = "35.9 fb^{-1}"
        #CMS_lumi.writeExtraText = 1
        ##CMS_lumi.extraText = "Preliminary"
        #CMS_lumi.extraText = ""
        #CMS_lumi.cmsText="CMS"
        #CMS_lumi.lumi_sqrtS = "13 TeV" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
        #CMS_lumi.cmsTextSize = 0.55
        #CMS_lumi.cmsTextOffset = 0.01
        #CMS_lumi.lumiTextSize = 0.43
        #CMS_lumi.lumiTextOffset = 0.61
        #CMS_lumi.relPosX = 0.15
        #CMS_lumi.hOffset = 0.000001
        #iPeriod=4   # 13TeV
        #iPos=0     # CMS inside frame
        #CMS_lumi.CMS_lumi(canvas, iPeriod, iPos)
        
        
        canvas.Print(dir_+"_"+ch_cat_dict_[channel]["catname"]+".pdf")
        canvas.Print(dir_+"_"+ch_cat_dict_[channel]["catname"]+".png")
        templateRootFile.Close()
    
    fitfile.Close()
    
    return ymax_per_channel
    


def ReadDatacard(datacard):
    print "reading datacard"
    buzzwords_in_relevant_lines = []
    shapeLines=[]
    categoryLine=""
    channel_category_dict = {}
    foundCategoryLine=False
    with open(datacard, "r") as ins:
        for line in ins:
            formattedLine=line
            # remove uneeded separators from line
            while "\t" in line or "  " in line or "\n" in line :
              line=line.replace("\t"," ").replace("  "," ").replace("\n","")
            if "shapes *" in line.replace("\t"," "):
              shapeLines.append(line)
            if "bin " in line and foundCategoryLine==False:
              foundCategoryLine=True
              categoryLine=line
    categoriesFromLine=categoryLine.split(" ")[1:]
    print categoriesFromLine
    print shapeLines
    for cfl in categoriesFromLine:
      channel = cfl
      category = ""
      histopath= ""
      histoexpression = ""
      for line in shapeLines:
        splitline=line.split(" ")
        pref=splitline[0]
        shapeproc=splitline[1] #disregared for now
        shapeChannel=splitline[2]
        shapeFile=splitline[3]
        shapeProcessPart=splitline[4]
        shapeSysPart=splitline[5]
        if shapeproc!="*" :
          continue
        if not (shapeChannel==channel or shapeChannel=="*"):
          continue
        histopath=shapeFile
        if "$CHANNEL" in shapeProcessPart:
          # This is needed for unanonymized kit cards
          shapeProcessPart.replace("$CHANNEL",channel)
        category=shapeProcessPart.replace("$PROCESS","").replace("/","").replace("_finaldiscr_","")
        histoexpression=shapeProcessPart
      channel_category_dict[channel]={}
      channel_category_dict[channel]["catname"] = category
      channel_category_dict[channel]["histopath"] = histopath
      channel_category_dict[channel]["histoexpression"] = histoexpression  
    
    print channel_category_dict
    return channel_category_dict
          
################################################################################# main function #################################################################################

def main(fitfile_,datacard_):
    
    #print datacard_
    ch_cat_dict = ReadDatacard(datacard_)
    print ">>>>>>>>>>>>>>>>> ", ch_cat_dict

    SetPadMargins()

    
    # plot prefit
    maxy = Plot(fitfile_,ch_cat_dict,"shapes_prefit",blind=False)
    
    # plot post fit after s+b fit
    Plot(fitfile_,ch_cat_dict,"shapes_fit_s",blind=False,ymax=maxy)

    # plot post fit after b-only fit
    Plot(fitfile_,ch_cat_dict,"shapes_fit_b",blind=False,ymax=maxy)


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2])
        

# usage: python PrePostFitPlots.py mlfitfile.root corresponding_datacard.txt
