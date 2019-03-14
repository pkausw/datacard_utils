import ROOT
import fnmatch
from os import path as ospath
from sys import path as syspath
thisdir = ospath.dirname(ospath.realpath(__file__))
basedir = ospath.join(thisdir, "../base")
if not basedir in syspath:
	syspath.append(basedir)

# from helperClass import helperClass
# helper = helperClass()

clearnames = {
	"all"					: "Stat",
	"thy"				: "Theory",
	"bgn"					: "  Background normalisation",
	"exp"					: "Exp",
	"syst"			: "Systematic",
	"btag"				: "  B tagging",
	"jes"				: "  JES",
	"ps"				: "  PS",
	"QCD"				: "QCD",
	"autoMCStats"		: "MC uncertainty",
	"sig_thy"			: "Theory for Signal",
	"tthf_bgn"			: "  add. t#bar{t}+HF XS",
	"tthf_model"		: "  add. t#bar{t}+HF XS + PS",
}


def translate_names(breakdownname, filterstring):
	if "bestfit" in filterstring:
		return "Total"
	elif breakdownname in clearnames:
		breakdownname = clearnames[breakdownname]
	return breakdownname


def find_group(filename, filterstring):
	temp = filterstring
	if temp.startswith("*"):
		temp = temp[1:]
	if temp.endswith("*"):
		temp = temp[:-1]
	name = ".".join(filename.split(".")[:-1])
	parts = name.split(temp)
	print parts
	
	sub = parts[-1]
	groupname = translate_names(breakdownname = sub, filterstring= filterstring)
	if groupname:
		return groupname
	else:
		print("could not find number with filter string %s" % filterstring)

