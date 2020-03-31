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

prefix = "unblinded_impacts"
prefix_2016 = "2016"
prefix_2017 = "2017"
prefix_2016p2017 = "2016 + 2017"
keyword_dict = {
	"ttH_hbb_13TeV_2016": {
		"label"		: prefix + "::2016_combination",
		"clearname" : prefix_2016 +" Combined",
	},
	"ttH_hbb_13TeV_2016_fh":{
		"label"		: prefix + "::fh_2016_combination",
		"clearname"	: prefix_2016 + " FH"
	},    
	"ttH_hbb_13TeV_2016p2017_dl": {
		"label"		: prefix + "::dl_2016p2017_combination",
		"clearname"	: prefix_2016p2017 + " DL"
	},
	"ttH_hbb_13TeV_2017": {
		"label"		: prefix + "::2017_combination",
		"clearname"	: prefix_2017 + " Combined"
	},    
	"ttH_hbb_13TeV_2017_fh": {
		"label"		: prefix + "::fh_2017_combination",
		"clearname"	: prefix_2017 + " FH"
	},    
	"ttH_hbb_13TeV_2017_sl_4j": {
		"label"		: prefix + "::sl_2017_4j",
		"clearname"	: prefix_2017 + " SL 4 Jets"
	},    
	"ttH_hbb_13TeV_2016_sl": {
		"label"		: prefix + "::sl_2016_combination",
		"clearname"	: prefix_2016 + " SL"
	},    
	"ttH_hbb_13TeV_2016p2017_fh": {
		"label"		: prefix + "::fh_2016p2017_combination",
		"clearname"	: prefix_2016p2017 + " FH"
	},    
	"ttH_hbb_13TeV_2017_dl": {
		"label"		: prefix + "::dl_2017_combination",
		"clearname"	: prefix_2017 + " DL"
	},    
	"ttH_hbb_13TeV_2017_fh_3b": {
		"label"		: prefix + "::fh_2017_3b",
		"clearname"	: prefix_2017 + " FH 3 b-tags"
	},    
	"ttH_hbb_13TeV_2017_sl_5j": {
		"label"		: prefix + "::sl_2017_5j",
		"clearname"	: prefix_2017 + " SL 5 Jets"
	},    
	"ttH_hbb_13TeV_2016_sldl": {
		"label"		: prefix + "::sldl_2016_combination",
		"clearname"	: prefix_2016 + " SL+DL"
	},    
	"ttH_hbb_13TeV_2016": {
		"label"		: prefix + "::2016_combination",
		"clearname"	: prefix_2016 + " Combined"
	},    
	"ttH_hbb_13TeV_2016p2017_sl": {
		"label"		: prefix + "::sl_2016p2017_combination",
		"clearname"	: prefix_2016p2017 + " SL"
	},    
	"ttH_hbb_13TeV_2017_dl_3j": {
		"label"		: prefix + "::dl_2017_3j",
		"clearname"	: prefix_2017 + " DL 3 Jets"
	},    
	"ttH_hbb_13TeV_2017_fh_4b": {
		"label"		: prefix + "::fh_2017_4b",
		"clearname"	: prefix_2017 + " FH 4 b-tags"
	},    
	"ttH_hbb_13TeV_2017_sl_6j": {
		"label"		: prefix + "::sl_2017_6j",
		"clearname"	: prefix_2017 + " SL 6 Jets"
	},    
	"ttH_hbb_13TeV_2016_dl": {
		"label"		: prefix + "::dl_2016_combination",
		"clearname"	: prefix_2016 + " DL"
	},    
	"ttH_hbb_13TeV_2016p2017": {
		"label"		: prefix + "::2016p2017_combination",
		"clearname"	: prefix_2016p2017 + " Combined"
	},    
	"ttH_hbb_13TeV_2016p2017_sldl": {
		"label"		: prefix + "::sldl_2016p2017_combination",
		"clearname"	: prefix_2016p2017 + " SL+DL"
	},    
	"ttH_hbb_13TeV_2017_dl_4j": {
		"label"		: prefix + "::dl_2017_4j",
		"clearname"	: prefix_2017 + " DL 4 Jets"
	},    
	"ttH_hbb_13TeV_2017_sl": {
		"label"		: prefix + "::sl_2017_combination",
		"clearname"	: prefix_2017 + " SL"
	},    
	"ttH_hbb_13TeV_2017_sldl": {
		"label"		: prefix + "::sldl_2017_combination",
		"clearname"	: prefix_2017 + " SL+DL"
	}
}

order = [
	"ttH_hbb_13TeV_2017",
	"ttH_hbb_13TeV_2017_sldl",
	"ttH_hbb_13TeV_2017_sl",    
	"ttH_hbb_13TeV_2017_dl",
	"ttH_hbb_13TeV_2017_fh",
	
	"ttH_hbb_13TeV_2017_sl_4j",
	"ttH_hbb_13TeV_2017_sl_5j",
	"ttH_hbb_13TeV_2017_sl_6j",    
	"ttH_hbb_13TeV_2017_dl_3j",
	"ttH_hbb_13TeV_2017_dl_4j",    
	"ttH_hbb_13TeV_2017_fh_3b",
	"ttH_hbb_13TeV_2017_fh_4b", 
	
	"ttH_hbb_13TeV_2016p2017",    
	"ttH_hbb_13TeV_2016p2017_sldl",    
	"ttH_hbb_13TeV_2016p2017_sl",   
	"ttH_hbb_13TeV_2016p2017_dl",
	"ttH_hbb_13TeV_2016p2017_fh",

	"ttH_hbb_13TeV_2016",
	"ttH_hbb_13TeV_2016_sldl",   
	"ttH_hbb_13TeV_2016_sl",
	"ttH_hbb_13TeV_2016_dl",    
	"ttH_hbb_13TeV_2016_fh",
	
	]

logfile = "json_creation.log"

texfile = "%s_impacts.tex"