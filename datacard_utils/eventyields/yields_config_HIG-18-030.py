bkg_processes = [
    "ttbarOther",
    "ttbarPlusCCbar",
    "ttbarPlusB",
    "ttbarPlus2B",
    "ttbarPlusBBbar",
    "singlet",
    "vjets",
    "ttbarV",
    "diboson",
]
total_bkg = "total_background"
total_sig = "total_signal"
data      = "data"

njet_categories = [ "SL 4j", "SL 5j", "SL 6j"]
sub_categories_sl = [ "ttH", "ttbb", "tt2b", "ttb", "ttcc", "ttlf" ]
sub_categories_dl = [ "3t", "4tl", "4th" ]

category_channel_map = {
    "SL 5j ttH"  : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttH",
    "SL 6j ttbb" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttbb",
    "SL 6j ttlf" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttlf",
    "SL 4j ttbb" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttbb",
    "SL 5j ttbb" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttbb",
    "SL 6j tt2b" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_tt2b",
    "SL 4j ttcc" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttcc",
    "SL 4j ttlf" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttlf",
    "SL 4j ttH"  : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttH",
    "SL 5j ttlf" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttlf",
    #"DL 4j 4th"  : "ch11",
    "SL 6j ttb"  : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttb",
    "SL 5j ttb"  : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttb",
    "SL 5j tt2b" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_tt2b",
    "SL 5j ttcc" : "ttH_hbb_13TeV_2017_sl_5j3b_DNN_ttcc",
    #"DL 4j 4tl"  : "ch16",
    "SL 4j ttb"  : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_ttb",
    "SL 4j tt2b" : "ttH_hbb_13TeV_2017_sl_4j3b_DNN_tt2b",
    "SL 6j ttH"  : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttH",
    "SL 6j ttcc" : "ttH_hbb_13TeV_2017_sl_6j3b_DNN_ttcc",
    #"DL 4j 3t"   : "ch21",
}

process_commands = {
    "ttbarOther"     : "\\ttlf",
    "ttbarPlusCCbar" : "\\ttcc",
    "ttbarPlusB"     : "\\ttb",
    "ttbarPlus2B"    : "\\tttwob",
    "ttbarPlusBBbar" : "\\ttbb",
    "singlet"        : "\\singlet",
    "vjets"          : "\\Vjets",
    "ttbarV"         : "\\ttV",
    "diboson"        : "\\diboson",
    "total_background"       : "Total\\;bkg.",
    "total_signal"       : "\\ttH",
    "data"       : "Data",
}

sub_category_commands = {
    "ttH"  : "\\ttH",
    "ttlf" : "\\ttlf",
    "ttcc" : "\\ttcc",
    "ttb"  : "\\ttb",
    "tt2b" : "\\tttwob",
    "ttbb" : "\\ttbb",
    #"3t"   : "\\dlFourThree",
    #"4tl"  : "\\dlFourFour BDT-low",
    #"4th"  : "\\dlFourFour BDT-high",
}