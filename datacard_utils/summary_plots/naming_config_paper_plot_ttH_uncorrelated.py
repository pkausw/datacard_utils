##### PAPER summary PLOT mu ttH
# block 1: per channel, uncorrelated backgrounds
# block 2: per year, uncorrelated backgrounds
# block 3: combination

naming = {
    "combined_ttRateFactors_FH_all_years_DNN": {
        "r": "FH",
    },    
    "combined_SL_all_years_separate_DNN_with_ratio": {
        "r": "SL",
    },
    "combined_DL_all_years_DNN_with_ratio": {
        "r": "DL",
    },    
    "combined_DLFHSL_2016_separate_DNN_with_ratio": {
        "r": "2016",
    },
    "combined_DLFHSL_2017_separate_DNN_with_ratio": {
        "r": "2017",
    },
    "combined_DLFHSL_2018_separate_DNN_with_ratio": {
        "r": "2018",
    },
    "combined_DLFHSL_all_years_separate_DNN_with_ratio": {
        "r": "Combined",
    },
}

order = [
    "FH",
    "SEPARATOR2",
    "SL",
    "SEPARATOR2",
    "DL",
    "SEPARATOR1",
    "2016",
    "SEPARATOR2",
    "2017",
    "SEPARATOR2",
    "2018",
    "SEPARATOR1",
    "Combined",
]

labels = {
    "FH" : "FH^{+}",
    "SL" : "SL",
    "DL" : "DL",
    "2016" : "2016",
    "2017" : "2017",
    "2018" : "2018",
    "Combined" : "Combined",
}

