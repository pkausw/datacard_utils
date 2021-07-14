bkg_processes = [
    "ttlf",
    "ttcc",
    "ttbb",
    "singlet",
   "vjets",
    "ttbarV",
    "ttbarGamma",
   "diboson",
    "tH",
]
total_bkg = "TotalBkg"
total_sig = "TotalSig"
data      = "data_obs"

njet_categories = [ "DL"]
sub_categories = [  "3j 2t", 
                    "3j 3t", 
                    "4j 2t", 
                ]

category_channel_map = {
    "DL 3j 2t" : "ttH_hbb_13TeV_dl_3j2b_ttHbb",
    "DL 3j 3t" : "ttH_hbb_13TeV_dl_3j3b_ttHbb",
    "DL 4j 2t" : "ttH_hbb_13TeV_dl_4j2b_ttHbb",
    "DL 4j \\geq 3t ttHbb" : "ttH_hbb_13TeV_dl_4j3b_DNN_ttHbb",
    "DL 4j \\geq 3t ttbb" : "ttH_hbb_13TeV_dl_4j3b_DNN_ttbb",
    "DL 4j \\geq 3t ttcc" : "ttH_hbb_13TeV_dl_4j3b_DNN_ttcc",
    "DL 4j \\geq 3t ttlf" : "ttH_hbb_13TeV_dl_4j3b_DNN_ttlf",
}

process_commands = {
    "ttlf"           : "\\ttlf",
    "ttcc"           : "\\ttC",
    "ttbb"           : "\\ttB",
    "singlet"        : "\\singlet",
    "vjets"          : "\\Vjets",
    "ttbarV"         : "\\ttV",
    "diboson"        : "\\diboson",
    "tH"	     : "\\tH",
    "ttbarGamma"     : "\\ttGamma",
    total_bkg       : "Total\\;bkg.",
    total_sig       : "\\ttH",
    data       : "Data",
}

sub_category_commands = {
    "4j \\geq 3t ttHbb" : "$4j \\geq 3t$ \\ttH", 
    "4j \\geq 3t ttbb" : "$4j \\geq 3t$ \\ttB",
    "4j \\geq 3t ttcc" : "$4j \\geq 3t$ \\ttC",
    "4j \\geq 3t ttlf" : "$4j \\geq 3t$ \\ttlf",
    #"3t"   : "\\dlFourThree",
    #"4tl"  : "\\dlFourFour BDT-low",
    #"4th"  : "\\dlFourFour BDT-high",
}
