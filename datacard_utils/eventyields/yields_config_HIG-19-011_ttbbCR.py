bkg_processes = [
    "ttlf",
    "ttcc",
    "ttbb",
    "singlet",
    "vjets",
    "ttbarV",
    "diboson",
    "tH",
    "ttbarGamma",
    "VH_hbb"
]
total_bkg = "total_background"
total_sig = "total_signal"
data      = "data"

njet_categories = [ "ttbbCR"]
sub_categories = [  
                    "ttbb CR"
                ]

category_channel_map = {
    "ttbbCR ttbb CR" : "ttbbCR"
}

process_commands = {
    "ttlf"           : "\\ttlf",
    "ttcc"           : "\\ttcc",
    "ttbb"           : "\\ttbb",
    "singlet"        : "\\singlet",
    "vjets"          : "\\Vjets",
    "ttbarV"         : "\\ttV",
    "diboson"        : "\\diboson",
    "tH"             : "\\tH",
    "ttbarGamma"     : "\\ttGamma",
    "VH_hbb"         : "\\VHbb",
    "total_background"       : "Total\\;bkg.",
    "total_signal"       : "\\ttH",
    "data"       : "Data",
}

sub_category_commands = {
    "ttbb CR" : "\\ttbb CR"
}
