import os
import sys
import json
import ROOT
from optparse import OptionParser
from collections import OrderedDict
from math import sqrt
from array import array

def load_channels(file, key):
    channels = []
    if key.count("/") == 2:
        print("loading channels using {}".format(key))
        maindirpath = key.split("/")[0]
        maindir = file.Get(maindirpath)
        maindir.GetListOfKeys().Print()
        channels = [x.GetName() for x in maindir.GetListOfKeys()\
                        if x.IsFolder()]
        print(channels)
    elif key.count("/") == 1:
        print("loading channels using {}".format(key))
        channels = [x.GetName() for x in file.GetListOfKeys()\
                        if x.IsFolder()]
        print(channels)
    else:
        msg = "Sorry, don't know what to do!"
        raise ValueError(msg)
    return channels
def open_file(path):
    if not os.path.exists(path):
        msg = "File {} does not exist".format(path)
        raise ValueError(msg)
    f = ROOT.TFile.Open(path)
    if not f.IsOpen() or f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered):
        msg = "File {} is broken!".format(path)
        raise ValueError(msg)
    return f

def combine_histos(file, hlist, key, bin_edges = None):
    h = None
    
    for name in hlist:
        process_key = key.replace("PROCESS", name)
        tmp = file.Get(process_key)
        if not isinstance(tmp, ROOT.TH1):
            print("Could not load '{}' from '{}'".\
                    format(process_key, file.GetName()))
            print("skipping...")
        elif h is None:
            print("cloning histogram '{}'".format(tmp.GetName()))
            h = tmp.Clone()
            # h.Print("range")
        else:
            print("adding histogram '{}'".format(tmp.GetName()))
            h.Add(tmp)
            # h.Print("range")
    if h and bin_edges:
        h = updateBinEdges(h, bin_edges)
    return h

def get_values(file, signals, backgrounds, key, name_template, mode, \
                bin_edges = None):
    values = {}
    print("key: {}".format(key))
    print("="*130)
    print("loading signal")
    print("="*130)
    h_signal = combine_histos(file = file, hlist = signals, key = key,\
                                bin_edges = bin_edges)
    if h_signal is None:
        print("Error: Could not load signal with key '{}'".format(key))
        return values
    print("="*130)
    print("loading background")
    print("="*130)
    h_background = combine_histos(file = file, hlist = backgrounds, key = key,\
                                bin_edges = bin_edges)

    if h_background is None:
        print("Error: Could not load background with key '{}'".format(key))
        return values
    nbins = h_signal.GetNbinsX()
    for i in range(1, nbins + 1):
        sig = h_signal.GetBinContent(i)
        bkg = h_background.GetBinContent(i)
        value = -1
        if not bkg == 0:
            if mode == "s_o_b":
                value = sig/bkg
            elif mode == "s_o_sqrtb":
                value = sig/sqrt(bkg)
            elif mode == "s_o_uncertb":
                value = sig/h_background.GetBinError(i)
        else:
            print("ERROR: Background stack is zero")
            print("\tbin {}".format(i))
            print("\tsignals: {}".format(",".join(signals)))
            print("\tbackgrounds: {}".format(",".join(backgrounds)))
        tmp_name = name_template.format(BINNUMBER = i)
        values[tmp_name] = {
            "value": value,
            "signal": sig,
            "background" : bkg
        }
        
    return values

def create_value_dict(file, signals, backgrounds, channels, key, mode,\
                        datacardpath = None):
    final_dict = {}
    print("base key: {}".format(key))
    metavar = {
        "signals": signals,
        "backgrounds": backgrounds,
        "channels" : channels,
        "key" : key,
        "rootfile": file.GetName()
    }
    final_dict["metavar"] = metavar
    values = {}
    for ch in channels:
        thiskey = key.replace("CHANNEL", ch)
        bin_edges = load_original_binedges(datacardpath, ch)
        values.update(get_values(file = file, signals = signals,
                                 backgrounds=backgrounds, key = thiskey,
                                 name_template=ch + "_bin_{BINNUMBER}",
                                 mode = mode, bin_edges = bin_edges))
    
    values = OrderedDict(sorted(values.iteritems(), \
                                key = lambda x: x[1]["value"]))
    print(values)
    final_dict["values"] = values
    return final_dict

def main(*args,**kwargs):
    signals = kwargs.get("signals")
    backgrounds = kwargs.get("backgrounds")
    filepath = kwargs.get("rootfile")
    file = open_file(filepath)
    channels = kwargs.get("channels")
    nomkey = kwargs.get("nominalkey")
    mode = kwargs.get("mode")
    datacard = kwargs.get("datacard")
    if len(channels) == 0:
        channels = load_channels(file = file, key = nomkey)
    
    values = create_value_dict(file = file, signals = signals,
                        backgrounds = backgrounds, 
                        channels = channels,
                        key = nomkey, mode = mode, datacardpath = datacard)
    file.Close()
    outname = kwargs.get("outfile")
    if not outname.endswith(".json"):
        outname += ".json"
    with open(outname, "w") as outfile:
        json.dump(values, outfile, separators=(",", ":"), indent=4)
    
def replace_placeholder(hlist):
    if not hlist is None:
        decays = [  'ttH_hbb',
                    'ttH_hcc',
                    'ttH_htt',
                    'ttH_hgg',
                    'ttH_hgluglu',
                    'ttH_hww',
                    'ttH_hzz',
                    'ttH_hzg']
        if "ttH" in hlist:
            index = hlist.index("ttH")
            hlist.pop(index)
            hlist += decays
def parse_list(hlist):
    final_list = []
    for entry in hlist:
        final_list += entry.split(",")
    return final_list

def updateBinEdges(hist, edges):
    newHist = ROOT.TH1F(hist.GetName(), hist.GetTitle(), len(edges)-1, array("f", edges))
    for i in range(len(edges)+1):
        newHist.SetBinContent(i, hist.GetBinContent(i))
        newHist.SetBinError(i, hist.GetBinError(i))
    
    return newHist

def load_original_binedges(datacardpath, channelName):
    binEdges = None
    if datacardpath:
        if not os.path.exists(datacardpath):
            print("ERROR: could not load datacard from '{}'".format(datacardpath))
        datacard_dir = os.path.dirname(os.path.abspath(datacardpath))
        with open(datacardpath, "r") as card:
            lines = card.readlines()
        lines = [l for l in lines if l.startswith("shapes")]
        channelLine = False
        for l in lines:
            line = l.split(" ")
            if channelName in line:
                channelLine = line
                break
        if channelLine is None: sys.exit("no channel {} found in datacard".format(channelName))
        channelLine = [elem for elem in channelLine if not elem == ""]
        binFileName = channelLine[3]
        binFileName = binFileName if os.path.isabs(binFileName) else os.path.join(datacard_dir, binFileName)
        binKey = channelLine[4].replace("$PROCESS","data_obs")
        binKey = binKey.replace("$CHANNEL", channelName)
        
        binFile = ROOT.TFile(binFileName)
        print("loading " + binKey)
        binHist = binFile.Get(binKey)
        binEdges = []
        for i in range(binHist.GetNbinsX()+1):
            binEdges.append( binHist.GetBinLowEdge(i+1) )
    return binEdges

def parse_arguments():
    parser = OptionParser()
    
    combinefolder_options = ["shapes_prefit",
                                 "shapes_fit_b",
                                 "shapes_fit_s"]
    parser.add_option("-s", "--signal",
                      help = " ".join(
                          """
                          use these processes as signal. This
                          should be the process names as they are
                          used in the histograms. Can be called
                          multiple times.
                          """.split()
                        ),
                      dest = "signals",
                      action = "append",
                      default = [])
    parser.add_option("-b", "--background",
                      help = " ".join(
                          """
                          use these processes as background. This
                          should be the process names as they are
                          used in the histograms. Can be called
                          multiple times.
                          """.split()
                        ),
                      dest = "backgrounds",
                      action = "append",
                      default = [])
    parser.add_option("--channel",
                      help = " ".join(
                          """
                          read histograms for this channelThis
                          should be the channel names as they are
                          used in the datacards. Can be called
                          multiple times.
                          """.split()
                        ),
                      dest = "channels",
                      action = "append",
                      default = [])
    parser.add_option("-k", "--nominalkey",
                      help = " ".join(
                            """
                            use this key to load histograms from
                            the root files. The keywords 'PROCESS' and
                            'CHANNEL' will be replaced when loading
                            the histograms
                            Default is 'PROCESS__CHANNEL'
                            """.split()
                        ),
                      dest = "nominalkey",
                      default = "PROCESS__CHANNEL"
                      )
    parser.add_option("-c", "--combinefolder",
                      help = " ".join(
                          """
                          use this flag if you want to use histograms
                          produced by using the combine option
                          '--saveShapes'. Choices are the folders this
                          option provides: shapes_prefit, shapes_fit_b,
                          shapes_fit_s. Activating this option will also
                          overwrite the option for the histogram keys with
                          'CHOICE/CHANNEL/PROCESS'
                          """.split()
                        ),
                      dest = "combinefolder",
                      choices = combinefolder_options,
                      metavar = "/".join(combinefolder_options),
                      default = None
                      
                      )
    parser.add_option("-r", "--rootfile",
                      help = " ".join(
                          """
                          path to file containing the histograms to read.
                          
                          """.split()
                        ),
                      dest = "rootfile",
                      metavar = "path/to/file.root"
                      )
    parser.add_option("-d", "--datacard",
                      help = " ".join(
                          """
                          path to datacard belonging to the root file 
                          (option r).
                          Will be used to load original binning of
                          templates.
                          Use this to avoid zero-padded bins in combine
                          histograms.                          
                          """.split()
                        ),
                      dest = "datacard",
                      metavar = "path/to/datacard.txt"
                      )
    parser.add_option("-o", "--outfile",
                      help = " ".join(
                          """
                          save S/B in this output file
                          
                          """.split()
                        ),
                      dest = "outfile",
                      metavar = "path/to/file.json"
                      )
    parser.add_option("-m", "--mode",
                      help = " ".join(
                          """
                          define what measure you want to compute.
                          Current choices: s_o_b (S/B), s_o_sqrtb (S/sqrt(B)),
                          s_o_uncertb (S/Bin_Uncertainty(B)).
                          Default: s_o_b
                          """.split()
                        ),
                      dest = "mode",
                      choices = ["s_o_b", "s_o_sqrtb", "s_o_uncertb"],
                      default = "s_o_b"
                      )
    
    opts, args = parser.parse_args()
    opts.signals = parse_list(opts.signals)
    opts.backgrounds = parse_list(opts.backgrounds)
    #for convenience
    replace_placeholder(opts.signals)
    replace_placeholder(opts.backgrounds)
    if opts.combinefolder:
        opts.nomkey = "{}/CHANNEL/PROCESS".format(opts.combinefolder)
    return opts, args

if __name__ == "__main__":
    
    options, files = parse_arguments()
    print(options)
    main(**vars(options))