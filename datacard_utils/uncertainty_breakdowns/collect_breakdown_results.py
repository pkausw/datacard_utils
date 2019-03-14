import os
import sys
from glob import glob
import json
import ROOT
import fnmatch
from optparse import OptionParser
import imp
from copy import deepcopy

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.join(thisdir, "..", "base")
if not basedir in sys.path:
	sys.path.append(basedir)

from helperClass import helperClass
helper = helperClass()

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)


def run_sanity_checks(yvals):
	print yvals

def fill_dict_with_values(allvals, groupname, postfit, par):
	if not par in allvals:
		allvals[par] = {}

	if not groupname in allvals[par]:
		allvals[par][groupname] = {}

		if isinstance(postfit, tuple):
			allvals[par][groupname]["valup"] = postfit[1]
			allvals[par][groupname]["valdown"] = -postfit[2]
		else:
			allvals[par][groupname]["values"] = postfit
	else:
		print("ERROR: group '%s' already exists for parameter '%s'" % (groupname, par))

def collect_uncertainty_scans(wildcards, pars, filterstring, config, asymmetric = False):
	allvals = {}
	for wildcard in wildcards:
		for f in filterstring.split(":"):
			files = fnmatch.filter(glob(wildcard), f)
			print files
			for file in files:
				filename = os.path.basename(file)
				for par in pars:
					groupname = config.find_group(filename = filename, filterstring = f)
					if groupname == None: 
						print "error identifying group name! Skipping par %s in %s" % (par, file)
						continue
					if asymmetric:
						postfit = helper.load_asym_postfit(file, par)
					else:
						postfit = helper.load_postfit_uncert_from_variable(file, par)
					if not postfit:
						print "unable to load values for", par
						continue
					
					fill_dict_with_values(	allvals=allvals,par = par,groupname=groupname,postfit=postfit)

	for par in allvals:
		print "checking values for parameter", par
		run_sanity_checks(allvals[par])
	return allvals

def sign(x):
	return 1 if x >= 0 else -1

def substract_quadrature(val1, val2):
	return sign(val2)*(abs(val1**2 - val2**2))**(1./2)

def do_quadratic_substraction(return_dic, keyword, valkeyword = "values"):

	print "valkeyword:", valkeyword
	refval = return_dic[keyword][valkeyword]
	print refval
	if not "Stat" in return_dic:
		sys.exit("Could not find group 'Stat'!")
	#add new group for "KEYWORD-Stat"
	for group in return_dic:
		if group == keyword or group == "Stat": continue
		
		groupval = return_dic[group][valkeyword]
		newval = substract_quadrature(val1 = groupval, val2 = refval)
		print "\tgroup value(%s) =" % group, groupval
		print "\t%s value =" % keyword, refval
		print "\tnew value =", newval
		return_dic[group][valkeyword] = newval

def get_value_identifier(dic):
	if "valup" in dic:
		return ["valup", "valdown"]
	else:
		return ["values"]

def do_substraction(allvals, keyword):
	return_dic = {}
	if keyword in allvals:
		return_dic = deepcopy(allvals)
		print return_dic
		words = get_value_identifier(return_dic[keyword])
		for w in words:	do_quadratic_substraction(return_dic = return_dic,keyword = keyword, valkeyword = w)
	else:
		print "could not find '%s' group" % keyword
	return return_dic

def substract_stat_uncert(allvals):
	return_dic = {}
	for par in allvals:
		print "performing substraction for parameter", par
		temp = do_substraction(allvals = allvals[par], keyword = "Stat")
		if temp:
			return_dic[par] = temp
	return return_dic

def substract_from_total(allvals):
	return_dic = {}
	for par in allvals:
		print "performing substraction for parameter", par
		temp = do_substraction(allvals = allvals[par], keyword = "Total")
		if temp:
			newname = "Total-Stat"
			print "constructing", newname
			temp[newname] = deepcopy(temp["Total"])
			print temp[newname]
			identifyer = get_value_identifier(temp[newname])
			for valkey in identifyer:
				temp[newname][valkey] = substract_quadrature(val1 = temp[newname][valkey], val2 = temp["Stat"][valkey])
			return_dic[par] = temp
	return return_dic

def parse_arguments():
	usage = "usage: %prog [options] path/to/rootfiles\n"

	parser = OptionParser(usage=usage)

	parser.add_option(	"-o", "--outname", 
						help="name of output json file", 
						dest = "outname",
						default = "result_file.json"
					)
	parser.add_option(	"-p", "--parameters", "--params",
						help="collect values for these parameters. Can be either comma-separated list or used multiple times", 
						action="append", 
						dest = "params"
					)
	parser.add_option(	"-f", "--filter",
						help="use this filter to find correct values. Use ':' to separate multiple filters, e.g. '*bestfit*:*breakdown_*",
						dest = "filter",
					)
	parser.add_option(	"-c", "--config",
						help = "config with the function 'find_group' to find the group name and the color scheme",
						dest= "pathToConfig"
					)
	parser.add_option( "-a", "--asymmetric",
						help = "collect the asymmetric postfit uncertainties",
						dest = "asymmetric",
						action = "store_true",
						default = False
					)
	

	(options, args) = parser.parse_args()
	
	if options.filter == None:
		parser.error("Please specify filter to collect param scan results!")
	if not options.pathToConfig:
		parser.error("You have to specify a config file!")

	return options, args

def main(options, wildcards):

	outname 	= options.outname
	if not outname.endswith(".json"):
		outname += ".json"

	pars = []
	temp_pars = options.params
	if temp_pars is None:
		pars = ["r"]
	else:
		for p in temp_pars:
			pars += p.split(",")

	filterstring = options.filter
	config = None

	pathToConfig = options.pathToConfig
	
	if pathToConfig and os.path.exists(pathToConfig):
		config = imp.load_source('config', pathToConfig)
		print "loaded config from", pathToConfig

	

	allvals = {}
	substract_stat = {}
	
	allvals = collect_uncertainty_scans(wildcards = wildcards, pars = pars, 
											filterstring = filterstring, 
											config = config, 
											asymmetric = options.asymmetric)
	substract_stat = substract_from_total(allvals)
	
	print "creating file", outname
	helper.dump_json(outname = outname, allvals = allvals)
	if substract_stat:
		print "creating file", "substracted_"+outname
		helper.dump_json(outname = "substracted_"+outname, allvals = substract_stat)


if __name__ == '__main__':
	options, wildcards = parse_arguments()
	main(options = options, wildcards = wildcards)


