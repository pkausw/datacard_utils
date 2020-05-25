import os
import sys
import json

from optparse import OptionParser

header = """\\begin{tabular}{lccc}
\\toprule
Parameter & Stat+Syst & Stat-Only & Significance \\\\"""
line = """{parameter} & {bestfit} & {statonly} & {signi}\\\\"""
footer = """\\bottomrule
\\end{tabular}"""

def parse_arguments():
    
    parser = OptionParser()
    parser.add_option("-o", "--outfile",
                      dest = "outfile",
                      help = " ".join(
                          """Use this as the output name""".split()
                        )
                      )
    parser.add_option("-p", "--prefix",
                      dest = "is_prefix",
                      action = "store_true",
                      default = False,
                      help = " ".join(
                          """activate this if you want to
                          translate multiple .json files
                          at once. The input from '-o'
                          will be prepended to the input
                          file name""".split()
                          )
                        )
    parser.add_option("-m", "--merge",
                      dest = "merge",
                      action = "store_true",
                      default = False,
                      help = " ".join(
                          """activate this if you want to
                          merge multiple .json files
                          at one .tex file""".split()
                          )
                        )
    options, infiles = parser.parse_args()
    if options.merge and options.is_prefix:
        parser.error("LOGIC ERROR: cannot merge and use prefix!")
    
    return options, infiles

def parse_results(file):
    print("reading results from {}".format(file))
    with open(file, "r") as f:
        results = json.load(f)
    lines = []
    fitresult_template = "{val}  +{up}/{down}"
    for param in results:
        subdict = results[param]
        if "bestfit" in subdict:
            bestfit_text = fitresult_template.format(
                val = round(subdict["bestfit"]["value"], 2),
                up = round(subdict["bestfit"]["up"], 2),
                down = round(subdict["bestfit"]["down"], 2)
            )
        else:
            bestfit_text = "--"
        if "stat_only" in subdict:
            stat_only_text = fitresult_template.format(
                val = round(subdict["stat_only"]["value"], 2),
                up = round(subdict["stat_only"]["up"], 2),
                down = round(subdict["stat_only"]["down"], 2)
            )
        else:
            stat_only_text = "--"
        if "significance" in subdict:
            signi_text = str(round(subdict["significance"], 1))
        else:
            signi_text = "--"
        lines.append(line.format(
            parameter = param.replace("_", "\\_"),
            bestfit = bestfit_text,
            statonly = stat_only_text,
            signi = signi_text
        ))
    return lines

def create_merged_tex(files):
    lines = [header]
    for f in files:
        if not os.path.exists(f):
            print("ERROR: file {} does not exist".format(f))
            continue
        lines.append("\\midrule")
        lines += parse_results(f)
    lines.append(footer)
    return "\n".join(lines)

def save_file(outname, output):
    if not outname.endswith(".tex"):
        outname += ".tex"
    with open(outname, "w") as f:
            f.write(output)

def main(options, files):
    merge = options.merge
    prepend = options.is_prefix
    outname = options.outfile
    output = None
    if merge:
        print("="*130)
        print("create merged output")
        print("="*130)
        output = create_merged_tex(files)
    elif prepend:
        output = []
        pass
    else:
        if len(files) == 1:
            tmp = [header]
            tmp.append("\\midrule")
            tmp += parse_results(files[0])
            tmp.append(footer)
            output = "\n".join(tmp)
    if output:
        if isinstance(output, list):
            pass
        else:
            save_file(outname, output)
    else:
        print("WARNING: Could not generate output")
if __name__ == '__main__':
    options, infiles = parse_arguments()
    main(options = options, files = infiles)