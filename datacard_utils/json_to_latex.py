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
global_mode = "tex"
def setup_global_table_format(mode):
    global header
    global line
    global footer
    global global_mode
    global_mode = mode
    if mode == "tex":
        header = """\\begin{tabular}{lccc}
        \\toprule
        Parameter & Stat+Syst & Stat-Only & Significance \\\\"""
        line = """{parameter} & {bestfit} & {statonly} & {signi}\\\\"""
        footer = """\\bottomrule
        \\end{tabular}"""
    elif mode == "md":
        header = """
        | Parameter | Stat+Syst | Stat-Only | Significance |
        | --- | --- | --- | --- |"""
        line = """| {parameter} & {bestfit} & {statonly} & {signi} |""".replace("&", "|")
        footer = ""

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
    parser.add_option("--mode",
                        help = " ".join(
                            """
                            select output mode. Current choices:
                            tex (LaTex), md (Markdown). Defaults to tex
                            """.split()
                            ),
                        dest = "mode",
                        choices = ["tex", "md"],
                        default = "tex"
                        )
    options, infiles = parser.parse_args()
    if options.merge and options.is_prefix:
        parser.error("LOGIC ERROR: cannot merge and use prefix!")
    
    setup_global_table_format(options.mode)
    if not options.outfile.endswith(options.mode):
        options.outfile = ".".join(options.outfile.split(".")[:-1] + [options.mode])
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
        if "significance" in subdict and not subdict["significance"] == "--":
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
        if global_mode == "tex":
            lines.append("\\midrule")
        lines += parse_results(f)
    lines.append(footer)
    return "\n".join(lines)

def save_file(outname, output):
    with open(outname, "w") as f:
        f.write(output)

def main(options, files):
    merge = options.merge
    prepend = options.is_prefix
    outname = options.outfile
    mode = options.mode
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
            if mode == "tex":
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
