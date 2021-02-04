import os
import sys
from glob import glob
from optparse import OptionParser
import imp


def parse_arguments():
	usage = """
	python %prog [options] path/to/input/files

	Small function to create latex slides with navigation for impacts,
	pulls and result tables. The inputs are the following

	- impacts: 	path to directories containing the list of missing variables 
				and the .tex file with code to display impact plot

	- pulls:	path to .pdf files of pull plots

	- results: 	path to .tex files containing the tables with fit results

	The name config contains the information about how to display a given 
	result and must contain 

	- keyword_dict:		a dictionary with the combination name as key 
						and the items 'label' and clearname
	- order:			list with the order in which the results are to be displayed

	The config 'config' must contain the slide_template and can contain prefixes for
	the label and the clearname
	"""
	parser = OptionParser(usage = usage)

	parser.add_option( "-m", "--mode",
						choices = [
						"i", "impacts",
						"p", "pulls",
						"r", "results"
						],
						dest = "mode",
						help = " ".join("""
						choose the sort of slides you'd like to produce.
						Choices are 'i' (impacts), 'p' (pulls), 'r' (results)
						""".split())
					)
	parser.add_option( "-c", "--config",
						dest = "config",
						help = " ".join("""
							path to config file containing slide_template
							""".split()),
						type = "str",
						default = "dummypath"
					)
	parser.add_option( "-n", "--nameconfig",
						dest = "nameconfig",
						help = " ".join("""
							path to config file containing 
							keyword_dict (with translations to clearname 
							and label for slides) as well as the 
							list 'order' (order in which to display
							the slides)
							""".split()),
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

def create_slide(slide_template, **kwargs):	
	startdir = os.getcwd()
	lines = None
	navigation_entry = None
	label = kwargs.get("label", None)
	clearname = kwargs.get("clearname", None)
	param = kwargs.get("param", None)
	if not param == "" and param:
		label += "_{}".format(param)
		clearname += " \\\\({})".format(param)
		kwargs.update({"label": label, "clearname": clearname})

	if not (label is None or clearname is None):
		lines = slide_template.format(**kwargs)
		navigation_entry = [label, clearname.replace("\\\\", "")]
	else:
		print "ERROR, could not load label/clearname information!"
	return lines, navigation_entry

def load_prefixes(config):
	prefix_label = None
	prefix_clearname = None
	try:
		prefix_label = config.prefix_label
	except:
		print "could not load prefix label"

	try:
		prefix_clearname = config.prefix_clearname
	except:
		print "could not load prefix clearname"
		
	return prefix_label, prefix_clearname

def create_results_slides(current_name, path, config, keyword_dict):
	
	slide_template = config.slide_template

	prefix_label, prefix_clearname = load_prefixes(config)

	label = keyword_dict["label"]
	if not prefix_label is None:
		label = label.format(prefix_label)

	clearname = keyword_dict["clearname"]
	if not prefix_clearname is None:
		clearname = clearname.format(prefix_clearname)

	lines = None
	navigation = None

	if path.endswith(".tex"):
		if path.endswith(current_name+".tex"):
			lines, navigation = create_slide(
									slide_template = slide_template,
									label = label,
									clearname = clearname,
									filename = os.path.basename(path)
									)
	else:
		print "'%s' is not a .tex file, skipping" % path

	return lines, navigation

def create_impact_slides(current_name, path, config, keyword_dict):
	
	slide_template = config.slide_template

	prefix_label, prefix_clearname = load_prefixes(config)

	label = keyword_dict["label"]
	if not prefix_label is None:
		label = label.format(prefix_label)

	clearname = keyword_dict["clearname"]
	if not prefix_clearname is None:
		clearname = clearname.format(prefix_clearname)
	
	path = os.path.abspath(path)
	lines = []
	navigation = []
	startdir = os.getcwd()
	if not os.path.isdir(path):
		print "'%s' is not a directory, skipping" % path
	else:
		if path == "ttH_hbb_13TeV_2017_sl/": print "HERE"
		if path.endswith("/"): path = path[:-1]
		
		dirname = os.path.basename(path)

		if dirname == current_name:
			print "checking", path
			os.chdir(path)
			missing_variables = load_missing_vars(logfile = config.logfile)
			missing_var_string = "all"
			
			texpath_wildcard = config.texfile.format(dirname)
			try:
				params = config.parameters
			except:
				params = [""]
			texpaths = glob(texpath_wildcard)
			print(texpaths)
			for param in params:
				print("doing parameter '{}'".format(param))
				for texpath in texpaths:
					if not os.path.exists(texpath):
						texpath = "NONE"
					if not param in texpath:
						continue
					print("current texpath: {}".format(texpath))
					if not texpath == "NONE":
						if not missing_variables is None:
							if len(missing_variables) == 0:
								missing_var_string = "none"
							else:
								missing_var_string = ",\n".join(
											[x.replace("_", "\\_") \
												for x in missing_variables]
												)
				
					
					tmp_lines, tmp_navigation = create_slide(
													slide_template = slide_template,
													label = label,
													clearname = clearname,
													filename = texpath,
													missing_vars = missing_var_string,
													param = param
													)
					lines.append(tmp_lines)
					navigation.append(tmp_navigation)
	if len(lines) == 0:
		lines = None
	if len(navigation) == 0:
		navigation = None
	os.chdir(startdir)
	return lines, navigation

def create_pullplot_slides(current_name, path, config, keyword_dict):
	slide_template = config.slide_template

	prefix_label, prefix_clearname = load_prefixes(config)

	label = keyword_dict["label"]
	if not prefix_label is None:
		label = label.format(prefix_label)

	clearname = keyword_dict["clearname"]
	if not prefix_clearname is None:
		clearname = clearname.format(prefix_clearname)

	lines = None
	navigation = None

	if not (os.path.isfile(path) and path.endswith(".pdf")):
		print "'%s' is not a .pdf file, skipping" % path
	else:
		path = os.path.abspath(path)
		# filename = os.path.basename(path)
		# # parname = ".".join(filename.split(".")[:-1])
		# # parname = parname.replace("pulls_", "")
		# # parname = parname.replace("fitDiagnostics_asimov_sig1_", "")

		if path.endswith(current_name+".pdf"):
			lines, navigation = create_slide(
									slide_template = slide_template,
									label = label,
									clearname = clearname,
									filename = os.path.basename(path)
									)

	return lines, navigation		

def create_file(slidelines, outputpath):
	for i, l in enumerate(slidelines):
		sublines = l.splitlines()
		for j, sl in enumerate(sublines):
			if "NONE" in sl:
				sublines[j] = "%" + sl
		slidelines[i] = "\n".join(sublines)

	with open(outputpath, "w") as f:
		f.write("\n".join(slidelines))

def main(options, filepaths):

	mode = options.mode
	configpath = options.config
	config = imp.load_source('config', configpath)

	name_cfgpath = options.nameconfig
	name_cfg = imp.load_source('name_cfg', name_cfgpath) 

	order = name_cfg.order
	keyword_dict = name_cfg.keyword_dict

	outputpath = options.output

	slidelines = []
	navigation = []
	paths = []
	for w in filepaths:
		paths += glob(w)
	print paths
	print order

	for name in order:
		for p in paths:

			if mode == "i" or mode == "impacts":
				lines, nav_entry = create_impact_slides(current_name = name,
														path = p, config = config,
														keyword_dict = keyword_dict[name])
			elif mode == "p" or mode == "pulls":
				lines, nav_entry = create_pullplot_slides(current_name = name,
														path = p, config = config,
														keyword_dict = keyword_dict[name])
			elif mode == "r" or mode == "results":
				lines, nav_entry = create_results_slides(current_name = name,
														path = p, config = config,
														keyword_dict = keyword_dict[name])

			if not (lines is None or nav_entry is None):
				if isinstance(lines, list):
					navigation += nav_entry
					slidelines += lines
				else:
					navigation.append(nav_entry)
					slidelines.append(lines)
				break

	if len(navigation) > 0:
		navlines = create_navigation_lines(navigation)
		slidelines.insert(0, navlines)
	else:
		print "WARNING: Could not generate navigation slide"

	if not slidelines is None and len(slidelines) > 0:
		create_file(slidelines, outputpath)


if __name__ == '__main__':
	options, filepaths = parse_arguments()
	main(options = options, filepaths = filepaths)