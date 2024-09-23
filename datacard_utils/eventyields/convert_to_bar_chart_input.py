import os
import sys

import json
import ROOT
from get_yields import init_module, get_yields, load_keyword, category
from argparse import ArgumentParser
from typing import Any
from tqdm import tqdm

def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument(
        "-c", "--config",
        help = " ".join("""
            Path to config specifying processes, latex code for
            processes, categories
            """.split()
        ),
        dest = "config",
        type = str,
        required = True,
                    )
    
    parser.add_argument(  "inputfiles",
                        help = " ".join("""
                        path to input files to convert
                        """.split()),
                        metavar = "path/to/inputs*.root",
                        nargs = "+",
                        type = str,
                    )
    parser.add_argument(  "-m", "--mode",
                        help = " ".join("""
                        switch that decides whether to create prefit
                        or postfit table. Choices: 'prefit' (prefit tables),
                        'fit_s' (s+b tables), 'fit_b' (b-only tables)
                        """.split()),
                        dest = "mode",
                        choices = ["prefit", "fit_s", "fit_b"],
                        required = True,
                    )

    parser.add_argument(  "-o", "--outputfile",
                        help = " ".join("""
                        save table string in this file. If not provided,
                        the name of the input file is used
                        """.split()),
                        dest = "outfile",
                        metavar = "path/to/output.json",
                        type = str,
                        required = False,
                        default=None,
                    )

    parser.add_argument( "--prefix",
                        help = " ".join("""
                        prepend this prefix to the individual channel names
                        specified in the label config, e.g. ttH_2016 etc.
                        """.split()),
                        dest = "prefix",
                        type = str,
                        default = "",
                        required = False,
                    )
    parser.add_argument(  "--not-harvester",
                        help = " ".join("""
                        use this option if the shapes were not generated using
                        the PostFitShapesFromWorkspace script in the 
                        CombineHarvester
                        """.split()),
                        dest = "not_harvester",
                        action = "store_true",
                        default = False,
                        required = False,
                    )
    parser.add_argument(
       "--overwrite-category",
        action = "store_true",
        help = (
            "Overwrite the category name in the final table with the file name "
        ),
        default=False,
    )

    args = parser.parse_args()

    return args

def convert_to_final_output(yields):
    
    final_yields = {}
    categories = list()
    pbar = tqdm(yields.items())
    for category, yields_dict in pbar:
        categories.append(category)
        for process, y in yields_dict.items():
            if process not in final_yields:
                final_yields[process] = []
                final_yields[f"{process}_err"] = []
            try:
                final_yields[process].append(y.getVal())
                final_yields[f"{process}_err"].append(y.getError())
            except AttributeError:
                final_yields[process].append(0)
                final_yields[f"{process}_err"].append(0)

    return {
        "categories": categories,
        "yields": final_yields,
    }

def convert_file(
    infile_path,
    categories,
    mode,
    cfg_module,
    prefix,
    **kwargs,
) -> None:
    is_harvester = not load_keyword(kwargs, "not_harvester")
    overwrite_category = load_keyword(kwargs, "overwrite_category")
    in_file = ROOT.TFile.Open(infile_path)
    yields = get_yields(in_file, categories, mode , cfg_module,\
                                 prefix, is_harvester)

    if overwrite_category and len(yields) >1:
        raise ValueError(
            "Cannot overwrite category name with multiple categories. "
            f"Expected 1 category, got {len(yields)}"
        )
    elif overwrite_category:
        infile_name = ".".join(os.path.basename(infile_path).split(".")[:-1])
        yields = {
            infile_name: yields[key] for key in yields.keys()
        }
    
    converted_yields = convert_to_final_output(yields)
    outfile = ".".join(infile_path.split(".")[:-1]) + ".json"
    with open(outfile, "w") as f:
        json.dump(converted_yields, f, indent=4)

def main(*args, **kwargs):
    config = load_keyword(kwargs, "config")
    inputfiles = load_keyword(kwargs, "inputfiles")

    cfg_module = init_module(config)
    input_bar = tqdm(inputfiles)
    # need to fake the category list, kind of dumb
    categories = []
    for njet_category in cfg_module.njet_categories:
        for sub_category in cfg_module.sub_categories:
            categories.append( category( njet_category, sub_category ) )
                
    for i, in_file in enumerate(input_bar):
        input_bar.set_description(f"Processing {in_file}")
        convert_file(in_file, cfg_module=cfg_module, categories=categories, **kwargs)


if __name__ == '__main__':
    args = parse_arguments()
    main(**vars(args))