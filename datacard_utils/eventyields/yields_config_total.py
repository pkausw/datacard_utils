bkg_processes = [
    "ttlf",
    "ttcc",
    "ttbb",
    "singlet",
    "vjets",
    "ttbarV",
    "diboson",
    "tH",
    "tHW",
    "tHq",
    "multijet",
    "ttbarGamma",
    "TotalProcs",
]
total_bkg = "TotalBkg"
total_sig = "TotalSig"
data      = "data_obs"

njet_categories = ["SL 5j \\geq 4t"]
sub_categories = [ 
#                    "ttH", 
 #                   "ttmb", 
                   "Ratio Observable (ttH, ttmb)", 
                #    "tt2b", 
                #     "ttcc", 
                #     "ttlf", 
                    # "tHq", 
                    # "tHW" 
                ]

category_channel_map = {

    "SL 5j \\geq 4t Ratio Observable (ttH, ttmb)" : "total",
 
}

process_commands = {
    "ttlf"           : "\\ttlf",
    "ttcc"           : "\\ttC",
    "ttbb"           : "\\ttB",
    "singlet"        : "\\singlet",
    "vjets"          : "\\Vjets",
    "ttbarV"         : "\\ttV",
    "diboson"        : "\\diboson",
    "tH"             : "\\tH",
    total_bkg       : "Total\\;bkg.",
    total_sig       : "\\ttH",
    data       : "Data",
}

sub_category_commands = {
    "Ratio Observable (ttH, ttmb)"  : "Ratio Observable (\\ttH, \\ttborbb)",
    "ttlf" : "\\ttlf",
    "ttcc" : "\\ttcc",
    "ttmb" : "\\ttbb",
    "tt2b" : "\\ttTwob",
    "tHq"  : "\\tHq",
    "tHW"  : "\\tHW",
    #"3t"   : "\\dlFourThree",
    #"4tl"  : "\\dlFourFour BDT-low",
    #"4th"  : "\\dlFourFour BDT-high",
}
