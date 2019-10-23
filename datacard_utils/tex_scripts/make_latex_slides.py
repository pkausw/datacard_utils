import os
import sys
from glob import glob
from optparse import OptionParser
import imp


def parse_arguments():
	parser = OptionParser()

	parser.add_option( "-m", "--mode",
						choices = [
						"i", "impacts",
						"p", "pulls"
						],
						dest = "mode",
						help = "choose the sort of slides you'd like to produce"
					)
	parser.add_option( "-c", "--config",
						dest = "config",
						help = """path to config file containing 
								slide_template
								keyword_dict (with translations to clearname and label for slides)
								""",
						type = "str",
						default = "dummypath"
					)
	parser.add_option( "-o", "--outputfile",
						dest = "output",
						help = "name of output file",
						default = "slides.tex"
		)
	options, args = parser.parse_args()
	if options.mode is None:
		parser.error("Mode is required!")
	if not os.path.exists(options.config):
		parser.error("Could not find config file!")
	return options, args

def load_missing_vars(logfile = "json_creation.log"):
	if not os.path.exists(logfile):
		print "ERROR: File '%s' does not exist!" % logfile
		return None
	lines = []
	variables = []
	with open(logfile) as f:
		lines = f.read().splitlines()
	for l in lines:
		l = l.strip()
		if l.startswith("Missing inputs"):
			variables = l.replace("Missing inputs: ", "").split(",")
			print variables
			if len(variables) > 0:
				with open("broken_variables.txt", "w") as f:
					f.write("\n".join(variables))
	return variables

def create_navigation_lines(navigation):
	counter = 0
	head = """\\begin{frame}{Overview - %s}
	\\begin{itemize}
	"""
	end = """
	\end{itemize}
	\end{frame}\n
	"""
	navlines = ""
	for i, pair in enumerate(navigation):
		if i % 10 == 0:
			if not navlines == "":
				navlines += end
			navlines += head % str(counter)
			counter += 1
		navlines += "\item \hyperlink{%s}{%s}\n" % (pair[0], pair[1])

	navlines += end
	return navlines

def create_slide(path, config):
	slide_template = config.slide_template
	keyword_dict = config.keyword_dict
	startdir = os.getcwd()
	lines = None
	navigation_entry = None
	print "checking", path
	path = os.path.abspath(path)

	dirname = os.path.basename(path)
	if not dirname in keyword_dict:
		print "No information about '%s' provided in keyword_dict of config file!" % dirname
		print "Skipping"
		os.chdir(startdir)
		return lines, navigation_entry
	os.chdir(path)
	missing_variables = load_missing_vars(logfile = config.logfile)
	missing_var_string = "all"

	texpath = config.texfile % dirname
	if not os.path.exists(texpath):
		texpath = "NONE"

	if not texpath == "NONE":
		if not missing_variables is None:
			if len(missing_variables) == 0:
				missing_var_string = "none"
			else:
				missing_var_string = ",\n".join([x.replace("_", "\\_") for x in missing_variables])

	lines = slide_template % ({
			"LABEL": keyword_dict[dirname]["label"],
			"CLEARNAME": keyword_dict[dirname]["clearname"],
			"MISSING_VARS": missing_var_string,
			"IMPACTSLIDETEX" : texpath
		})
	navigation_entry = [keyword_dict[dirname]["label"], keyword_dict[dirname]["clearname"].replace("\\\\", "")]
	os.chdir(startdir)
	return lines, navigation_entry

def create_impact_slides(filepaths, config):
	
	order = config.order

	lines = []
	navigation = []
	paths = []
	for w in filepaths:
		paths += glob(w)
	print paths
	print order
	for key in order:
		for path in paths:
			

			if not os.path.isdir(path):
				print "'%s' is not a directory, skipping" % path
				os.chdir(startdir)
				continue
			if path == "ttH_hbb_13TeV_2017_sl/": print "HERE"
			if path.endswith("/"): path = path[:-1]


			if path == key:
				slide, navigation_entry = create_slide(path = path, config = config)
				print slide, navigation_entry
				if not (slide is None or navigation_entry is None):
					lines.append(slide)
					navigation.append(navigation_entry)
	
			
	if len(navigation) > 0:
		navlines = create_navigation_lines(navigation)
		lines.insert(0, navlines)
	else:
		print "WARNING: Could not generate navigation slide"
	return lines

def create_pullplot_slides(filepaths, config):
	slide_template = config.slide_template
	label_template = config.label_template
	startdir = os.getcwd()
	lines = []
	navigation = []
	for w in filepaths:
		for path in glob(w):
			print "checking", path
			if not os.path.isfile(path):
				print "'%s' is not a file, skipping" % path
				os.chdir(startdir)
				continue
			path = os.path.abspath(path)
			filename = os.path.basename(path)
			parname = ".".join(filename.split(".")[:-1])
			parname = parname.replace("_pulls", "")
			parlabel = label_template % parname
			clearname = parname.replace("_", "\\_")
			lines.append(slide_template % ({
					"CLEARNAME" : clearname,
					"LABEL" : parlabel,
					"PLOTNAME" : filename

				}))
			navigation.append([parlabel, clearname])
	if len(navigation) > 0:
		navlines = create_navigation_lines(navigation)
		lines.insert(0, navlines)
	else:
		print "WARNING: Could not generate navigation slide"
	return lines


def main(options, filepaths):

	mode = options.mode
	configpath = options.config
	config = imp.load_source('config', configpath)

	if mode == "i" or mode == "impacts":
		slidelines = create_impact_slides(filepaths, config)
	elif mode == "p" or mode == "pulls":
		slidelines = create_pullplot_slides(filepaths, config)
	else:
		print "Did not recognize mode!"
		sys.exit(0)

	if not slidelines is None and len(slidelines) > 0:
		for i, l in enumerate(slidelines):
			sublines = l.splitlines()
			for j, sl in enumerate(sublines):
				if "NONE" in sl:
					sublines[j] = "%" + sl
			slidelines[i] = "\n".join(sublines)

		outputpath = options.output
		with open(outputpath, "w") as f:
			f.write("\n".join(slidelines))




if __name__ == '__main__':
	options, filepaths = parse_arguments()
	main(options = options, filepaths = filepaths)