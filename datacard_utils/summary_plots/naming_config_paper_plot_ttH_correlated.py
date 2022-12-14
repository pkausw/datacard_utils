##### PAPER summary PLOT mu ttH
# block 1: per channel, correlated backgrounds
# block 2: per year, correlated backgrounds
# block 3: combination

naming = {
    "combined_DLFHSL_all_years_packaged_mus": {
        "r_SL": "SL",
        "r_DL": "DL",
        "r_FH": "FH",
    },
    "combined_DLFHSL_all_years_packaged_mus_per_year": {
        "r_2016": "2016",
        "r_2017": "2017",
        "r_2018": "2018",
    },
    "combined_DLFHSL_all_years_separate_DNN_with_ratio": {
        "r": "Combined",
    },
}

order = [
    "FH",
    "SL",
    "DL",
    "SEPARATOR",
    "2016",
    "2017",
    "2018",
    "SEPARATOR",
    "Combined",
]

labels = {
    "FH" : "FH",
    "SL" : "SL",
    "DL" : "DL",
    "2016" : "2016",
    "2017" : "2017",
    "2018" : "2018",
    "Combined" : "Combined",
}

