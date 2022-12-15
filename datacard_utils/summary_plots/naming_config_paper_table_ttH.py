##### PAPER summary TABLE mu ttH
# block 1: per channel, uncorrelated backgrounds
# block 2: per channel, correlated backgrounds
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
    "combined_DLFHSL_all_years_packaged_mus": {
        "r_SL": "SL_correlated",
        "r_DL": "DL_correlated",
        "r_FH": "FH_correlated",
    },
    "combined_DLFHSL_all_years_separate_DNN_with_ratio": {
        "r": "Combined",
    },
}

order = [
    "SEPARATOR:Individual fits",
    "FH",
    "SL",
    "DL",
    "SEPARATOR:Fit with correlated uncertainties",
    "FH_correlated",
    "SL_correlated",
    "DL_correlated",
    "SEPARATOR",
    "Combined",
]

labels = {
    "FH" : "FH$^{+}$",
    "SL" : "SL",
    "DL" : "DL",
    "FH_correlated" : "FH",
    "SL_correlated" : "SL",
    "DL_correlated" : "DL",
    "Combined" : "Combined",
}

