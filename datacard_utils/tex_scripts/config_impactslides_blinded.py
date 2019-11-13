slide_template = """\\subsection*{%(CLEARNAME)s}
\\begin{frame}
\label{%(LABEL)s}
	\\begin{center}
		\\begin{Huge}
			%(CLEARNAME)s
		\end{Huge}
		
		\\ Missing inputs: \\texttt{
			%(MISSING_VARS)s
		}
	\end{center}
\end{frame}
\input{\pathToImpactTex/%(IMPACTSLIDETEX)s}
	"""

prefix = "blinded_impacts"
prefix_2017 = "2017"
keyword_dict = {
	"combined_DLFHSL_2017_baseline_v01": {
		"label"		: prefix + "::2017_combination",
		"clearname"	: prefix_2017 + "\\\\ FH (DNN)+ DL (MEM) + SL (DNN) Combined"
	},    
	"combined_FH_2017_DNN": {
		"label"		: prefix + "::fh_2017_combination",
		"clearname"	: prefix_2017 + " FH"
	},    
	"combined_DL_2017_MEM": {
		"label"		: prefix + "::dl_2017_combination",
		"clearname"	: prefix_2017 + " DL"
	},    
	"combined_SL_2017_DNN": {
		"label"		: prefix + "::sl_2017_combination",
		"clearname"	: prefix_2017 + " SL"
	},    
	"combined_DLSL_2017_baseline_v01": {
		"label"		: prefix + "::sldl_2017_combination",
		"clearname"	: prefix_2017 + " SL+DL"
	}
}

#order = [
#	"ttH_hbb_13TeV_2017",
#	"ttH_hbb_13TeV_2017_sldl",
#	"ttH_hbb_13TeV_2017_sl",    
#	"ttH_hbb_13TeV_2017_dl",
#	"ttH_hbb_13TeV_2017_fh",
	
	#"ttH_hbb_13TeV_2017_sl_4j",
	#"ttH_hbb_13TeV_2017_sl_5j",
	#"ttH_hbb_13TeV_2017_sl_6j",    
	#"ttH_hbb_13TeV_2017_dl_3j",
	#"ttH_hbb_13TeV_2017_dl_4j",    
	#"ttH_hbb_13TeV_2017_fh_3b",
	#"ttH_hbb_13TeV_2017_fh_4b", 
	
	#"ttH_hbb_13TeV_2016p2017",    
	#"ttH_hbb_13TeV_2016p2017_sldl",    
	#"ttH_hbb_13TeV_2016p2017_sl",   
	#"ttH_hbb_13TeV_2016p2017_dl",
	#"ttH_hbb_13TeV_2016p2017_fh",

	#"ttH_hbb_13TeV_2016",
	#"ttH_hbb_13TeV_2016_sldl",   
	#"ttH_hbb_13TeV_2016_sl",
	#"ttH_hbb_13TeV_2016_dl",    
	#"ttH_hbb_13TeV_2016_fh",
	
#	]
order = keyword_dict.keys()

logfile = "json_creation.log"

texfile = "%s_impacts.tex"
