bkg_processes = [
    "ttlf",
    "ttcc",
    "ttbb",
    "singlet",
#    "vjets",
    "ttbarV",
#    "diboson",
    "tH",
    "multijet"
]
#bkg_processes += [x+"CR" for x in bkg_processes]
#bkg_processes += ["dataCR"]
total_bkg = "TotalBkg"
total_sig = "TotalSig"
data      = "data_obs"

njet_categories = [ "FH"]
sub_categories = [  
                    "7j", 
                    "8j",
                    "9j",
                ]

category_channel_map = {
    "FH 7j"            : "fh_j7_t4_DNN_Node0",
    "FH 8j"            : "fh_j8_t4_DNN_Node0",
    "FH 9j"            : "fh_j9_t4_DNN_Node0",
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

#    "ttlf_CR"           : "\\ttlf CR",
#    "ttcc_CR"           : "\\ttcc CR",
#    "ttbb_CR"           : "\\ttbb CR",
#    "singlet_CR"        : "\\singlet CR",
#    "vjets_CR"          : "\\Vjets CR",
#    "ttbarV_CR"         : "\\ttV CR",
#    "diboson_CR"        : "\\diboson CR",
#    "data_CR"           : "Data CR",
    "multijet"         : "Multijet Bkg",
    total_bkg       : "Total\\;bkg.",
    total_sig       : "\\ttH",
    data       : "Data",
}

sub_category_commands = {
    "7j" : "$7j \\geq 3t$", 
    "8j" : "$8j \\geq 3t$",
    "9j" : "$\\geq 9j \\geq 3t$",
}
