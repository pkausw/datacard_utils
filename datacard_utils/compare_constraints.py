import os
import sys
import json
import pprint
import ROOT
from collections import OrderedDict
from optparse import OptionParser
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)

header = """
    \\begin{frame}
    \\begin{scriptsize}
    \\begin{tabular}{lcccc}
    \\toprule
    Parameter & Base Value & Varied Value & Difference & Rel.\\ Difference \\\\
    \\midrule
    """
footer = """
\\bottomrule
\\end{tabular}
\\end{scriptsize}
\\end{frame}
"""
template = "$_{{{low:+}}}^{{{up:+}}}$"

def setup_table_template(mode):
    global header
    global footer
    global template
    if mode == "tex":
        header = """
        \\begin{frame}
        \\begin{scriptsize}
        \\begin{tabular}{lcccc}
        \\toprule
        Parameter & Base Value & Varied Value & Difference & Rel.\\ Difference \\\\
        \\midrule
        """
        footer = """
        \\bottomrule
        \\end{tabular}
        \\end{scriptsize}
        \\end{frame}
        """
        template = "$_{{{low:+}}}^{{{up:+}}}$"
    elif mode == "md":
        header = """
        | Parameter | Base Value | Varied Value | Difference | Rel. Difference |
        | --- | --- | --- | --- | --- |
        """
        footer = ""
        template = "{low:+}/{up:+}"

def translate_fitresult_to_dict(f):
    params = f.floatParsFinal().contentsString().split(",")
    return_list = []
    for p in params:
        var = f.floatParsFinal().find(p)
        vallist = [
            var.getErrorLo() + var.getVal(),
            var.getVal(),
            var.getErrorHi() + var.getVal(),
        ]
        return_list.append({
            "name": p,
            "fit": vallist
        })
        # print(vallist)
        # print({
        #     "name": p,
        #     "fit": vallist
        # })
    return return_list
def load_fitresult_object(path, fitobject = "fit_s"):
    r = ROOT.TFile.Open(path)
    if r.IsOpen() and not r.IsZombie() and not r.TestBit(ROOT.TFile.kRecovered):
        f = r.Get(fitobject)
        if not isinstance(f, ROOT.RooFitResult):
            f = r.Get("fit_mdf")
            if not isinstance(f, ROOT.RooFitResult):
                raise ValueError("Could not load fit results from '{}'".\
                    format(path))
    else:
        raise ValueError("Could not load fit results from '{}'".\
                    format(path))
    
    return translate_fitresult_to_dict(f)

def load_json(path):
    return_dict = {}
    if path.endswith(".json"):
        with open(path) as f:
            return_dict = json.load(f)
        return return_dict.get("params", {})
    elif path.endswith(".root"):
        return load_fitresult_object(path)

def construct_difference_dict(basevals, othervals):
    default_val = -999999
    baseval_down = basevals.get("fit", [default_val, 0, default_val])[0]
    baseval_val = basevals.get("fit", [default_val, default_val, default_val])[1]
    baseval_up = basevals.get("fit", [default_val, 0, default_val])[2]

    otherval_down = othervals.get("fit", [default_val, 0, default_val])[0]
    otherval_val = othervals.get("fit", [default_val, default_val, default_val])[1]
    otherval_up = othervals.get("fit", [default_val, 0, default_val])[2]

    if any(v == default_val for v in [baseval_up, baseval_val, baseval_down, otherval_up, otherval_val, otherval_down]):
        return None
    baseval_up = baseval_up - baseval_val
    baseval_down = baseval_down - baseval_val

    otherval_up -= otherval_val
    otherval_down -= otherval_val 
    reldif_up = (otherval_up - baseval_up)/baseval_up if not baseval_up == 0 else 0
    reldif_down = (otherval_down - baseval_down)/baseval_down if not baseval_down == 0 else 0
    rdict = {
        "baseval_up" : baseval_up,
        "baseval_down": baseval_down,
        "otherval_up" : otherval_up,
        "otherval_down" : otherval_down,
        "differance_up": otherval_up - baseval_up,
        "differance_down" : otherval_down - baseval_down,
        "rel_diff": (abs(reldif_up) + abs(reldif_down))/ 2.
    }
    for key in rdict:
        rdict[key] = round(rdict[key], 3)
    return rdict

def create_table(dictionary, outformat):
    
    s = ""
    for i, par in enumerate(dictionary):
        if i == 0:
            s = header
        elif i % 15 == 0:
            s += footer
            s += header
        parts = [par]
        if outformat == "tex":
            parts = [par.replace("_", "\\_")]
        pardict = dictionary[par]
        parts.append(template.format(low = pardict["baseval_down"], 
                                        up = pardict["baseval_up"]))
        parts.append(template.format(low = pardict["otherval_down"], 
                                        up = pardict["otherval_up"]))
        parts.append(template.format(low = pardict["differance_down"], 
                                        up = pardict["differance_up"]))
        parts.append(str(pardict["rel_diff"]))
        if outformat == "tex":
            s += " & ".join(parts) + "\\\\\n"
        elif outformat == "md":
            s += "| {} |\n".format(" | ".join(parts))
    s += footer
    return s


def get_differences(basevals, othervals):
    return_dict = {}
    for pardict in basevals:
        parname = pardict.get("name", "")
        # if not (parname.endswith("_j") or "_j_" in parname):
        #     continue 
        if "prop_bin" in parname:
            continue
        for valdict in othervals:
            if not valdict.get("name", "") == parname:
                continue
            # print(valdict)
            values = construct_difference_dict(basevals = pardict, 
                                                othervals = valdict)

            if values:
                return_dict[parname] = values
            else:
                print("Could not find values for '{}'! Skipping".format(parname))
    return return_dict

def main(basevals, othervals, outpath, outformat):

    results = {}
    params1 = load_json(basevals)
    params2 = load_json(othervals)
    results = get_differences(basevals = params1, othervals = params2)

    values = OrderedDict(reversed(sorted(results.iteritems(), \
                                key = lambda x: x[1]["rel_diff"])))
    print(json.dumps(values, indent = 4))

    table = create_table(values, outformat)
    print(table)
    if not outpath.endswith(outformat): 
        outpath = ".".join(outpath.split(".")[:-1] + [outformat])
    with open(outpath, "w") as f:
        f.write(table)

def check_path(inpath):
    if not os.path.exists(inpath):
        raise ValueError("file {} does not exist!".format(inpath))
    if not inpath.endswith(".json") and not inpath.endswith(".root"):
        raise ValueError("file {} is not a json file!".format(inpath))
    return inpath

def parse_arguments():
    usage = """Tool to compare the constraints based on the fits
    done for the generation of the impacts
    %prog [options]
    """
    parser = OptionParser(usage = usage)

    parser.add_option("-b", "--base",
                        help = " ".join(
                            """
                            use the values in this .json file as reference
                            """.split()),
                        dest = "base",
                        type = "str"
                    )
    parser.add_option("-v", "--varied",
                        help = " ".join(
                            """
                            compare the values in this .json file to the base values
                            """.split()),
                        dest = "varied",
                        type = "str"
                    )
    parser.add_option("-o", "--outpath",
                        help = " ".join(
                            """path to the .tex file containing tables
                             (sorted w.r.t. relative difference)
                            """.split()),
                        dest = "outpath",
                        type = "str"
                    )
    parser.add_option("-f", "--format",
                        help = " ".join(
                            """select output format. Available formats:
                            tex, md
                            """.split()),
                        dest = "format",
                        choices = ["tex", "md"],
                        default = "tex"
                    )

    options, args = parser.parse_args()
    setup_table_template(options.format)
    return options
if __name__ == "__main__":
    
    options = parse_arguments()
    fpath1 = check_path(options.base)
    fpath2 = check_path(options.varied)
    outpath = options.outpath
    
    main(basevals = fpath1, othervals = fpath2, outpath = outpath, outformat = options.format)