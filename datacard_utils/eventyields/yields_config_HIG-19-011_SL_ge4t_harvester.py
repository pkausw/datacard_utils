bkg_processes = [
    "ttlf",
    "ttcc",
    "ttbb",
    "singlet",
    "vjets",
    "ttbarV",
    "diboson",
    "tH",
]
total_bkg = "TotalBkg"
total_sig = "TotalSig"
data      = "data"

njet_categories = ["SL \\geq 4j \\geq 4t"]
sub_categories = [ 
#                    "ttH", 
 #                   "ttmb", 
                   "Ratio Observable (ttH, ttmb)", 
                   "tt2b", 
                    "ttcc", 
                    "ttlf", 
                    "tHq", 
                    "tHW" 
                ]

category_channel_map = {
    "SL \\geq 4j 3t ttH" : "ljets_ge4j_3t_ttH_node",
    "SL \\geq 4j 3t tHq" : "ljets_ge4j_3t_tHq_node",
    "SL \\geq 4j 3t tHW" : "ljets_ge4j_3t_tHW_node",
    "SL \\geq 4j 3t ttmb" : "ljets_ge4j_3t_ttmb_node",
    "SL \\geq 4j 3t tt2b" : "ljets_ge4j_3t_tt2b_node",
    "SL \\geq 4j 3t ttcc" : "ljets_ge4j_3t_ttcc_node",
    "SL \\geq 4j 3t ttlf" : "ljets_ge4j_3t_ttlf_node",

    "SL \\geq 4j \\geq 4t Ratio Observable (ttH, ttmb)" : "ljets_ge4j_ge4t_ttH_ttmb_ratioObservable",
    "SL \\geq 4j \\geq 4t tHq" : "ljets_ge4j_ge4t_tHq_node",
    "SL \\geq 4j \\geq 4t tHW" : "ljets_ge4j_ge4t_tHW_node",
    "SL \\geq 4j \\geq 4t ttmb" : "ljets_ge4j_ge4t_ttmb_node",
    "SL \\geq 4j \\geq 4t tt2b" : "ljets_ge4j_ge4t_tt2b_node",
    "SL \\geq 4j \\geq 4t ttcc" : "ljets_ge4j_ge4t_ttcc_node",
    "SL \\geq 4j \\geq 4t ttlf" : "ljets_ge4j_ge4t_ttlf_node",

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
    "Ratio Observable (ttH, ttmb)"  : "Ratio Observable (\\ttH, \\ttborbb",
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
