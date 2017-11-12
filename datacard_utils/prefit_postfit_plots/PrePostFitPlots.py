import ROOT
import sys
import os
import CMS_lumi
import re
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
color_dict["ttbarW"]=ROOT.kBlue-10
color_dict["ttbarZ"]=ROOT.kBlue-6
color_dict["diboson"]=ROOT.kAzure+2
color_dict["QCD"]=ROOT.kYellow
color_dict["ttH_hbb"]=ROOT.kBlue+1
color_dict["ttH_hcc"]=ROOT.kBlue+1
color_dict["ttH_htt"]=ROOT.kBlue+1
color_dict["ttH_hgg"]=ROOT.kBlue+1
color_dict["ttH_hgluglu"]=ROOT.kBlue+1
color_dict["ttH_hww"]=ROOT.kBlue+1
color_dict["ttH_hzz"]=ROOT.kBlue+1
color_dict["ttH_hzg"]=ROOT.kBlue+1
color_dict["ttH"]=ROOT.kBlue+1
color_dict["total_background"]=ROOT.kBlack
color_dict["total_signal"]=ROOT.kBlack
color_dict["total_covar"]=ROOT.kBlack
color_dict["total"]=ROOT.kBlack
color_dict["data"]=ROOT.kBlack

latex_dict = {}
latex_dict["ttbarOther"]="t#bar{t}+lf"
latex_dict["ttbarPlusCCbar"]="t#bar{t}+c#bar{c}"
latex_dict["ttbarPlusB"]="t#bar{t}+b"
latex_dict["ttbarPlus2B"]="t#bar{t}+2b"
latex_dict["ttbarPlusBBbar"]="t#bar{t}+b#bar{b}"
latex_dict["singlet"]="Single Top"
latex_dict["zjets"]="Z+jets"
latex_dict["wjets"]="W+jets"
latex_dict["ttbarW"]="t#bar{t}W"
latex_dict["ttbarZ"]="t#bar{t}Z"
latex_dict["diboson"]="Diboson"
latex_dict["QCD"]="QCD"
latex_dict["ttH_hbb"]="t#bar{t}H"
latex_dict["ttH_hcc"]="t#bar{t}H"
latex_dict["ttH_htt"]="t#bar{t}H"
latex_dict["ttH_hgg"]="t#bar{t}H"
latex_dict["ttH_hgluglu"]="t#bar{t}H"
latex_dict["ttH_hww"]="t#bar{t}H"
latex_dict["ttH_hzz"]="t#bar{t}H"
latex_dict["ttH_hzg"]="t#bar{t}H"
latex_dict["ttH"]="t#bar{t}H"
latex_dict["total_background"]="Total background"
latex_dict["total_signal"]="Total signal"
latex_dict["total_covar"]="bla"
latex_dict["total"]="Total s+b"
latex_dict["data"]="data"

def ColorizeHistograms(processes_histos_dict):
    for process in processes_histos_dict:
        processes_histos_dict[process].SetLineColor(ROOT.kBlack)
        processes_histos_dict[process].SetFillColor(color_dict[process])
    return 0

def GetCanvas(canvas_name):
    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas(canvas_name,"",900,800)
    c.Divide(1,2);
    c.GetPad(1).SetPad(0.05,0.3,0.95,1);
    c.GetPad(1).SetLeftMargin(0.1);
    c.GetPad(1).SetRightMargin(0.05);
    c.GetPad(1).SetBottomMargin(0);
    c.GetPad(2).SetPad(0.05,0.0,0.95,0.3);
    c.GetPad(2).SetRightMargin(0.05);
    c.GetPad(2).SetLeftMargin(0.1);
    c.GetPad(2).SetTopMargin(0);
    c.GetPad(2).SetBottomMargin(0.2)
    c.cd();
    return c

# returns directory in tfile***    
def GetDirectory(fitfile,directory):
    dir_ = fitfile.Get(directory)
    return dir_

#returns a list of all channels in the given directory***
def GetChannels(directory):
    channels = []
    for key in directory.GetListOfKeys():
        if "ch" in key.GetName():
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
    signal = processes_histos_dict["total_signal"]
    signal.SetLineColor(ROOT.kBlue+1)
    signal.SetFillStyle(0)
    signal.SetLineWidth(2)
    signal_integral = signal.Integral()
    #print signal_integral
    if signal_integral>0.:
        signal.Scale(background_integral/signal_integral)
        return signal,background_integral/signal_integral
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
    legend.SetX1NDC(0.63)
    legend.SetX2NDC(0.79)
    legend.SetY1NDC(0.88)
    legend.SetY2NDC(0.89)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.03);
    legend.SetFillStyle(0);
    return legend

def getLegendR():
    legend=ROOT.TLegend()
    legend.SetX1NDC(0.79)
    legend.SetX2NDC(0.96)
    legend.SetY1NDC(0.88)
    legend.SetY2NDC(0.89)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    legend.SetTextSize(0.03);
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

def GetRatioHisto(nominator,denominator,templateHisto=None):
    ratio = ROOT.TGraphAsymmErrors(nominator.GetNbinsX())
    lowerx=0
    upperx=nominator.GetNbinsX()
    #print "ratio"
    #templateHisto=None
    if templateHisto!=None:
      lowerx=templateHisto.GetBinLowEdge(1)
      upperx=templateHisto.GetBinLowEdge(nominator.GetNbinsX())+templateHisto.GetBinWidth(nominator.GetNbinsX())
      for i in range(1,nominator.GetNbinsX()+1,1):
        theCorrectXvalue=templateHisto.GetXaxis().GetBinCenter(i)
        #print theCorrectXvalue
        ratio.SetPoint(i-1,theCorrectXvalue,nominator.GetBinContent(i)/denominator.GetBinContent(i))
        ratio.SetPointError(i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i))
        #print i-1,theCorrectXvalue,nominator.GetBinContent(i)/denominator.GetBinContent(i)
        #print i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i)
    else:    
      for i in range(1,nominator.GetNbinsX()+1,1):
          ratio.SetPoint(i-1,i-1+0.5,nominator.GetBinContent(i)/denominator.GetBinContent(i))
          ratio.SetPointError(i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i))
          #print i-1,i-1+0.5,nominator.GetBinContent(i)/denominator.GetBinContent(i)
          #print i-1,0.,0.,(nominator.GetBinErrorLow(i))/denominator.GetBinContent(i),(nominator.GetBinErrorUp(i))/denominator.GetBinContent(i)
    ratio.SetMarkerStyle(20)
    ratio.GetYaxis().SetRangeUser(0.00,1.99)
    ratio.GetXaxis().SetLimits(lowerx,upperx)
    ratio.SetTitle("")
    ratio.GetYaxis().SetLabelFont(43)
    ratio.GetYaxis().SetLabelSize(18)
    ratio.GetXaxis().SetLabelFont(43)
    ratio.GetXaxis().SetLabelSize(18)
    ratio.GetYaxis().SetTitle("data/MC")
    ratio.GetYaxis().SetTitleOffset(2.0)
    ratio.GetYaxis().SetTitleFont(43)
    ratio.GetYaxis().SetTitleSize(22)
    ratio.GetXaxis().SetTitle("discriminant value")
    ratio.GetXaxis().SetTitleOffset(3.0)
    ratio.GetXaxis().SetTitleFont(43)
    ratio.GetXaxis().SetTitleSize(22)
    ratio.GetYaxis().CenterTitle()
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
          ratio_error_graph.SetPoint(i,theCorrectXvalue,1)
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
    stack.GetYaxis().SetLabelFont(43)
    stack.GetYaxis().SetLabelSize(18)
    stack.GetYaxis().SetTitle("Events")
    stack.GetYaxis().SetTitleOffset(2.0)
    stack.GetYaxis().SetTitleFont(43)
    stack.GetYaxis().SetTitleSize(22)
    stack.SetTitle("")
    return 0


# replace this with proper cms label function
def GetCMSandInfoLabels():
    cms = ROOT.TLatex(0.12, 0.92, '#scale[1.5]{#bf{CMS}}'  );# add this for preliminary #it{Preliminary}
    cms.SetTextFont(43)
    cms.SetTextSize(22)
    cms.SetNDC()
    info = ROOT.TLatex(0.7, 0.92, '35.9 fb^{-1} (13 TeV)'  );
    info.SetTextFont(43)
    info.SetTextSize(22)
    info.SetNDC()
    return cms,info

def GetFitLabel(prepostfitflag):
    category=""
    if "prefit" in prepostfitflag:
        category = "pre-fit expectation"
    elif "fit_s" in prepostfitflag:
        category = "post-fit s+b"
    else:
        category = "post-fit b"
    label = ROOT.TLatex(0.15, 0.8, category  );
    label.SetTextFont(42)
    label.SetTextSize(0.035)
    label.SetNDC()
    return label

def GetCatLabel(cat,prepostfitflag):
    category = ""
    #cat = cat.replace("_"," ")
    cat = cat.replace("ljets","l+jets")
    cat = cat.replace("mu","#mu")
    cat = cat.replace("ttH125","ttH")
    cat = cat.replace("ttJets","tt")
    dnn_node = ""
    if cat.find("tt")>0:
        dnn_node = cat[cat.find("tt"):]
        dnn_node += " DNN-node"
        dnn_node = dnn_node.replace("_","+")
        dnn_node = dnn_node.replace("ttH+bb","ttH")
    print dnn_node
    help_array = cat.split("_")
    print help_array
    jets = ""
    btags = ""
    jets_relation = ""
    btags_relation = ""
    bdt_cat = "BDT"
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
                        jets_relation = "="
                elif ("t" in part or "b" in part) and not "v" in part and len(part)<5:
                    btags = character
                    if "ge" in part:
                        btags_relation = "#geq"
                    else:
                        btags_relation = "="
        if jets!="" and btags!="":
            break
    print jets_relation,jets
    print btags_relation,btags
    cat = help_array[0]+", #jets "+jets_relation+" "+jets+", #btags "+btags_relation+" "+btags+", "
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
    label = ROOT.TLatex(0.15, 0.85, category  );
    label.SetTextFont(42)
    label.SetTextSize(0.035)
    label.SetNDC()
    return label


def GetPlots(categories_processes_histos_dict,category,prepostfitflag,templateHisto=None):
    # create legend
    #legend = GetLegend()
    legendL=getLegendL()
    legendR=getLegendR()
    
    # get dictionary process->histo dictionary for category
    processes_histos_dict = categories_processes_histos_dict[category]
    #print processes_histos_dict
    
    # set colors of histograms
    ColorizeHistograms(processes_histos_dict)
    
    # create stack
    stack = ROOT.THStack(category,category)
    
    # get total background or total signal+background prediction
    background = None
    if prepostfitflag=="shapes_fit_s":
        background = processes_histos_dict["total"]
    else:
        background = processes_histos_dict["total_background"]
        
    signal,sf = GetSignal(processes_histos_dict,background.Integral())
    
    # get data histogram
    data = GetDataHistogram(processes_histos_dict)
     
    procListForLegend=[] 
    if data!=None:
        procListForLegend.append([data,"Asimov s+b","p"])
        
    if signal!=None:
        procListForLegend.append([signal,latex_dict["ttH"]+" #times "+str(round(sf,1)),"l"])
    
    # sort histograms in cateogory depending on their integral (first with largest integral, last with smallest) -> to get smallest contributions in the stack plot on top of it
    sorted_processes_histos_list = sorted(processes_histos_dict.items(),key=lambda x: x[1].Integral(),reverse=False)
    #print sorted_processes_histos_list
    
    # add background histogram to the stackplot
    n_ttH = 0
    for process in sorted_processes_histos_list:
        # avoid all total histograms and data for background+signal
        if prepostfitflag=="shapes_fit_s":
            if not "total" in process[0] and not "data" in process[0]:
                stack.Add(process[1])
                if "ttH" in process[0]:
                    if n_ttH<1:
                        procListForLegend.append([process[1],latex_dict[process[0]],"f"])
                        n_ttH+=1
                else:
                    procListForLegend.append([process[1],latex_dict[process[0]],"f"])
        # avoid all total histograms, data and signal processes for background only
        else:
            if not "total" in process[0] and not "data" in process[0] and not "ttH" in process[0]:
                stack.Add(process[1])
                procListForLegend.append([process[1],latex_dict[process[0]],"f"])

    for ileg, leg in enumerate(procListForLegend):
      if ileg%2==0:
        legendL.AddEntry22(leg[0],leg[1],leg[2])
      else:
        legendR.AddEntry22(leg[0],leg[1],leg[2])
    
    # from total background or total background+signal prediction histogram in mlfit file, get the error band
    error_graph = GetErrorGraph(background)
    
    ratio_error_graph = GetRatioErrorGraph(error_graph,templateHisto)
    
    # everything should fit in the plots 
    stack.SetMaximum(error_graph.GetHistogram().GetMaximum()*1.1)
    
    # calculate the ratio between background only or background+signal prediction and data
    ratio_background_data = None
    if data!=None:
        ratio_background_data = GetRatioHisto(data,background,templateHisto)
    
    return  stack,legendL,legendR,error_graph,data,ratio_background_data,signal,ratio_error_graph


def Plot(fitfile_,ch_cat_dict_,prepostfitflag):
    
    fitfile = ROOT.TFile.Open(fitfile_,"READ")
    
    dir_ = prepostfitflag
    
    categories_processes_histos_dict = GetHistos(fitfile,dir_)
    
    channels = GetChannels(GetDirectory(fitfile,dir_))
    
    for channel in channels:
    
        canvas = GetCanvas(dir_+channel)
        
        templateRootFilePath=ch_cat_dict_[channel]["histopath"]
        templateHistoExpression=ch_cat_dict_[channel]["histoexpression"]
        print templateRootFilePath,templateHistoExpression
        templateHisto=None
        if templateRootFilePath!="" and templateHistoExpression!="":
          print templateRootFilePath
          print templateHistoExpression.replace("$PROCESS","ttH_hbb")
          templateRootFile=ROOT.TFile(templateRootFilePath,"READ")
          templateHisto=templateRootFile.Get(templateHistoExpression.replace("$PROCESS","ttH_hbb"))
        stack,legendL,legendR,error_band,data,ratio_data_prediction,signal,ratio_error_band = GetPlots(categories_processes_histos_dict,channel,dir_,templateHisto)
        
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
        
        legendL.Draw("same")
        legendR.Draw("same")
        
        
        
        catlabel = GetCatLabel(ch_cat_dict_[channel]["catname"],prepostfitflag)
        catlabel.Draw("same")
        fitlabel = GetFitLabel(prepostfitflag)
        fitlabel.Draw("same")
        
        canvas.cd(2)
        #ratio_background_data.GetXaxis().SetRange(1,background_tot.GetMinimumBin()-1)
        if ratio_data_prediction!=None:
            ratio_data_prediction.Draw("AP2")
            linemin=0
            linemax=ratio_data_prediction.GetN()
            if templateHisto!=None:
              linemin=templateHisto.GetBinLowEdge(1)
              linemax=templateHisto.GetBinLowEdge(stack.GetXaxis().GetNbins())+templateHisto.GetBinWidth(stack.GetXaxis().GetNbins())
              print linemin, linemax
            ratio_line = ROOT.TLine(linemin,1,linemax,1)
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
    
    return 0
    


def ReadDatacard(datacard):
    print "reading datacard"
    buzzwords_in_relevant_lines = []
    with open(datacard, "r") as ins:
        for line in ins:
            if "shapes *" in line:
                line_array = line.split(' ')
                modified_line_array = []
                for element in line_array:
                    if not element=='' and not element=='*' and not "$SYSTEMATIC" in element and ("ch" in element or "$PROCESS" in element or ".root" in element):
                        modified_line_array.append(element)
                buzzwords_in_relevant_lines.append(modified_line_array)
    print "buzzwords in line ", buzzwords_in_relevant_lines
    channel_category_dict = {}
    for relevant_line in buzzwords_in_relevant_lines:
        channel = ""
        category = ""
        histopath= ""
        histoexpression = ""
        for buzzword in relevant_line:
            if "ch" in buzzword:
                channel = buzzword
            if "$PROCESS" in buzzword:
                category = buzzword.replace("$PROCESS","").replace("/","").replace("_finaldiscr_","")
            if "$PROCESS" in buzzword:
                histoexpression = buzzword
            if ".root" in buzzword:
                histopath = buzzword                
        
        channel_category_dict[channel]={}
        channel_category_dict[channel]["catname"] = category
        channel_category_dict[channel]["histopath"] = histopath
        channel_category_dict[channel]["histoexpression"] = histoexpression
        
    print channel_category_dict
    #channel_category_dict = {}
    return channel_category_dict
    
    #print mod_array
################################################################################# main function #################################################################################

def main(fitfile_,datacard_):
    
    print datacard_
    ch_cat_dict = ReadDatacard(datacard_)
    
    # plot prefit
    Plot(fitfile_,ch_cat_dict,"shapes_prefit")
    
    # plot post fit after s+b fit
    Plot(fitfile_,ch_cat_dict,"shapes_fit_s")

    # plot post fit after b-only fit
    Plot(fitfile_,ch_cat_dict,"shapes_fit_b")


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2])
        

# usage: python PrePostFitPlots.py mlfitfile.root corresponding_datacard.txt
