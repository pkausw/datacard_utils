bkg_processes = [
    "ttlf",
    "ttcc",
    "ttbb",
    "singlet",
    "vjets",
    "ttbarV",
    "diboson",
]
bkg_processes += [x+"CR" for x in bkg_processes]
bkg_processes += ["dataCR"]
total_bkg = "total_background"
total_sig = "total_signal"
data      = "data"

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
    "ttcc"           : "\\ttcc",
    "ttbb"           : "\\ttbb",
    "singlet"        : "\\singlet",
    "vjets"          : "\\Vjets",
    "ttbarV"         : "\\ttV",
    "diboson"        : "\\diboson",

    "ttlfCR"           : "\\ttlf CR",
    "ttccCR"           : "\\ttcc CR",
    "ttbbCR"           : "\\ttbb CR",
    "singletCR"        : "\\singlet CR",
    "vjetsCR"          : "\\Vjets CR",
    "ttbarVCR"         : "\\ttV CR",
    "dibosonCR"        : "\\diboson CR",
    "dataCR"           : "Data CR"

    "total_background"       : "Total\\;bkg.",
    "total_signal"       : "\\ttH + \\tH",
    "data"       : "Data",
}

sub_category_commands = {
    "7j" : "$7j \\geq 3t$", 
    "8j" : "$8j \\geq 3t$",
    "9j" : "$\\geq 9j \\geq 3t$",
}