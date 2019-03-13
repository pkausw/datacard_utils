#!/usr/bin/env python
import os, sys, re, array, ROOT

# usage: python PrePostFitPlots.py mlfitfile.root corresponding_datacard.txt

import CMS_lumi

ROOT.gROOT.SetBatch(True)

VERBOSE = False

OUTPUT_EXTENSIONS = [
  'pdf',
  'C',
#  'png',
#  'root',
]

color_dict = {}
color_dict["ttbarOther"]     = ROOT.kRed+2
color_dict["ttbarPlusCCbar"] = ROOT.kRed-9
color_dict["ttbarPlusB"]     = ROOT.kRed+1
color_dict["ttbarPlus2B"]    = ROOT.kRed-5
color_dict["ttbarPlusBBbar"] = ROOT.kRed+3
color_dict["singlet"]        = ROOT.kMagenta
color_dict["stop"]           = ROOT.kMagenta
color_dict["zjets"]          = ROOT.kOrange-5
color_dict["wjets"]          = ROOT.kOrange-9
color_dict["vjets"]          = ROOT.kOrange-4
color_dict["ttbarW"]         = ROOT.kBlue-10
color_dict["ttbarZ"]         = ROOT.kBlue-6
color_dict["ttbarV"]         = ROOT.kBlue-10
color_dict["ttw"]            = ROOT.kBlue-10
color_dict["ttz"]            = ROOT.kBlue-6
color_dict["ttv"]            = ROOT.kBlue-10
color_dict["diboson"]        = ROOT.kAzure+2

color_qcd = ROOT.TColor(9007, 102/255., 201/255., 77/255.)
color_dict  ["QCD"]          = 9007
color_dict["ddQCD"]          = 9007

color_signal=ROOT.kCyan
color_dict["ttH_hbb"]     = color_signal
color_dict["ttH_hcc"]     = color_signal
color_dict["ttH_htt"]     = color_signal
color_dict["ttH_hgg"]     = color_signal
color_dict["ttH_hgluglu"] = color_signal
color_dict["ttH_hww"]     = color_signal
color_dict["ttH_hzz"]     = color_signal
color_dict["ttH_hzg"]     = color_signal
color_dict["ttH_nonhbb"]  = color_signal
color_dict["ttH"]         = color_signal

color_dict["total_signal"]     = color_signal
color_dict["total_background"] = ROOT.kBlack
color_dict["total_covar"]      = ROOT.kBlack
color_dict["total"]            = ROOT.kBlack
color_dict["data"]             = ROOT.kBlack

latex_dict = {}
latex_dict["ttbarOther"]     = "t#bar{t}+lf"
latex_dict["ttbarPlusCCbar"] = "t#bar{t}+c#bar{c}"
latex_dict["ttbarPlusB"]     = "t#bar{t}+b"
latex_dict["ttbarPlus2B"]    = "t#bar{t}+2b"
latex_dict["ttbarPlusBBbar"] = "t#bar{t}+b#bar{b}"
latex_dict["singlet"] = "Single t"
latex_dict["stop"]    = "Single t"
latex_dict["zjets"] = "Z+jets"
latex_dict["wjets"] = "W+jets"
latex_dict["vjets"] = "V+jets"
latex_dict["ttbarW"] = "t#bar{t}+W"
latex_dict["ttbarZ"] = "t#bar{t}+Z"
latex_dict["ttbarV"] = "t#bar{t}+V#color[0]{~~~}" # white ~ needed to keep legend column width constant...
latex_dict["ttw"] = "t#bar{t}+W"
latex_dict["ttz"] = "t#bar{t}+Z"
latex_dict["ttv"] = "t#bar{t}+V#color[0]{~~~}" # white ~ needed to keep legend column width constant...
latex_dict["diboson"] = "Diboson"
latex_dict  ["QCD"] = "Multijet"
latex_dict["ddQCD"] = "Multijet"

latex_dict["ttH_hbb"]     = "t#bar{t}H"
latex_dict["ttH_hcc"]     = "t#bar{t}H"
latex_dict["ttH_htt"]     = "t#bar{t}H"
latex_dict["ttH_hgg"]     = "t#bar{t}H"
latex_dict["ttH_hgluglu"] = "t#bar{t}H"
latex_dict["ttH_hww"]     = "t#bar{t}H"
latex_dict["ttH_hzz"]     = "t#bar{t}H"
latex_dict["ttH_hzg"]     = "t#bar{t}H"
latex_dict["ttH_nonhbb"]  = "t#bar{t}H"
latex_dict["ttH"]         = "t#bar{t}H_{SM}"

latex_dict["total_background"] = "total background"
latex_dict["total_signal"] = "signal#color[0]{~~~}" # white ~ needed to keep legend column width constant...
latex_dict["total_covar"] = "COV"
latex_dict["total"] = "total s+b"
latex_dict["data"] = "Data"

controlplots_variable_label = {}
controlplots_variable_label["controlplots_njets"] = "Number of jets"
controlplots_variable_label["controlplots_btags"] = "Number of b-tagged jets"
controlplots_variable_label["controlplots_var1"]  = "Sum pt(jet)/E(jet)"
controlplots_variable_label["controlplots_var2"]  = "Avg. #Delta #eta(jets)"

controlplots_entries_label = {}
controlplots_entries_label["controlplots_njets"] = "Events"
controlplots_entries_label["controlplots_btags"] = "Events"
controlplots_entries_label["controlplots_var1"] = "Events"
controlplots_entries_label["controlplots_var2"] = "Events"

controlplots_ndivisions = {}
controlplots_ndivisions["controlplots_njets"] = 110
controlplots_ndivisions["controlplots_btags"] = 105
controlplots_ndivisions["controlplots_var1"] = 506
controlplots_ndivisions["controlplots_var2"] = 506

controlplots_logy = {}
controlplots_logy["controlplots_njets"] = True
controlplots_logy["controlplots_btags"] = True
controlplots_logy["controlplots_var1"] = False
controlplots_logy["controlplots_var2"] = False

controlplots_ymin = {}
controlplots_ymin["controlplots_njets"] = 1E2
controlplots_ymin["controlplots_btags"] = 1E1
controlplots_ymin["controlplots_var1"] = 1E-1
controlplots_ymin["controlplots_var2"] = 1E-1

controlplots_ymax = {}
controlplots_ymax["controlplots_njets"] = 3E7
controlplots_ymax["controlplots_btags"] = 3E8
controlplots_ymax["controlplots_var1"] = 1E-1
controlplots_ymax["controlplots_var2"] = 1E-1

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

category_label_font_size = 0.047

################################################################
################################################################
################################################################

CHANNELS_COSMETICS_DICT = {

  # 2016 FH
  'ttH_hbb_13TeV_2016_fh_7j3b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (7 jets, 3 b tags)']        , 'logY': True, 'ymin': 1.4, 'ymax': 5e7, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_fh_7j4b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (7 jets, #geq4 b tags)']    , 'logY': True, 'ymin': 1.4, 'ymax': 3e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_fh_8j3b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (8 jets, 3 b tags)']        , 'logY': True, 'ymin': 1.4, 'ymax': 5e7, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_fh_8j4b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (8 jets, #geq4 b tags)']    , 'logY': True, 'ymin': 1.4, 'ymax': 3e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_fh_9j3b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (#geq9 jets, 3 b tags)']    , 'logY': True, 'ymin': 1.4, 'ymax': 1e7, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_fh_9j4b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (#geq9 jets, #geq4 b tags)'], 'logY': True, 'ymin': 1.4, 'ymax': 3e5, 'ymaxSF': 1, },

  # 2016 SL
  'ttH_hbb_13TeV_2016_sl_4j3b_DNN_ttlf': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+lf'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_4j3b_DNN_ttcc': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+c#bar{c}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_4j3b_DNN_tt2b': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+2b'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_4j3b_DNN_ttb' : { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+b'       +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_4j3b_DNN_ttbb': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+b#bar{b}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_4j3b_DNN_ttH' : { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}H'        +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },

  'ttH_hbb_13TeV_2016_sl_5j3b_DNN_ttlf': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+lf'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_5j3b_DNN_ttcc': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+c#bar{c}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_5j3b_DNN_tt2b': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+2b'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_5j3b_DNN_ttb' : { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+b'       +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_5j3b_DNN_ttbb': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+b#bar{b}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_5j3b_DNN_ttH' : { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}H'        +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },

  'ttH_hbb_13TeV_2016_sl_6j3b_DNN_ttlf': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+lf'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_6j3b_DNN_ttcc': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+c#bar{c}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_6j3b_DNN_tt2b': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+2b'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_6j3b_DNN_ttb' : { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+b'       +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e4, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_6j3b_DNN_ttbb': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+b#bar{b}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_sl_6j3b_DNN_ttH' : { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}H'        +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },

  # 2016 DL
  'ttH_hbb_13TeV_2016_dl_4j3b_BDT'      : { 'titleX': 'BDT discriminant', 'labels': ['DL (#geq4 jets, 3 b tags)']                , 'logY': True , 'ymin': 1.0, 'ymax': 2e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_dl_4j4b_loBDT_MEM': { 'titleX': 'MEM discriminant', 'labels': ['SL (#geq4 jets, #geq4 b tags)', 'BDT-low'] , 'logY': False, 'ymin': 0.1, 'ymax': 190, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2016_dl_4j4b_hiBDT_MEM': { 'titleX': 'MEM discriminant', 'labels': ['SL (#geq4 jets, #geq4 b tags)', 'BDT-high'], 'logY': False, 'ymin': 0.1, 'ymax':  70, 'ymaxSF': 1, },

  # 2017 FH
  'ttH_hbb_13TeV_2017_fh_7j3b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (7 jets, 3 b tags)']        , 'logY': True, 'ymin': 1.4, 'ymax': 5e7, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_fh_7j4b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (7 jets, #geq4 b tags)']    , 'logY': True, 'ymin': 1.4, 'ymax': 3e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_fh_8j3b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (8 jets, 3 b tags)']        , 'logY': True, 'ymin': 1.4, 'ymax': 5e7, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_fh_8j4b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (8 jets, #geq4 b tags)']    , 'logY': True, 'ymin': 1.4, 'ymax': 3e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_fh_9j3b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (#geq9 jets, 3 b tags)']    , 'logY': True, 'ymin': 1.4, 'ymax': 1e7, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_fh_9j4b_MEM': { 'titleX': 'MEM discriminant', 'labels': ['FH (#geq9 jets, #geq4 b tags)'], 'logY': True, 'ymin': 1.4, 'ymax': 3e5, 'ymaxSF': 1, },

  # 2017 SL
  'ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttlf': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+lf'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e6, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttcc': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+c#bar{c}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_4j3b_DNN_tt2b': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+2b'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttb' : { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+b'       +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttbb': { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}+b#bar{b}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttH' : { 'titleX': 'DNN discriminant', 'labels': ['SL (4 jets, #geq3 b tags)', 't#bar{t}H'        +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },

  'ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttlf': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+lf'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e6, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttcc': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+c#bar{c}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_5j3b_DNN_tt2b': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+2b'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttb' : { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+b'       +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttbb': { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}+b#bar{b}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttH' : { 'titleX': 'DNN discriminant', 'labels': ['SL (5 jets, #geq3 b tags)', 't#bar{t}H'        +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },

  'ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttlf': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+lf'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 5e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttcc': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+c#bar{c}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 2e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_6j3b_DNN_tt2b': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+2b'      +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttb' : { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+b'       +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttbb': { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}+b#bar{b}'+' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttH' : { 'titleX': 'DNN discriminant', 'labels': ['SL (#geq6 jets, #geq3 b tags)', 't#bar{t}H'        +' node'], 'logY': True, 'ymin': 1.4, 'ymax': 1e5, 'ymaxSF': 1, },

  # 2017 DL
  'ttH_hbb_13TeV_2017_dl_3j2b_BDT': { 'titleX': 'BDT discriminant', 'labels': ['DL (3 jets, 2 b tags)']        , 'logY': True, 'ymin': 0.5, 'ymax': 5e6, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_dl_3j3b_BDT': { 'titleX': 'BDT discriminant', 'labels': ['DL (3 jets, 3 b tags)']        , 'logY': True, 'ymin': 0.5, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_dl_4j2b_BDT': { 'titleX': 'BDT discriminant', 'labels': ['DL (#geq4 jets, 2 b tags)']    , 'logY': True, 'ymin': 0.5, 'ymax': 5e6, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_dl_4j3b_BDT': { 'titleX': 'BDT discriminant', 'labels': ['DL (#geq4 jets, 3 b tags)']    , 'logY': True, 'ymin': 0.5, 'ymax': 1e5, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_dl_4j4b_BDT': { 'titleX': 'BDT discriminant', 'labels': ['DL (#geq4 jets, #geq4 b tags)'], 'logY': True, 'ymin': 0.5, 'ymax': 4e4, 'ymaxSF': 1, },

  # 2017 DL (baseline selection)
  'ttH_hbb_13TeV_2017_dl_baseline_Njets' : { 'titleX': 'Number of jets'         , 'labels': ['DL (#geq2 jets, #geq1 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 5e8, 'ymaxSF': 1, },
  'ttH_hbb_13TeV_2017_dl_baseline_Nbtags': { 'titleX': 'Number of b-tagged jets', 'labels': ['DL (#geq2 jets, #geq1 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 5e8, 'ymaxSF': 1, },

  # 2017 DL (BDT inputs)
  'ttH_hbb_13TeV_2017_dl_4j3b_MEM'                             : { 'titleX': 'MEM'                           , 'labels': ['DL (#geq4 jets, ' +'3 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 1e5, },
  'ttH_hbb_13TeV_2017_dl_4j3b_btagDiscriminatorAverage_tagged' : { 'titleX': 'average DeepCSV value (b-jets)', 'labels': ['DL (#geq4 jets, ' +'3 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 1e6, },

  'ttH_hbb_13TeV_2017_dl_4j4b_MEM'                             : { 'titleX': 'MEM'                           , 'labels': ['DL (#geq4 jets, #geq4 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 4e4, },
  'ttH_hbb_13TeV_2017_dl_4j4b_maxDeltaEta_tag_tag'             : { 'titleX': '#Delta#eta^{max}_{bb}'         , 'labels': ['DL (#geq4 jets, #geq4 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 4e4, },

  # 2017 SL (baseline selection)
  'N_Jets'  : { 'titleX': 'Number of jets'         , 'labels': ['SL (#geq4 jets, #geq2 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 5e9, 'ymaxSF': 1, },
  'N_BTagsM': { 'titleX': 'Number of b-tagged jets', 'labels': ['SL (#geq4 jets, #geq2 b tags)'], 'logY': True, 'ymin': 1.0, 'ymax': 5e9, 'ymaxSF': 1, },
}

CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Njets'] ['binLabelsX']  = ['2', '3', '4', '5', '6', '7', '8', '#geq9']
CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Njets'] ['Ndivisions']  = -414
CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Njets'] ['titleY']      = 'Events'
CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Njets'] ['addFitLabel'] = False

CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Nbtags']['binLabelsX']  = ['1', '2', '3', '4', '#geq5']
CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Nbtags']['Ndivisions']  = -414
CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Nbtags']['titleY']      = 'Events'
CHANNELS_COSMETICS_DICT['ttH_hbb_13TeV_2017_dl_baseline_Nbtags']['addFitLabel'] = False

CHANNELS_COSMETICS_DICT['N_Jets'] ['binLabelsX']  = ['4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '#geq14']
CHANNELS_COSMETICS_DICT['N_Jets'] ['Ndivisions']  = -414
CHANNELS_COSMETICS_DICT['N_Jets'] ['titleY']      = 'Events'
CHANNELS_COSMETICS_DICT['N_Jets'] ['addFitLabel'] = False

CHANNELS_COSMETICS_DICT['N_BTagsM']['binLabelsX']  = ['2', '3', '4', '#geq5']
CHANNELS_COSMETICS_DICT['N_BTagsM']['Ndivisions']  = -414
CHANNELS_COSMETICS_DICT['N_BTagsM']['titleY']      = 'Events'
CHANNELS_COSMETICS_DICT['N_BTagsM']['addFitLabel'] = False

## luminosity string
for i_cat in CHANNELS_COSMETICS_DICT:

    if   i_cat.startswith('ttH_hbb_13TeV_2016'): CHANNELS_COSMETICS_DICT[i_cat]['lumi'] = '35.9 fb^{-1} (13 TeV)'
    elif i_cat.startswith('ttH_hbb_13TeV_2017'): CHANNELS_COSMETICS_DICT[i_cat]['lumi'] = '41.5 fb^{-1} (13 TeV)'
    elif i_cat.startswith('N_')                : CHANNELS_COSMETICS_DICT[i_cat]['lumi'] = '41.5 fb^{-1} (13 TeV)'
    else                                       : CHANNELS_COSMETICS_DICT[i_cat]['lumi'] = ''
## -----------------

################################################################
################################################################
################################################################

def GetLegendColumns():

    legend_columns = [

      # left column
      [
        'data',
        'ttbarOther',
        'ttbarPlusCCbar',
        'ttbarPlusB',
        'ttbarPlus2B',
        'ttbarPlusBBbar',
      ],

      # right column
      [
        'total_signal',

        'ddQCD',
          'QCD',

#        'stop',
        'singlet',

        'vjets',
        'zjets',
        'wjets',

#        'ttv',
#        'ttz',
#        'ttw',
        'ttbarV',
        'ttbarZ',
        'ttbarW',

        'diboson',

        'Uncertainty',
      ],
    ]

    return legend_columns

def GetSortedProcesses(processes_histos_dict):
    order = [
        'diboson',
        
        'ttbarW',
        'ttbarZ',
        'ttbarV',
        'ttw',
        'ttz',
        'ttv',
        
        'wjets',
        'zjets',
        'vjets',

        'singlet',
        'stop',

        'ttbarPlusBBbar',
        'ttbarPlus2B',
        'ttbarPlusB',
        'ttbarPlusCCbar',
        'ttbarOther',
        'total_background',

          'QCD',
        'ddQCD',

        'ttH_hgg',
        'ttH_hzg',
        'ttH_hcc',
        'ttH_hgluglu',
        'ttH_htt',
        'ttH_hzz',
        'ttH_hww',
        'ttH_nonhbb',
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
#    if VERBOSE: print proc_A, ": ", intA 
#    if VERBOSE: print proc_B, ": ", intB
#    if VERBOSE: print  "Sum: ", intA+intB

    if proc_A in new_dict or proc_B in new_dict:
        if proc_A in new_dict:
            new_dict[proc_Sum] = new_dict[proc_A].Clone()
            if proc_B in new_dict:
                new_dict[proc_Sum].Add(new_dict[proc_B])
        else:
            new_dict[proc_Sum] = new_dict[proc_B].Clone()

        if proc_A in new_dict:
            new_dict.pop(proc_A)
        if proc_B in new_dict:
            new_dict.pop(proc_B)

#    if VERBOSE: print proc_Sum, ": ", new_dict[proc_Sum].Integral()
        
    return new_dict

                                
def ColorizeHistograms(processes_histos_dict):
    for process in processes_histos_dict:
        processes_histos_dict[process].SetLineWidth(2)
        processes_histos_dict[process].SetLineColor(ROOT.kBlack)
        processes_histos_dict[process].SetFillColor(color_dict[process])
    return 0

def SetPadMargins():
    ROOT.gStyle.SetFrameLineWidth(2);
    ROOT.gStyle.SetPadLeftMargin(0.15)
    ROOT.gStyle.SetPadRightMargin(0.04)
    ROOT.gStyle.SetPadTopMargin(0.08)
    ROOT.gStyle.SetPadBottomMargin(0.0)

def GetCanvas(canvas_name):
    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas(canvas_name,"",820,850)
    c.Divide(1,2)
    c.GetPad(1).SetPad(0.0,0.3,1.0,1.0)
    c.GetPad(2).SetPad(0.0,0.0,1.0,0.3)
    c.GetPad(1).SetBottomMargin(0)
    c.GetPad(1).SetTicks(1,1)
    c.GetPad(2).SetTopMargin(0)
    c.GetPad(2).SetBottomMargin(0.32)
    c.GetPad(2).SetTicks(1,1)
    c.cd()
    return c

# returns directory in tfile***    
def GetDirectory(fitfile, directory):

    dir_ = fitfile.Get(directory)

    if VERBOSE: print "Input Folder: ", dir_

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
    datahisto.SetName (oldname+"_old")
    datahisto.SetTitle(oldname+"_old")
    binEdgeArray=array.array("f",[])
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

def blindDataHisto(datahisto, signalhisto, backgroundhisto,SoBCut=0.01):
    oldname=datahisto.GetName()
    datahisto.SetName(oldname+"_old")
    binEdgeArray=array.array("f",[])
    nBins=datahisto.GetNbinsX()
    for i in range(1,nBins+2,1):
      binEdgeArray.append(datahisto.GetBinLowEdge(i))

    newHisto = ROOT.TH1F(oldname, datahisto.GetTitle(), len(binEdgeArray)-1,binEdgeArray)

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
    if VERBOSE: print " >>>> 1 dirr: ", dirr
    # get channels/categories in this directory
    categories = GetChannels(dirr)
    if VERBOSE: print " >>>> 2 categories: ", categories
    # get processes in the different channels/categories as dict["chX"]->[processes]
    categories_processes_dict = GetProcessesInCategories(dirr,categories)
    if VERBOSE: print " >>>> 3 categories_processes_dict: ", categories_processes_dict

    # get final dictionary, e.g. dict["ch1"]["ttbarOther"]->corresponding histogram
    categories_processes_histos_dict = GetHistosForCategoriesProcesses(dirr,categories_processes_dict)

    if VERBOSE: print categories_processes_histos_dict

    return categories_processes_histos_dict

def GetDataHistogram(processes_histos_dict):
    data = None
    if "data" in processes_histos_dict:
        data = processes_histos_dict["data"]
        data.SetMarkerStyle(20)
        data.SetMarkerSize(1.2)
        #data.SetLineWidth(2)
        data.SetFillStyle(0)        
    return data

def GetSignal(processes_histos_dict,background_integral):
    signal_unscaled = processes_histos_dict["total_signal"]
    signal=signal_unscaled.Clone()
    signal.SetLineColor(color_dict["total_signal"])
    signal.SetFillStyle(0)
    signal.SetLineWidth(3)
    signal_integral = signal.Integral()

    scaleFactor=0.0

    scaleMode = 15.

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

def GetLegend(prepostfitflag):
#    legend = ROOT.TLegend(0.59,0.5,0.97,0.87)
    legend = ROOT.TLegend(0.54,0.5,0.98,0.87)
#    if prepostfitflag == "shapes_prefit":
#        legend.SetX1NDC(0.56)
#        legend.SetX2NDC(0.94)
    legend.SetNColumns(2)
    legend.SetLineStyle(0);
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.044)
    return legend

def getLegendL(prepostfitflag):
    legend=ROOT.TLegend()
    if prepostfitflag == "shapes_prefit":
        legend.SetX1NDC(0.58)
    else:
        legend.SetX1NDC(0.61)
    legend.SetX2NDC(0.81)
    legend.SetY1NDC(0.79)
    legend.SetY2NDC(0.87)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    #legend.SetTextSize(0.038);
    legend.SetTextSize(0.042);
    legend.SetFillStyle(0);
    return legend

def getLegendR(prepostfitflag):
    legend=ROOT.TLegend()
    if prepostfitflag == "shapes_prefit":
        legend.SetX1NDC(0.87)
    else:
        legend.SetX1NDC(0.79)
    legend.SetX2NDC(0.99)
    legend.SetY1NDC(0.79)
    legend.SetY2NDC(0.87)
    legend.SetBorderSize(0);
    legend.SetLineStyle(0);
    legend.SetTextFont(42);
    #legend.SetTextSize(0.038);
    legend.SetTextSize(0.042);
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
    error_graph.SetFillStyle(3645)
    error_graph.SetFillColor(ROOT.kBlack)
    return error_graph

def GetRatioGraph(nominator,denominator,templateHisto=None):
    ratio  = ROOT.TGraphAsymmErrors(nominator.GetNbinsX())
    lowerx = 0
    upperx = nominator.GetNbinsX()
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
    ratio.SetMarkerSize(1.2)
    #ratio.SetLineWidth(2)

    ratio.GetYaxis().SetRangeUser(0.01,1.99)
    ratio.GetXaxis().SetLimits(lowerx,upperx)

    ratio.SetTitle('')

    ratio.GetYaxis().SetLabelFont(axis_label_font)
    ratio.GetYaxis().SetLabelOffset(axis_label_offset)
    ratio.GetYaxis().SetTickLength(tick_length_ryaxis)
    ratio.GetYaxis().SetLabelSize(axis_label_size/sf_stack_ratio)
    ratio.GetXaxis().SetLabelFont(axis_label_font)
    ratio.GetXaxis().SetLabelOffset(axis_label_offset)
    ratio.GetXaxis().SetLabelSize(axis_label_size/sf_stack_ratio)
    ratio.GetXaxis().SetTickLength(tick_length_rxaxis)

    ratio.GetYaxis().SetTitle("Data / Pred.")
    ratio.GetYaxis().SetTitleFont(axis_title_font)
    ratio.GetYaxis().SetTitleSize(axis_title_size)
    ratio.GetYaxis().SetTitleOffset(yaxis_title_offset)

    ratio.GetXaxis().SetTitle("Discriminant value")
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


def has_equidistant_bins(h):
    width = h.GetXaxis().GetBinWidth(1)
    for ibin in range(2,h.GetXaxis().GetNbins()+1):
        if abs( h.GetXaxis().GetBinWidth(ibin) - width ) > 1E-4:
            return False

    return True

def SetUpStack(stack,prepostfitflag):
    stack.GetYaxis().SetLabelFont(axis_label_font)
    stack.GetYaxis().SetLabelOffset(axis_label_offset)
    stack.GetYaxis().SetLabelSize(axis_label_size)
    stack.GetYaxis().SetTickLength(tick_length_yaxis)
    stack.GetXaxis().SetTickLength(tick_length_xaxis)

    if has_equidistant_bins(stack):
        width = stack.GetXaxis().GetBinWidth(1)
        stack.GetYaxis().SetTitle("Events / "+str(round(width,2)))
    else:
        stack.GetYaxis().SetTitle("Events / Bin")
        
    stack.GetYaxis().SetTitleOffset(yaxis_title_offset / sf_stack_ratio)
    stack.GetYaxis().SetTitleFont(axis_title_font)
    stack.GetYaxis().SetTitleSize(sf_stack_ratio * axis_title_size)

    stack.SetTitle("")

#    if "controlplots" in prepostfitflag:
#        stack.GetYaxis().SetTitle     (controlplots_entries_label[prepostfitflag])
#        stack.GetXaxis().SetNdivisions(controlplots_ndivisions   [prepostfitflag])

    return 0

# replace this with proper cms label function
def GetCMSandInfoLabels(pubstatus):

    posy = 1.0-ROOT.gStyle.GetPadTopMargin()+0.03

    cms = ROOT.TPaveText(ROOT.gStyle.GetPadLeftMargin(), posy+0.02, 1.0-ROOT.gStyle.GetPadRightMargin(), 1.0, "NDC")

    if   pubstatus == "public"     : cms.AddText("#scale[1.5]{#bf{CMS}}")
    elif pubstatus == "preliminary": cms.AddText("#scale[1.5]{#bf{CMS}} #scale[1.1]{#it{Preliminary}}")
    elif pubstatus == "supp"       : cms.AddText("#scale[1.5]{#bf{CMS}} #scale[1.1]{#it{Supplementary}}")

    cms.SetFillColor(0)
    cms.SetTextFont(43)
    cms.SetTextSize(26)
    cms.SetMargin(0.)
    cms.SetTextAlign(13)

    info = ROOT.TPaveText(0.7, posy, 1.0-ROOT.gStyle.GetPadRightMargin(), 1.0, "NDC")
    info.SetFillColor(0)
    info.SetTextFont(43)
    info.SetTextSize(26)
    info.SetMargin(0.)
    info.SetTextAlign(33)

    return cms, info

def GetFitLabel(catname, prepostfitflag):

    label = None

    if CHANNELS_COSMETICS_DICT[catname].get('addFitLabel', True):

       if   prepostfitflag == 'shapes_prefit': fit_label = 'Pre-fit expectation'
       elif prepostfitflag == 'shapes_fit_b' : fit_label = 'Post-fit (Background-only)'
       elif prepostfitflag == 'shapes_fit_s' : fit_label = 'Post-fit'

       label = ROOT.TLatex(ROOT.gStyle.GetPadLeftMargin()+0.05, 1.0-ROOT.gStyle.GetPadTopMargin()-0.2, fit_label)
       label.SetTextFont(42)
       label.SetTextSize(category_label_font_size)
       label.SetNDC()

    return label

#def GetDiscriminantLabel(cat,prepostfitflag):
#    if "controlplots" in prepostfitflag:
#       return controlplots_variable_label[prepostfitflag]
#
#    if cat.find("DNN")>0:
#       return "DNN discriminant"
#
#    help_array = cat.split("_")
#    if "loBDT_MEM" in help_array or "hiBDT_MEM" in help_array:
#       return "MEM discriminant"
#
#    return "BDT discriminant"

def GetCatLabels(cat,prepostfitflag):

    txt_labels = CHANNELS_COSMETICS_DICT[cat]['labels']

    label1 = None
    label2 = None

    if len(txt_labels) >= 1: 
       label1 = ROOT.TLatex(ROOT.gStyle.GetPadLeftMargin()+0.05, 1.0-ROOT.gStyle.GetPadTopMargin()-0.09, txt_labels[0])
       label1.SetTextFont(42)
       label1.SetTextSize(category_label_font_size)
       label1.SetNDC()

    if len(txt_labels) >= 2: 
       label2 = ROOT.TLatex(ROOT.gStyle.GetPadLeftMargin()+0.05, 1.0-ROOT.gStyle.GetPadTopMargin()-0.145, txt_labels[1])
       label2.SetTextFont(42)
       label2.SetTextSize(category_label_font_size)
       label2.SetNDC()

    return label1, label2

def GetPlots(categories_processes_histos_dict,category,prepostfitflag,templateHisto=None, blind=False,ymax=-1):

    # create legend
    legend = GetLegend(prepostfitflag)

    # get dictionary process->histo dictionary for category
    processes_histos_dict = categories_processes_histos_dict[category]
    #print processes_histos_dict
    for process in processes_histos_dict:
      oldh=processes_histos_dict[process]
      processes_histos_dict[process]=rebinToTemplate(oldh,templateHisto)

    theTotalBackgroundHisto = processes_histos_dict["total_background"]

    for process in processes_histos_dict:
        processes_histos_dict[process] = stripEmptyBins(processes_histos_dict[process], theTotalBackgroundHisto)

    templateHisto = stripEmptyBins(templateHisto, theTotalBackgroundHisto)

    # fix data histo 
    processes_histos_dict["data"] = makeAsymErrorsForDataHisto(processes_histos_dict["data"])

    # Set data bin contents to zero if blinding is required
    if blind==True:
       processes_histos_dict["data"] = blindDataHisto(processes_histos_dict["data"], processes_histos_dict["total_signal"], processes_histos_dict["total_background"], SoBCut=0.01)

    # merge minor backgrounds
    MergeProcesses(processes_histos_dict,"wjets","zjets","vjets")
    MergeProcesses(processes_histos_dict,"ttbarW","ttbarZ","ttbarV")
    MergeProcesses(processes_histos_dict,"ttw","ttz","ttv")

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
    if prepostfitflag=="shapes_prefit" or "controlplots" in prepostfitflag:
        signal,sf = GetSignal(processes_histos_dict,background.Integral())
    
    # get data histogram
    data = GetDataHistogram(processes_histos_dict)

    # sort histograms in cateogory depending on their integral (first with largest integral, last with smallest) -> to get smallest contributions in the stack plot on top of it
#    sorted_processes_histos_list = sorted(processes_histos_dict.items(),key=lambda x: x[1].Integral(),reverse=False)
    sorted_processes_histos_list = GetSortedProcesses(processes_histos_dict)
    #print "sorted_processes_histos_list: ", sorted_processes_histos_list

    legdPrc_dict = {}

    # add background histogram to the stackplot
    for process in sorted_processes_histos_list:
        # avoid all total histograms, data and signal processes for background only
        if not "total" in process[0] and not "data" in process[0] and not "ttH" in process[0]:
           stack.Add(process[1])
           legdPrc_dict[process[0]] = [process[1], latex_dict[process[0]], "f"]

    # add signal histogram to the stack (in case of s+b fit)
    if prepostfitflag=="shapes_fit_s":
       for process in sorted_processes_histos_list:
           if process[0] == "total_signal":
              stack.Add(process[1])
              legdPrc_dict[process[0]] = [process[1], latex_dict[process[0]], "f"]

    elif prepostfitflag=="shapes_fit_b":
         legdPrc_dict["total_signal"] = [None,"",""] # add blank line

    elif (prepostfitflag=="shapes_prefit" or "controlplots" in prepostfitflag) and (signal != None):
         legdPrc_dict["total_signal"] = [signal, '{:1.0f}'.format(sf)+" #times "+latex_dict["ttH"], "l"]

    if data != None: legdPrc_dict['data'] = [data, "Data", "p"]

    # from total background or total background+signal prediction histogram in mlfit file, get the error band
    error_graph = GetErrorGraph(background)

    legdPrc_dict['Uncertainty'] = [error_graph, "Uncertainty", "f"]

    # we want the legend to have entries from top to bottom, per column
    # (ROOT default is from left to right, per row)
    legd_cols = GetLegendColumns()

    legd_cols[0] = [i_leg_col1 for i_leg_col1 in legd_cols[0] if i_leg_col1 in legdPrc_dict]
    legd_cols[1] = [i_leg_col2 for i_leg_col2 in legd_cols[1] if i_leg_col2 in legdPrc_dict]

    while len(legd_cols[0]) < len(legd_cols[1]): legd_cols[0] += [None]
    while len(legd_cols[1]) < len(legd_cols[0]): legd_cols[1] += [None]

    legd_list = [None]*(len(legd_cols[0])+len(legd_cols[1]))
    legd_list[ ::2] = legd_cols[0]
    legd_list[1::2] = legd_cols[1]

    for i_leg in legd_list:

        if i_leg == None: leg_data = [None, "", ""]
        else            : leg_data = legdPrc_dict[i_leg]

        legend.AddEntry(leg_data[0], leg_data[1], leg_data[2])

    # everything should fit in the plots
    if ymax < 0:
       ymax = error_graph.GetHistogram().GetMaximum() * abs(ymax)

#    stack.SetMaximum(ymax)
#    stack.SetMinimum(0.1) # suppress showing 0 on y axis

    ratio_error_graph = GetRatioErrorGraph(error_graph, templateHisto)

    # calculate the ratio between background only or background+signal prediction and data
    ratio_background_data = None
    if data != None:
       ratio_background_data = GetRatioGraph(data,background,templateHisto)

    return stack,ymax,legend,error_graph,data,ratio_background_data,signal,ratio_error_graph

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
  binEdgeArray=array.array("f",[])
  binContents=[]
  binErrors=[]
  for i in range(firstFilledBin,lastFilledBin+2,1):
    binEdgeArray.append(histo.GetBinLowEdge(i))
    binContents.append(histo.GetBinContent(i))
    binErrors.append(histo.GetBinError(i))
  # create new histo without empty bins at the ends                     
  histo_name = histo.GetName()
  histo.SetName(histo_name+'_old')

  newHisto=ROOT.TH1F(histo_name,histo.GetTitle(),len(binEdgeArray)-1,binEdgeArray)
  newNBins=newHisto.GetNbinsX()
  for i in range(newNBins):
    newHisto.SetBinContent(i+1,binContents[i])
    newHisto.SetBinError(i+1,binErrors[i])
  return newHisto  

def Plot(fitfile_,ch_cat_dict_,prepostfitflag,pubstatus="",blind=False,ymax=None):

    fitfile = ROOT.TFile.Open(fitfile_,"READ")
    if not fitfile: raise SystemExit(1)

    dir_ = prepostfitflag
    
    categories_processes_histos_dict = GetHistos(fitfile,dir_)
    #print " >> 1 categories_processes_histos_dict: ", categories_processes_histos_dict
    
    channels = GetChannels(GetDirectory(fitfile,dir_))
    #print " >> 2 channels: ", channels

    # list of y-axis ranges
    ymax_per_channel = {}
    if ymax is None:
        for channel in channels:

            # depending on MVA method, decide which y-axis SF to use
            catname = ch_cat_dict_[channel]["catname"]

            if catname not in CHANNELS_COSMETICS_DICT:
               raise RuntimeError('Plot -- invalid key for CHANNELS_COSMETICS_DICT: key="'+catname+'"')

            ymaxsf = CHANNELS_COSMETICS_DICT[catname].get('ymaxSF', 1.0)

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

           templateRootFile = ROOT.TFile.Open(templateRootFilePath, "READ")
           if not templateRootFile: raise SystemExit(1)

           templateHisto = templateRootFile.Get(templateHistoExpression.replace("$PROCESS","ttbarOther"))

           if VERBOSE:
              print ">>>>>>"
              print templateHistoExpression
              print "<<<<<<"
              print templateHisto

           stack,ymax_this_channel,legend,error_band,data,ratio_data_prediction,signal,ratio_error_band = GetPlots(categories_processes_histos_dict,channel,dir_,templateHisto,blind,ymax_per_channel[channel])

        # if y-axis range has not been provided, fill dict to return  
        if ymax_per_channel[channel] < 0:
           ymax_per_channel[channel] = ymax_this_channel

        titleX_label = CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]['titleX']

        logy = CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]].get('logY', False)

        if 'ymin' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]: stack.SetMinimum(CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]['ymin'])
        if 'ymax' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]: stack.SetMaximum(CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]['ymax'])

#        if "controlplots" in prepostfitflag:
#           logy = controlplots_logy[prepostfitflag]
#           stack.SetMinimum(controlplots_ymin[prepostfitflag])
#           stack.SetMaximum(controlplots_ymax[prepostfitflag])

        canvas.cd(1)

        stack.Draw("hist")

        # unfortunately this has to be done after a first Draw() because only then the axis objects are created ... ROOT ...
        SetUpStack(stack, prepostfitflag)

        if 'binLabelsX' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]:
            binLabelsX  =  CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]['binLabelsX']
            xax = stack.GetXaxis()
            xaN = len(binLabelsX)
            xax.Set(xaN, xax.GetBinLowEdge(1), xax.GetBinLowEdge(1 + xax.GetNbins()))
            xax.SetNdivisions(-414)
            for _ix in range(xaN): xax.SetBinLabel(_ix+1, binLabelsX[_ix])
            xax.SetLabelSize(xax.GetLabelSize() * (3./2.))

        if 'Ndivisions' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]:
            Ndivisions  =  CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]['Ndivisions']
            stack.GetXaxis().SetNdivisions(Ndivisions)

        if 'titleY' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]:
            titleY  =  CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]['titleY']
            stack.GetYaxis().SetTitle(titleY)

        stack.Draw("hist")

        if signal != None:
           signal.Draw("histsame][")

        if data != None:
           data.Draw("histPEX0same")

        error_band.Draw("2same")

        ROOT.gPad.RedrawAxis()
        
        legend.Draw("same")

        catlabel1, catlabel2 = GetCatLabels(ch_cat_dict_[channel]["catname"],prepostfitflag)

        if catlabel1 != None: catlabel1.Draw("same")
        if catlabel2 != None: catlabel2.Draw("same")

        fitlabel = GetFitLabel(ch_cat_dict_[channel]["catname"], prepostfitflag)
        if fitlabel != None:
           if catlabel2 == None: fitlabel.SetY(fitlabel.GetY() + 0.055)
           fitlabel.Draw("same")

        ROOT.gPad.SetLogy(logy)

        canvas.cd(2)
        #ratio_background_data.GetXaxis().SetRange(1,background_tot.GetMinimumBin()-1)
        if ratio_data_prediction != None:

           ratio_data_prediction.GetXaxis().SetTitle(titleX_label)

           if 'binLabelsX' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]:
               binLabelsX  =  CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]['binLabelsX']
               xax = ratio_data_prediction.GetXaxis()
               xaN = len(binLabelsX)
               xax.Set(xaN, xax.GetBinLowEdge(1), xax.GetBinLowEdge(1 + xax.GetNbins()))
               xax.SetNdivisions(-414)
               for _ix in range(xaN): xax.SetBinLabel(_ix+1, binLabelsX[_ix])
               xax.SetLabelSize(xax.GetLabelSize() * (3./2.))

           if 'Ndivisions' in CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]:
               ratio_data_prediction.GetXaxis().SetNdivisions(CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]['catname']]['Ndivisions'])

           ratio_data_prediction.Draw('APZE0')

        linemin = ratio_error_band.GetX()[0] - ratio_error_band.GetEXlow()[0]
        linemax = ratio_error_band.GetX()[ratio_error_band.GetN()-1] + ratio_error_band.GetEXhigh()[ratio_error_band.GetN()-1]
        ratio_line = ROOT.TLine(linemin,1,linemax,1)
        ratio_line.SetNDC(False)
        ratio_line.SetLineStyle(2)
        ratio_line.Draw("same")
        ratio_error_band.Draw("2same")

        canvas.cd(1)
        cms, info = GetCMSandInfoLabels(pubstatus)

        info.AddText(CHANNELS_COSMETICS_DICT[ch_cat_dict_[channel]["catname"]]['lumi'])

        cms .Draw("same")
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

        ### output name
        out_name = channel

        # remove repetitions of 'ttH_hbb_13TeV_' prefixes
        while out_name.startswith('ttH_hbb_13TeV_'):

          _tmp_idx = out_name.find('ttH_hbb_13TeV_', 1)

          if _tmp_idx != -1: out_name = out_name[_tmp_idx:]; del _tmp_idx;
          else: del _tmp_idx; break;
        ### -----------

        for _tmp_ext in OUTPUT_EXTENSIONS:
            canvas.Print(dir_+'_'+out_name+'.'+_tmp_ext)

        templateRootFile.Close()

    fitfile.Close()

    return ymax_per_channel

def ReadDatacard(datacard):

    if VERBOSE: print "reading datacard"

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

    categoriesFromLine = categoryLine.split(" ")[1:]

    if VERBOSE:
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

        ### determine path to input ROOT file with templates

        # if absolute path is written in the datacard, use that directly
        if os.path.isabs(shapeFile): histopath = shapeFile
        # if relative path is written in the datacard, derive abs path based on datacard location
        else: histopath = os.path.dirname(os.path.abspath(datacard))+'/'+shapeFile

        histopath = os.path.abspath(histopath)
        ### ------------------------------------------------

        if "$CHANNEL" in shapeProcessPart:
           # This is needed for unanonymized kit cards
           shapeProcessPart.replace("$CHANNEL",channel)

        category=shapeProcessPart.replace("$PROCESS","").replace("/","").replace("_finaldiscr_","")
        histoexpression=shapeProcessPart

      ### category name
      cat_name = channel

      # remove repetitions of 'ttH_hbb_13TeV_' prefixes
      while cat_name.startswith ('ttH_hbb_13TeV_'):
        _tmp_idx = cat_name.find('ttH_hbb_13TeV_', 1)

        if _tmp_idx != -1: cat_name = cat_name[_tmp_idx:]; del _tmp_idx;
        else: del _tmp_idx; break;
      ### -----------

      channel_category_dict[channel]={}
      channel_category_dict[channel]["catname"]         = cat_name # category
      channel_category_dict[channel]["histopath"]       = histopath
      channel_category_dict[channel]["histoexpression"] = histoexpression  

    if VERBOSE: print channel_category_dict

    return channel_category_dict

################################################################################# main function #################################################################################

def main(fitfile_, datacard_):

    #print datacard_
    ch_cat_dict = ReadDatacard(datacard_)

    pubstatus = 'preliminary'

    SetPadMargins()

#    Plot(fitfile_, ch_cat_dict, 'controlplots_btags', pubstatus=pubstatus, blind=False)
#    Plot(fitfile_, ch_cat_dict, 'controlplots_njets', pubstatus=pubstatus, blind=False)
#    Plot(fitfile_, ch_cat_dict, 'controlplots_var1' , pubstatus=pubstatus, blind=False)
#    Plot(fitfile_, ch_cat_dict, 'controlplots_var2' , pubstatus=pubstatus, blind=False)

#    maxy = Plot(fitfile_,ch_cat_dict,"shapes_prefit",pubstatus=pubstatus,blind=False)
#    Plot(fitfile_,ch_cat_dict,"shapes_fit_s",pubstatus=pubstatus,blind=False,ymax=maxy)
#    Plot(fitfile_,ch_cat_dict,"shapes_fit_b",pubstatus="",blind=False,ymax=maxy)

    Plot(fitfile_, ch_cat_dict, "shapes_prefit", pubstatus=pubstatus, blind=False)
    Plot(fitfile_, ch_cat_dict, "shapes_fit_s" , pubstatus=pubstatus, blind=False)
    Plot(fitfile_, ch_cat_dict, "shapes_fit_b" , pubstatus=""       , blind=False)

if __name__ == "__main__":

   input_fitDiagnostics = sys.argv[1]
   input_txtDatacard    = sys.argv[2]

   print '[input]', input_fitDiagnostics

   main(input_fitDiagnostics, input_txtDatacard)
