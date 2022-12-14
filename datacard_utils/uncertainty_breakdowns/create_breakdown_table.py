from collections import OrderedDict
import os
import sys
import json
from optparse import OptionParser
import imp

header = """
\\begin{tabular}{cc}
\hline\hline
Group & \Delta \mu \\\\
\hline\hline
"""
line_template = "{group} & {valup:+.2f}/{valdown:+.2f}\\\\"

footer = """
\hline\hline
\end{tabular}
"""

def parse_arguments():
    usage = "python %prog [options] paths/to/files.json"
    parser = OptionParser(usage = usage)
    parser.add_option("-c", "--config",
                    help = " ".join(
                        """
                        file containing the order in which to display
                        the groups. Should be a python file containing
                        the object 'clearnames', which can either be a list
                        or an OrderedDict
                        """.split()
                    ),
                    dest = "config",
                    type = "str"
    )
    parser.add_option("-f", "--format",
                    help = " ".join(
                        """
                        format of output file. Choices: tex, md.
                        Default: tex
                        """.split()
                    ),
                    dest = "format",
                    choices = "tex md".split(),
                    default = "tex"
    )
    options, files = parser.parse_args()

    return options, files

def create_table(val_dict, outname, order = []):
    lines = []
    if len(order) == 0:
        order = val_dict.keys()
    if not "Total" in order:
        order += ["Total-Stat","Total"] 
    for group in order:
        group_dict = val_dict.get(group, None)
        group = group.replace(" - substract from Stat", "")
        if group_dict:
            line = line_template.format(group=group,
                                valup = group_dict["valup"],
                                valdown = group_dict["valdown"]
                            )
            lines.append(line)
    
    table = header
    table += "\n".join(lines)
    table += footer
    if not outname.endswith(".tex"):
        outname += ".tex"
    with open(outname, "w") as f:
        f.write(table)

def load_order(path_to_config):
    order = []
    config = imp.load_source('config', path_to_config)
    try:
       names = config.clearnames
    except:
        s = ("Unable to load object 'clearnames' from '{}'"
                .format(path_to_config))
        raise ImportError(s)
    if isinstance(names, OrderedDict):
        order = names.values()
    elif isinstance(names, list):
        order = names
    else:
        s = ("Currently unable to support config with clearnames of type '{}'"
                .format(type(names)))
        raise ValueError(s)
    
    return order

def main(*files, **kwargs):
    config = kwargs.get("config")
    order = load_order(config)
    for f in files:
        if not f.endswith(".json"):
            print("Input needs to be json format!")
            continue
        val_dict = {}
        with open(f) as infile:
            val_dict = json.load(infile)
        
        for par in val_dict:
            outname = ".".join(f.split(".")[:-1])
            outname += "_{}".format(par)
            create_table(val_dict=val_dict[par], outname=outname, order=order)

if __name__ == "__main__":
    options, files = parse_arguments()
    main(*files, **vars(options))
