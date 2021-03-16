import os
import sys
from optparse import OptionParser
import ROOT
from math import ceil
from math import floor
import json
ROOT.gROOT.SetBatch(1)
verbosity = 0
vars_44 = [
    "memDBp",
    "Reco_JABDT_ttbar_Jet_CSV_whaddau2",
    "Evt_Deta_JetsAverage",
    "Reco_JABDT_ttbar_Jet_CSV_whaddau1",
    "Evt_CSV_avg_tagged",
    "Reco_JABDT_tHW_Jet_CSV_whaddau1",
    "Reco_JABDT_tHq_abs_ljet_eta",
    "Evt_M_JetsAverage",
    "Evt_M_minDrLepTag",
    "Reco_JABDT_ttH_Jet_CSV_hdau2",
    "Reco_ttH_toplep_m",
    "Evt_CSV_avg",
    "Reco_JABDT_tHW_energy_fraction",
    "Reco_ttH_bestJABDToutput",
    "Reco_ttbar_toplep_m",
    "Reco_tHq_bestJABDToutput",
    "Evt_Pt_JetsAverage",
    "Reco_tHW_bestJABDToutput",
    "Reco_JABDT_tHW_Jet_CSV_btop",
    "Reco_ttbar_bestJABDToutput",
    "Evt_M_TaggedJetsAverage",
    "N_Jets",
    "CSV_2",
    "Reco_JABDT_tHq_Jet_CSV_hdau1",
    "Evt_Deta_TaggedJetsAverage",
    "Evt_Pt_minDrTaggedJets",
    "Evt_blr_transformed",   
]

vars_34 = [
    "Evt_Deta_JetsAverage",
    "Reco_JABDT_ttbar_Jet_CSV_whaddau1",
    "Evt_CSV_avg_tagged",
    "Reco_JABDT_tHW_Jet_CSV_whaddau1",
    "Reco_JABDT_ttbar_Jet_CSV_btophad",
    "Reco_JABDT_ttbar_Jet_CSV_btoplep",
    "Evt_M_JetsAverage",
    "Evt_HT_tags",
    "Reco_ttbar_whad_m",
    "Reco_JABDT_ttH_Jet_CSV_btoplep",
    "Evt_CSV_avg",
    "Evt_M_Total",
    "Reco_ttH_bestJABDToutput",
    "Reco_ttbar_toplep_m",
    "Reco_tHq_bestJABDToutput",
    "Evt_CSV_dev",
    "Reco_tHW_bestJABDToutput",
    "Reco_JABDT_tHW_Jet_CSV_btop",
    "Reco_ttbar_bestJABDToutput",
    "Evt_M_TaggedJetsAverage",
    "Reco_tHW_whad_dr",
    "N_Jets",
    "Evt_JetPt_over_JetE",
    "Evt_Deta_TaggedJetsAverage",
    "Evt_Pt_minDrTaggedJets",
    "Reco_JABDT_tHW_log_wb_m",
    "Evt_h1",
    "Evt_blr_transformed",  
]

def getChannels(cat = "ge4j_ge4t"):
    channels = []
    if cat == "ge4j_ge4t":
        varlist = vars_44
    elif cat == "ge4j_3t":
        varlist = vars_34

    for i, var1 in enumerate(varlist):
        for var2 in varlist[i+1:]:
            channels.append("ljets_{cat}_{var2}_ljets_{cat}_{var1}".format(cat=cat, var1=var1, var2=var2))
    
    for i, var2 in enumerate(varlist):
        for var1 in varlist[i+1:]:
            channels.append("ljets_{cat}_{var2}_ljets_{cat}_{var1}".format(cat=cat, var1=var1, var2=var2))
    return channels



def split_comma_list(tosplit):
    returnlist = []
    print("Input to split:")
    print(tosplit)
    for c in tosplit:
        returnlist += c.split(",")
    return returnlist

def rebin_histo(h, division_factor = 2):
    bins_x = h.GetNbinsX()
    bins_y = h.GetNbinsY()
    # new_bins_x = int(ceil(bins_x/float(division_factor)))
    # new_bins_y = int(ceil(bins_y/float(division_factor)))
    new_bins_x = int(floor(bins_x/float(division_factor)))
    new_bins_y = int(floor(bins_y/float(division_factor)))

    x_min = h.GetXaxis().GetBinLowEdge(1)
    x_max = h.GetXaxis().GetBinUpEdge(bins_x)

    y_min = h.GetYaxis().GetBinLowEdge(1)
    y_max = h.GetYaxis().GetBinUpEdge(bins_y)
    print("Dividing by {}".format(division_factor))
    print ("Creating new histogram with n_x = %s, n_y = %s" % (str(new_bins_x), str(new_bins_y)))
    new_h = ROOT.TH2D("rebinned_" + h.GetName(), h.GetTitle(), new_bins_x, x_min, x_max, new_bins_y, y_min, y_max)

    xProblem = False
    yProblem = False
    xMod =  bins_x % division_factor
    yMod =  bins_y % division_factor
    if xMod != 0:
        xProblem = True
    if yMod != 0:
        yProblem = True
    print(xProblem,yProblem)

    for x in range(1, bins_x+1, division_factor):
        for y in range(1, bins_y+1, division_factor):
            content = 0
            error = 0
            xOffset = 0
            yOffset = 0
            for i in range(0, division_factor):
                for j in range(0, division_factor):
                    if not (yProblem and y == bins_y-yMod+1) and not (xProblem and x == bins_x-xMod+1):
                        if  verbosity > 0:
                            print ("\tadding from ({0}, {1}) value {2}, {3}".format(x+i, y+j, h.GetBinContent(x+i, y+j), (h.GetBinError(x+i, y+j))**2))
                        content += h.GetBinContent(x+i, y+j)
                        error += (h.GetBinError(x+i, y+j))**2

                if xProblem and x == bins_x-xMod+1 and y != bins_y-yMod+1:
                # if xProblem and x == bins_x and y != bins_y:
                    xOffset = -1*(bins_x % division_factor)
                    content += h.GetBinContent(x, y+i)
                    error += (h.GetBinContent(x, y+i))**2 

                if yProblem and y == bins_y-yMod+1 and x != bins_x-xMod+1:
                    yOffset = -1*(bins_y % division_factor)
                    content += h.GetBinContent(x+i, y)
                    error += (h.GetBinContent(x+i, y))**2 

                if xProblem and yProblem and x == bins_x-xMod+1 and y == bins_y-yMod+1:
                    xOffset = -1*(bins_x % division_factor)
                    yOffset = -1*(bins_y % division_factor)
                    content += h.GetBinContent(x+i, y+i)
                    error += (h.GetBinContent(x+i, y+i))**2 

            new_x = int(ceil(x/float(division_factor)))+xOffset
            new_y = int(ceil(y/float(division_factor)))+yOffset
            # new_x = int(floor(x/float(division_factor)))+xOffset
            # new_y = int(floor(y/float(division_factor)))+yOffset
            # print(new_x,new_y)
            if not (yProblem and y == bins_y) and not (xProblem and x == bins_x):
                new_h.SetBinContent(new_x, new_y, content)
                new_h.SetBinError(new_x, new_y, error**(1./2))

            elif (yProblem and y == bins_y and x != bins_x):
                new_h.SetBinContent(new_x, new_y-1, new_h.GetBinContent(new_x, new_y-1)+ content)
                new_h.SetBinError(new_x, new_y-1, (new_h.GetBinError(new_x, new_y-1)**2 + error**2)**(1./2))

            elif (xProblem and x == bins_x and y != bins_y):
                new_h.SetBinContent(new_x-1, new_y, new_h.GetBinContent(new_x-1, new_y) + content)
                new_h.SetBinError(new_x, new_y-1, (new_h.GetBinError(new_x-1, new_y)**2 + error**2)**(1./2))

            elif (xProblem and yProblem and x == bins_x and y == bins_y):
                new_h.SetBinContent(new_x, new_y, new_h.GetBinContent(new_x, new_y) + content)
                new_h.SetBinError(new_x, new_y, (new_h.GetBinError(new_x, new_y)**2 + error**2)**(1./2))
    print(new_h.Integral())
    return new_h

def addOverflows(h):
    nBinsX = h.GetNbinsX()
    nBinsY = h.GetNbinsY()

    for y in range(0,nBinsY+2):
        h.SetBinContent(1, y , h.GetBinContent(0,y)+h.GetBinContent(1,y))
        h.SetBinContent(0, y , 0)
        h.SetBinContent(nBinsX, y ,h.GetBinContent(nBinsX+1,y)+h.GetBinContent(nBinsX,y))
        h.SetBinContent(nBinsX+1, y, 0)
    
    for x in range(1,nBinsX+1):
        h.SetBinContent(x, 1 , h.GetBinContent(x,0)+h.GetBinContent(x,1))
        h.SetBinContent(x, 0 , 0)
        h.SetBinContent(x, nBinsY , h.GetBinContent(x, nBinsY+1)+h.GetBinContent(x,nBinsY))
        h.SetBinContent(x, nBinsY+1, 0)
    return h


def findMinBinPopulation(histogram):
    nbinsX = histogram.GetNbinsX()
    nbinsY = histogram.GetNbinsY()
    minimum = 9999999999
    xmin = 0
    ymin = 0
    for i in range(1,nbinsX+1):
        for j in range(1,nbinsY+1):
            if i==0 or j == 0: continue
            # globalBin = histogram.GetBin(i,j)
            content = histogram.GetBinContent(i,j)
            if content < 0: continue
            if content < minimum:
                minimum = content
                xmin = i
                ymin = j
    print("Found Bin with fewest entries ({entries}) at (x,y): ({x},{y})".format(entries = minimum, x = xmin, y = ymin))

    return minimum, i, j

def findBiggestError(histogram):
    nbinsX = histogram.GetNbinsX()
    nbinsY = histogram.GetNbinsY()
    maximum = 0
    x = 0
    y = 0
    for i in range(nbinsX+1):
        for j in range(nbinsY+1):
            if i==0 or j == 0: continue
            # globalBin = histogram.GetBin(i,j)
            content = histogram.GetBinContent(i,j)
            error = histogram.GetBinError(i,j)
            if content <= 0: continue
            ratio = error/content
            if ratio > maximum:
                maximum = ratio
                x = i
                y = j
    print("Found Bin with largest rel. error ({entries}) at (x,y): ({x},{y})".format(entries = ratio, x = x, y = y))

    return ratio, i, j


def doRebinning(rootfile, histolist, threshold, channel):
    combinedHist = None
    c = ROOT.TCanvas()
    c.cd()
    ROOT.gStyle.SetOptStat(2110111)
    ROOT.gPad.SetLogz()
    dic = {}
    # loop over hists and add them to a combined histogram
    for h in histolist:
        h_tmp = rootfile.Get(str(h))
        if not isinstance(h_tmp, ROOT.TH2):
            print("Rebinning 2D histogram!")
            isTwoD = True
        elif combinedHist is None:
            combinedHist = h_tmp.Clone("combinedHist")
            # combinedHist.Reset()
        elif isinstance(combinedHist, ROOT.TH1):
            combinedHist.Add(h_tmp)
        # if combinedHist:
            # print("AFTER ADDING")
            # print(combinedHist.Integral())
            # combinedHist.Print("range")
    if combinedHist is None:
        print("ERROR: could not add any histograms!")
        return []
    
    combinedHist.Draw("colz")
    if not os.path.exists("rebinnedPlots"):
        os.makedirs("rebinnedPlots")
    c.SaveAs("rebinnedPlots/before_"+channel+".png")
    nbinsX = combinedHist.GetNbinsX()
    nbinsY = combinedHist.GetNbinsY()
    print("Starting with {x},{y} bins with integral {integral}".format(x = nbinsX, y = nbinsY, integral = combinedHist.Integral()))
    print("before dim: {0},{1}".format(nbinsX, nbinsY))
    minPop, minX, minY = findMinBinPopulation(combinedHist)
    # minPop, minX, minY = findBiggestError(combinedHist)
    dic["nBinsX_before"] = nbinsX
    dic["nBinsY_before"] = nbinsY
    dic["MinEntry_before"] = minPop
    dic["minX_before"] = minX
    dic["minY_before"] = minY
    rebinCounter = 0
    divFac = 2
    # combinedHist.Rebin2D(3)
    while minPop < threshold:
        nbinsX = combinedHist.GetNbinsX()
        nbinsY = combinedHist.GetNbinsY()
        rebinnedHist = combinedHist.Rebin2D(divFac, divFac, "rebinned")
        rebinnedHist = addOverflows(rebinnedHist)
        # rebinned_Hist = rebin_histo(combinedHist, divFac)
        nbinsX = rebinnedHist.GetNbinsX()
        nbinsY = rebinnedHist.GetNbinsY()
        print("Rebinned to {x},{y} bins with integral {integral} via divFactor {div}".format(x = nbinsX, y = nbinsY, integral = rebinnedHist.Integral(), div = divFac))
        minPop, minX, minY = findMinBinPopulation(rebinnedHist)
        rebinCounter += 1
        divFac += 1

    print("Finished Rebinning")
    if rebinCounter == 0:
        rebinnedHist = combinedHist.Clone()
    rebinnedHist.Draw("colz")
    
    c.SaveAs("rebinnedPlots/rebinned_"+channel+".png")
    # print("Integral after Rebinning: {}".format(rebinned_Hist.Integral(0,nbinsX+1,0,nbinsY+1)))
    dic["Nrebins"] = rebinCounter
    dic["MinEntry"] = minPop
    dic["minX"] = minX
    dic["minY"] = minY
    dic["nBinsX"] = nbinsX
    dic["nBinsY"] = nbinsY
    dic["integral"] = rebinnedHist.Integral()
    dic["divFac"] = divFac-1
    return dic

def correct_channel_name(key, channel_idx):
    channel = key
    if key.count("__") > 1:
        parts = key.split("__")
        channel = "__".join(parts[channel_idx:min(len(parts)-1+channel_idx, len(parts))])
    else:
        channel = key.split("__")[channel_idx]
    return channel
def getOptimizedBinEdges(label, opts):
    # open rootfile
    rfile = ROOT.TFile.Open(opts.histogram_file)
    keylist = [x.GetName() for x in rfile.GetListOfKeys() \
                if not any( x.GetName().endswith(ext) for ext in "Up Down".split()) ]
    
    # collect keys to consider for rebinning
    dic = {}
    notFound = []
    histkey = opts.histkey
    channel_idx = histkey.split("__").index("CHANNEL")
    # channels = getChannels(cat=opts.cat)
    channels = [correct_channel_name(x, channel_idx) for x in keylist]
    print("found {} channels".format(len(channels)))
    channels = list(set(channels))
    print("found {} unique channel names".format(len(channels)))
    # channels = ["ljets_ge4j_ge4t_Reco_ttH_bestJABDToutput_ljets_ge4j_ge4t_Reco_JABDT_tHW_energy_fraction"]
    # for channel in opts.channels.split(","):
    print(channels)
    for channel in channels:
        print("\noptimizing bin edges for channel {}".format(channel))
        consider_for_rebinning = []
        for p in opts.considered_processes.split(","):
            branch = histkey.replace("PROCESS", p)
            branch = branch.replace("CHANNEL", channel)
            # if branch in keylist:
            print("\twill use '{}' for rebinning".format(branch))
            consider_for_rebinning.append(branch)
            # else:
            # print("ERROR: Could not find histogram with name {} in inputfile {}".format(
                # branch, opts.histogram_file))

        # do the rebinning
        if len(consider_for_rebinning) > 0:
            dic[channel] = doRebinning(
                rootfile  = rfile,
                histolist = consider_for_rebinning,
                threshold = float(opts.threshold),
                channel = channel)
        else:
            print("Did not find histograms for rebinning in channel {}".format(channel))
            notFound.append(channel)
    print("Didn't find {notFound}/{all} channels:".format(notFound= len(notFound), all = len(channels)))
    for i in notFound:
        print(i)
    return dic


def main(options):
    d = getOptimizedBinEdges(label = "", opts = options)
    with open('rebins_{outName}.json'.format(outName=options.JSONoutput), 'w') as fp:
        json.dump(d, fp, indent=4)

def parse_arguments():
    parser = OptionParser()

    parser.add_option("-k", "--histkey",
                        help = "use this string to select histogram keys, e.g. 'PROCESS__CHANNEL' (this is the default)",
                        dest = "histkey",
                        type = "str",
                        default = "PROCESS__CHANNEL"
                    )
    # parser.add_option( "-c", "--channels",
    #                     help = """Do rebinning for this channel, e.g. 'ljets_ge4j_ge4t_ttH_node'.
    #                     Can be comma-separated list.
    #                     """,
    #                     # action = "append",
    #                     dest = "channels",
    #                     type = "str"
    #         )
    # parser.add_option( "--cat",
    #                     help = """Do rebinning for this catgory, default = "ge4j_ge4t" """,
    #                     dest = "cat",
    #                     type = "str"
    #         )
    parser.add_option( "--output",
                        help = """outname for RebinJSON""",
                        dest = "JSONoutput",
                        type = "str"
        )
    parser.add_option( "-p", "--processes",
                        help = """Consider these processes for the rebinning.
                        Can be comma-separated.
                        (default = 'ttlf,ttcc,ttbb,singlet,ttbarZ,ttbarW,zjets,wjets,diboson,tHq,tHW')
                        """,
                        action = "append",
                        dest = "considered_processes",
                        type = "str",
                        default = "ttlf,ttcc,ttbb,singlet,ttbarZ,ttbarW,zjets,wjets,diboson,tHq,tHW"
        )
    parser.add_option( "-t", "--threshold",
                        help = "threshold to use when bin uncertainties are used to decide on binning (default = 15)",
                        dest = "threshold",
                        default = 15,
                        type = "float"
                )

    parser.add_option( "-f", "--file", 
                        help = "root file with histograms for binning optimization",
                        dest="histogram_file",
                        default="output_limitInput.root")

    options, args = parser.parse_args()
    # if len(options.channels) == 0:
        # parser.error("ERROR: You need to provide at least one category for rebinning")
    return options, args

if __name__ == '__main__':
    options, args = parse_arguments()
    main(options = options)