import ROOT
import fnmatch
from os import path as ospath
from sys import path as syspath
from collections import OrderedDict
thisdir = ospath.dirname(ospath.realpath(__file__))
basedir = ospath.join(thisdir, "../base")
if not basedir in syspath:
	syspath.append(basedir)

# from helperClass import helperClass
# helper = helperClass()

clearnames = OrderedDict([
        ("syst"                 , "Systematic"),
        ("exp"                                  , "  Exp"),
        ("btag"                         , "    B tagging"),
        ("jes"                          , "    JES"),
        ("lumi"                          , "    Lumi"),
        ("thy"                          , "  Theory"),
        ("sig_thy"                      , "    Theory for Signal"),
        ("bkg_thy"                      , "    Theory for Background"),
        ("bgn"                                  , "    Background normalisation"),
        ("tthf_model"           , "    add. t#bar{t}+HF XS + PS"),
        ("tthf_bgn"                     , "      add. t#bar{t}+HF XS"),
        ("ps"                           , "      PS"),
        ("ddQCD"                          , "  QCD"),
        ("autoMCStats"          , "MC uncertainty"),
        ("all"                                  , "Stat"),
		("bgnorm_ttX"                                  , "    freely-floating ttX normalisation - substract from Stat"),
		("bgnorm"                                  , "    freely-floating normalisation parameters - substract from Stat"),
		("bgnorm_ttbb_part_all"                                  , "    freely-floating ttbb normalisation - substract from Stat"),
		("bgnorm_ttcc_part_all"                                  , "    freely-floating ttcc normalisation - substract from Stat"),
		("bgnorm_ddQCD"                                  , "    freely-floating ddQCD normalisation - substract from Stat"),
])

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
	print (parts)
	
	sub = parts[-1]
	groupname = translate_names(breakdownname = sub, filterstring= filterstring)
	if groupname:
		return groupname
	else:
		print("could not find number with filter string %s" % filterstring)

