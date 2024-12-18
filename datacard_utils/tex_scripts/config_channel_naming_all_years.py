
naming = {}
dnn_configs = {
    "DNN_ge5j_ge4t": "1 ANN",
    "separate_DNN": "2 ANNs"
}
ro_configs = {
    "": "w/ RO", 
    "_no_ratio": "w/o RO"}
subdict = {}
for dnn in dnn_configs:
    dnn_clearname = dnn_configs[dnn]
    for ro in ro_configs:
        ro_clearname = ro_configs[ro]

		key = "combined_DLFHSL_all_years_{}{}".format(dnn, ro)
		label = "{}::" + key.lower()
		clearname = "{}\\\\ FH+DL+SL all years {} {}".format(dnn_clearname, ro_clearname)
        subdict [key]= {
				"label": label,
				"clearname": clearname
			}

		key = "combined_DLSL_all_years_{}{}".format(dnn, ro)
		label = "{}::" + key.lower()
		clearname = "{}\\\\ DL+SL all years {} {}".format(dnn_clearname, ro_clearname)
        subdict [key]= {
				"label": label,
				"clearname": clearname
			}

		key = "combined_SLFH_all_years_{}{}".format(dnn, ro)
		label = "{}::" + key.lower()
		clearname = "{}\\\\ SL+FH all years {} {}".format(dnn_clearname, ro_clearname)
        subdict [key]= {
				"label": label,
				"clearname": clearname
			}

keyword_dict.update(subdict)
keyword_dict.update({            
    "combined_DL_all_years_DNN": {
		"label": "{}::" + "combined_DL_all_years_DNN".lower(),
		"clearname": "{}\\\\ DL all years"
	},

    "combined_FH_all_years_DNN": {
		"label": "{}::" + "combined_FH_all_years_DNN".lower(),
		"clearname": "{}\\\\ FH all years"
		},
	})

dnn_configs = {
    "DNN_ge5j_ge4t": ">=5j, >=4t",
    "DNN_ge6j_ge4t": ">=6j, >=4t",
    "DNN_5j_ge4t": "5j, >=4t",
    "separate_DNN": "2 ANNs"
}
subdict = {}
for dnn in dnn_configs:
    dnn_clearname = dnn_configs[dnn]
    for ro in ro_configs:
        ro_clearname = ro_configs[ro]
        key = "combined_SL_all_years_{}{}".format(dnn, ro)
		label = "{}::" + key.lower()
		clearname = "{}\\\\ SL all years {} {}".format(dnn_clearname, ro_clearname)
        subdict [key]= {
				"label": label,
				"clearname": clearname
			}
naming.update(subdict)

keyword_dict = {

	"combined_DLFHSL_all_years": {
		"label"		: "{}::dlslfh_all_years_combination",
		"clearname"	: "{}\\\\ FH (DNN)+ DL (DNN) + SL (DNN) Combined"
	},
	"combined_DLFHSL_all_years": {
		"label"		: "{}::dlslfh_all_years_combination",
		"clearname"	: "{}\\\\ FH (DNN)+ DL (DNN) + SL (DNN) Combined"
	},
    "combined_DLSL_all_years": {
		"label"		: "{}::sldl_all_years_combination",
		"clearname"	: "{} SL+DL"
	},
    "combined_DLSL_all_years": {
		"label"		: "{}::sldl_all_years_combination",
		"clearname"	: "{} SL+DL"
	},
       "combined_DLFH_all_years": {
                "label"         : "{}::dlfh_all_years_combination",
                "clearname"     : "{} DL+FH"
        },
        "combined_SLFH_all_years": {
                "label"         : "{}::slfh_all_years_combination",
                "clearname"     : "{} SL+FH"
        },
	"combined_FH_all_years_DNN": {
		"label"		: "{}::fh_all_years_combination",
		"clearname"	: "{} FH"
	},    
	"combined_DL_all_years_DNN": {
		"label"		: "{}::dl_all_years_combination",
		"clearname"	: "{} DL"
	},    
    "combined_SL_all_years_DNN": {
		"label"		: "{}::sl_all_years_combination",
		"clearname"	: "{} SL"
	},
    "ttbb_CR_all_years": {
		"label"		: "{}::ttbb_CR_all_years",
		"clearname"	: "{} ttbb CR Split"
	},

    "ttH_hbb_13TeV_all_years_dl_4j3b_DNN": {
		"label"		: "{}::dl_4j3b_DNN_all_years_combination",
		"clearname"	: "{} DL $\\geq 4$ jets, 3 tags"
	}, 
    "ttH_hbb_13TeV_all_years_dl_4j4b_DNN": {
		"label"		: "{}::dl_4j4b_DNN_all_years_combination",
		"clearname"	: "{} DL $\\geq 4$ jets, $\\geq 4$ tags"
	},    

    "combined_SL_all_years_DNN_ge4j_3t": {
		"label"		: "{}::sl_ge4j_3t_all_years_combination",
		"clearname"	: "{} SL $\\geq 4$ jets, 3 tags"
	}, 
    "combined_SL_all_years_DNN_ge4j_ge4t": {
		"label"		: "{}::sl_ge4j_ge4t_all_years_combination",
		"clearname"	: "{} SL $\\geq 4$ jets, $\\geq 4$ tags"
	},   

    "fh_j7_t4_DNN_Node0": {
		"label"		: "{}::fh_j7_t4_DNN_Node0_all_years",
		"clearname"	: "{} FH 7 jets, $\\geq 4$ tags"
	},
    "fh_j8_t4_DNN_Node0": {
		"label"		: "{}::fh_j8_t4_DNN_Node0_all_years",
		"clearname"	: "{} FH 8 jets, $\\geq 4$ tags"
	},
    "fh_j9_t4_DNN_Node0": {
		"label"		: "{}::fh_j9_t4_DNN_Node0_all_years",
		"clearname"	: "{} FH $\\geq 9$ jets, $\\geq 4$ tags"
	},


	
    "combined_DLFHSL_all_years_HT_jets":{
		"label"		: "{}::dlslfh_all_years_HT_jets",
		"clearname"	: "{} DL+SL+FH HT(jets)"
	},
    "combined_DLSL_all_years_HT_jets":{
		"label"		: "{}::dlsl_all_years_HT_jets",
		"clearname"	: "{} DL+SL HT(jets)"
	},
    "combined_DL_all_years_HT_jets.tex":{
		"label"		: "{}::dl_all_years_HT_jets",
		"clearname"	: "{} DL HT(jets)"
	},
    "combined_SL_all_years_HT_jets.tex":{
		"label"		: "{}::sl_all_years_HT_jets",
		"clearname"	: "{} SL HT(jets)"
	},
    "combined_FH_all_years_HT_jets.tex":{
		"label"		: "{}::fh_all_years_HT_jets",
		"clearname"	: "{} FH HT(jets)"
	},

    "fh_j7_t4_ht30": {
		"label"		: "{}::fh_j7_t4_ht30_all_years",
		"clearname"	: "{} FH 7 jets, $\\geq 4$ tags HT(jets)"
	},
    "fh_j8_t4_ht30": {
		"label"		: "{}::fh_j8_t4_ht30_all_years",
		"clearname"	: "{} FH 8 jets, $\\geq 4$ tags HT(jets)"
	},
    "fh_j9_t4_ht30": {
		"label"		: "{}::fh_j9_t4_ht30_all_years",
		"clearname"	: "{} FH $\\geq 9$ jets, $\\geq 4$ tags HT(jets)"
	},

    "ttH_hbb_13TeV_all_years_dl_3j2b_HT_jets": {
		"label"		: "{}::dl_3j2b_HT_jets_all_years",
		"clearname"	: "{} DL 3 jets, 2 tags"
	}, 
    "ttH_hbb_13TeV_all_years_dl_3j3b_HT_jets": {
		"label"		: "{}::dl_3j3b_HT_jets_all_years",
		"clearname"	: "{} DL 3 jets, 3 tags"
	}, 
    "ttH_hbb_13TeV_all_years_dl_4j2b_HT_jets": {
		"label"		: "{}::dl_4j2b_HT_jets_all_years",
		"clearname"	: "{} DL $\\geq 4$ jets, 2 tags"
	}, 
    "ttH_hbb_13TeV_all_years_dl_4j3b_HT_jets": {
		"label"		: "{}::dl_4j3b_HT_jets_all_years",
		"clearname"	: "{} DL $\\geq 4$ jets, 3 tags"
	}, 
    "ttH_hbb_13TeV_all_years_dl_4j4b_HT_jets": {
		"label"		: "{}::dl_4j4b_HT_jets_all_years",
		"clearname"	: "{} DL $\\geq 4$ jets, $\\geq 4$ tags"
	}, 

}



order = [
    #"combined_full_all_years",
    #"combined_full_all_years_packaged_mus",
    #"combined_full_all_years_scalable",
    #"combined_full_all_years_scalable_packaged_mus",

	"combined_DLFHSL_all_years",
    "combined_DLSL_all_years",
	"combined_DLFH_all_years",
	"combined_SLFH_all_years",
	"combined_FH_all_years_DNN",    
	"combined_DL_all_years_DNN",    
    "combined_SL_all_years_DNN",
    "ttbb_CR_all_years",

    "ttH_hbb_13TeV_all_years_dl_4j3b_DNN", 
    "ttH_hbb_13TeV_all_years_dl_4j4b_DNN",    

    "combined_SL_all_years_DNN_ge4j_3t", 
    "combined_SL_all_years_DNN_ge4j_ge4t",   

    "fh_j7_t4_DNN_Node0",
    "fh_j8_t4_DNN_Node0",
    "fh_j9_t4_DNN_Node0",


	
    "combined_DLFHSL_all_years_HT_jets",
    "combined_DLSL_all_years_HT_jets",
    "combined_DL_all_years_HT_jets.tex",
    "combined_SL_all_years_HT_jets.tex",
    "combined_FH_all_years_HT_jets.tex",

    "fh_j7_t4_ht30",
    "fh_j8_t4_ht30",
    "fh_j9_t4_ht30",

    "ttH_hbb_13TeV_all_years_dl_3j2b_HT_jets", 
    "ttH_hbb_13TeV_all_years_dl_3j3b_HT_jets", 
    "ttH_hbb_13TeV_all_years_dl_4j2b_HT_jets", 
    "ttH_hbb_13TeV_all_years_dl_4j3b_HT_jets", 
    "ttH_hbb_13TeV_all_years_dl_4j4b_HT_jets", 

]
