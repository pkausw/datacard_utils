from ROOT import TFile
import os
import sys
import glob
import subprocess
import json
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'base'))
scriptDir = os.path.join(os.path.dirname(sys.path[0]),'scripts')
from batchConfig import *
batch_config = batchConfig()
#========input variables================================================

listOfDatacards = None
listOfResubFolders = None
additionalSubmitCmds 	= None
useBatch = True

if len(sys.argv) == 2:
	pathToJson = sys.argv[1]
	pathToJson = os.path.abspath(pathToJson)
	if os.path.exists(pathToJson) and pathToJson.endswith(".json"):
		print "loading impact submit infos from", pathToJson
		with open(pathToJson) as f:
			dic = json.load(f)
		listOfDatacards = dic["datacards"]
		listOfResubFolders = dic["impact_folders"]
		additionalSubmitCmds = dic["commands"]
	else:
		sys.exit("Input has to be a .json file!")
else:
	resubWildcard 		= sys.argv[1]
	datacardWildcard 	= sys.argv[2]
	additionalSubmitCmds 	= None
	if len(sys.argv) > 3:
		additionalSubmitCmds= sys.argv[3:]

	listOfDatacards = glob.glob(datacardWildcard)
	listOfResubFolders = glob.glob(resubWildcard)


# pathToConfig = scriptDir + "/batch_config.py"
# pathToConfig = os.path.abspath(pathToConfig)
# print "loading config from", pathToConfig

# config = imp.load_source('config', pathToConfig)

#=======================================================================

#========functions======================================================

def get_number_of_cmds():
	counter = 0
	scriptList = None
	if batch_config.jobmode == "condor":
		scriptList = glob.glob("condor*.sh")
		if len(scriptList) > 0:
			script = scriptList[0]
			with open(script, "r") as f:
				lines = f.read().splitlines()
				# print lines
				for l in lines:
					words = l.split()
					if len(words) == 0: continue
					if words[0] == "combine": counter += 1
	else:
		scriptList = glob.glob("*.sh")
		counter = len(scriptList)

	return counter, scriptList

def load_script_lines(scriptList):
	"""
	creates list with following structure:
	0: script that is to be submitted. If you're using :
			- HTCondor: 'scriptname NUMBEROFCOMMAND'
			- else:		path/to/script
	1: combine command saved in the script
	"""
	lines = []
	if batch_config.jobmode == "condor":
		script = scriptList[0]
		counter = 0
		with open(script) as f:
			tmplines = f.read().splitlines()
		for l in tmplines:
			l = l.strip()
			if l.startswith("combine"):
				tosub = "'%s %s'" % (script, counter)
				lines.append([tosub, l])
				counter += 1
	else:			
		for script in scriptList:
			script = os.path.abspath(script)
			with open(script) as s:
				tmplines = s.read().splitlines()
			lines.append()
			if any(x in lines[-1] for x in keywords):
				scripts.append(script)
				break
	return lines

def find_missing_scripts(rootfiles, scriptList):
	keywords = []
	scripts = []
	lines = load_script_lines(scriptList)
	valid_output_keys = []
	for path in rootfiles:
		infile = TFile(path)
		parts = path.replace("higgsCombine", "").split(".")
		if (infile.IsOpen() and not infile.IsZombie() and not infile.TestBit(TFile.kRecovered)):
			valid_output_keys.append(parts[0])
			# keywords.append(parts[0])
	
	if len(valid_output_keys) == len(rootfiles) and len(valid_output_keys) == len(lines):
		print "all files are fine!"
	else:
		if not len(valid_output_keys) == len(rootfiles):
			print "WARNING: encountered corrupted root files, will resubmit!"
		if not len(valid_output_keys) == len(lines):
			print "WARNING: output for some commands is missing, will resubmit!"
		# print lines
		scripts += [x[0] for x in lines if not any(key in x[1] for key in valid_output_keys)]
	# print "commands without root files:"
	# print scripts_without_rootfiles
	# scripts += scripts_without_rootfiles
	# print keywords
	# if len(keywords) > 0:
	# 	scripts += [x[0] for x in lines if any(key in x[1] for key in keywords)]
	return scripts

def check_param_fits(rootfiles, scriptList):
	keywords = []
	scripts = []
	for path in rootfiles:
		infile = TFile(path)
		if not (infile.IsOpen() and not infile.IsZombie() and not infile.TestBit(TFile.kRecovered)):
			print "looking for script for file", path
			parts = path.replace("higgsCombine", "").split(".")
			keywords.append(parts[0])
	print keywords
	if len(keywords) > 0:
		if batch_config.jobmode == "condor":
			script = scriptList[0]
			lines = []
			counter = 0
			with open(script) as f:
				lines = f.read().splitlines()
			for l in lines:
				l = l.strip()
				if l.startswith("combine"):
					if any(x in l for x in keywords):
						scripts.append("'{0} {1}'".format(script, counter))
					counter += 1
		else:			
			for script in scriptList:
				script = os.path.abspath(script)
				s = open(script)
				lines = s.read().splitlines()
				s.close()
				if any(x in lines[-1] for x in keywords):
					scripts.append(script)
					break
	return scripts


def check_for_resubmit(folder):
	if not os.path.exists(folder):
		return True

	print "cd into", folder
	os.chdir(folder)
	toResub = []
	if not os.path.exists("commands.txt"):
		print "unable to find commands.txt in", folder
		return True
	ncmds, scriptList = get_number_of_cmds()

	with open("commands.txt") as infile:
		lines = infile.read().splitlines()
	if not ncmds == 0:
		rootfiles = glob.glob("higgsCombine_paramFit*.root")
		print "# rootfiles:", len(rootfiles)
		print "# scripts:", ncmds
		initFitList = glob.glob("higgsCombine_initialFit_*.root")
		redoInitFit = False
		if initFitList:
			initFitFile = initFitList[0]
			infile = TFile(initFitFile)
			if not (infile.IsOpen() and not infile.IsZombie() and not infile.TestBit(TFile.kRecovered)):
				redoInitFit = True
			else:
				print "init file is working"
		else:
			print "could not find initial fit file!"
			return True

		if redoInitFit:
			cmd = lines[1]
			print cmd
			subprocess.call([cmd], shell = True)
		scripts = []
		# if not ncmds == len(rootfiles) or redoInitFit:
		# 	cmd = lines[-1]
		# 	print cmd
		# 	subprocess.call([cmd], shell = True)
		# else:
		scripts = find_missing_scripts(rootfiles = rootfiles, scriptList = scriptList)
				
		if len(scripts) is not 0:
			if useBatch:
				print scripts
				if batch_config.arraysubmit is True:
					batch_config.submitArrayToBatch(scripts, folder + "/logs/arrayJob.sh")
				else:
					batch_config.submitJobToBatch(scripts)
			else:
				for script in scripts:
					subprocess.call([script], shell=True)
		else:
			print "all root files are intact"

		return False
	else:
		print "unable to find any .sh files!"
		return True

def submit_missing(	impactFolders, listToCrossCheck, 
			listToResub, cmdList = None):
	folders = []
	basenames = [os.path.basename(i) for i in impactFolders]
	print "list of impact folders to be cross checked with list of datacards/workspaces"
	print basenames
	for path in listToCrossCheck:
		parts = os.path.basename(path).split(".")
		foldername = ".".join(parts[:len(parts)-1])
		print "checking", foldername
		for entry in listToResub:
			name = os.path.basename(entry)
			print "\tcomparing", name
			if foldername == name:
				print "found match!"
				folders.append(path)
				break
		if foldername in basenames:
			print "\tfound matching folder"
		else:
			print "\t%s flagged for fresh submit" % foldername
			folders.append(path)

	fresh_submit(folders, cmdList)

def fresh_submit(datacards, cmdList = None):
	for datacard in datacards:
		scriptPath = scriptDir + "/submitImpactFits.py"
		print "calling", scriptPath
		cmd = "python {0} {1}".format(scriptPath, datacard)
		if cmdList:
			cmd += " " + " ".join(cmdList)
		print cmd
		subprocess.call([cmd], shell = True)

#=======================================================================

#=======script==========================================================

print listOfDatacards
print listOfResubFolders
print additionalSubmitCmds
if not additionalSubmitCmds is None:
	print " ".join(additionalSubmitCmds)

if len(listOfDatacards) is 0:
	sys.exit("Found no datacards to cross check with in %s" % datacardWildcard)

listOfDatacards = [os.path.abspath(datacard) for datacard in listOfDatacards]
impactFolders = [os.path.abspath(path) for path in listOfResubFolders]

toResub = []
base = os.getcwd()
for resubFolder in impactFolders:
	# resubFolder = os.path.abspath(resubFolder)
	foldername = os.path.basename(resubFolder)

	if check_for_resubmit(folder = resubFolder):
		toResub.append(resubFolder)
	os.chdir(base)

print "list to resubmit:"
print toResub

submit_missing(	impactFolders = impactFolders,
		listToCrossCheck = listOfDatacards,
		listToResub = toResub,
		cmdList = additionalSubmitCmds)
