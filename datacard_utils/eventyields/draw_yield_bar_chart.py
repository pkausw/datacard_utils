import os
import mplhep as hep
import cmsstyle as CMS
import matplotlib.pyplot as plt
import numpy as np
import json
from typing import Any
from tqdm import tqdm
from argparse import ArgumentParser
from get_yields import init_module, load_keyword
from ROOT import gROOT

# setup CMS style for matplotlib
hep.style.use("CMS")

from matplotlib.colors import ListedColormap
petroff10 = ListedColormap([
    "#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6", "#a96b59",
    "#e76300", "#b9ac70", "#717581", "#92dadd",
])

default_color_iterator = iter(petroff10.colors)

default_objects = [
    "ttlf", "ttcc", "ttbb", "singlet", "vjets", "ttbarV", "diboson", "tHq",
    "tHW", "TotalSig"
]

def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        "inputs", type=str, nargs="+",
        help="Input JSON files containing event yields",
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True,
        help="Path to output file (without extension)",
    )
    parser.add_argument(
        "-e", "--extensions", type=str, nargs="+", default=[],
        help="File extensions to save. Default: pdf, png",
    )
    parser.add_argument(
        "-d", "--draw-total", action="store_true",
        help="If true, draw the total MC and observed data yields under category name",
    )
    parser.add_argument(
        "-c", "--config", type=str, default=None,
        metavar="path/to/config.py",
        help="Path to configuration file with style settings for processes",
    )
    parser.add_argument(
        "-l", "--label-config", type=str, default=None,
        metavar="path/to/cateorgy_label_config.json",
        help="Path to configuration file for category labels",
    )
    parser.add_argument(
        "--draw-objects", type=str, nargs="+", default=default_objects,
        help="Objects to draw in the bar chart. Default: {}".format(", ".join(default_objects)),
    )

    args = parser.parse_args()

    if not args.extensions:
        args.extensions = ["pdf", "png"]
    
    if not args.draw_objects:
        args.draw_objects = default_objects
    return args

def draw_yield_bar_chart(
    yields_dict: dict[str, np.ndarray],
    output_path: str,
    objects_to_draw: list[str],
    plot_config: dict[str, Any] = None,
    extensions: list[str] = ["pdf", "png"],
    draw_total: bool = True,
) -> None:
    """
    """
    data = yields_dict["yields"]
    shape = data["ttlf"].shape
    final_xlabels = yields_dict["categories"]
    bottom = np.zeros(final_xlabels.shape[0])
    mc_sum = np.sum((data[x] for x in objects_to_draw), axis=0)
    if not plot_config:
        plot_config = dict()

    
    if draw_total:
        stacked_values = np.column_stack((final_xlabels, data["TotalProcs"], data["TotalProcs_err"], data["data_obs"]))
        final_xlabels = list(map(
            lambda entry: f"{entry[0]}\nTotal MC: ${float(entry[1]):.2f}\\pm {float(entry[2]):.2f}$\nObs. Data: {np.ceil(float(entry[3])):.0f}",
            stacked_values
        ))
    

    fig = plt.figure(figsize=(24/0.9, 25))
    ax = plt.subplot(111)
    hep.cms.label("Supplementary", loc=0, ax=ax, data=True, lumi=138)

    for key in objects_to_draw:
        values = data[key]/mc_sum
        if key == "TotalSig":
            key = "ttH"
        info = plot_config.get(key, {}).get("info", {})
        color = info.get("color", next(default_color_iterator))
        # check if color is a ROOT color
        if isinstance(color, int):
            color = gROOT.GetColor(color).AsHexString()
        label = r"${}$".format(info.get("label", key).replace("#", "\\"))

        
        ax.barh(final_xlabels, values, edgecolor="black", left=bottom, color=color, label=label)
        bottom += values

    ax.set_xlabel("Fraction of events")
    plt.subplots_adjust(left=0.15, right=0.85, top=0.9, bottom=0.13)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    for ext in extensions:
        outname = f"{output_path}.{ext}"
        print(f"Saving {outname}")
        plt.savefig(outname)

def prepare_inputs(inputs, category_names=None, ordered_categories=None) -> dict[str, Any]:
    """Function to prepare input for later processing.

    Inputs should be a list of JSON files containting event yields in the following
    format:

    ```json
    {
        "categories": [cat1, cat2, ...],
        "yields": {
            "process1": [yield1, yield2, ...],
            "process2": [yield1, yield2, ...],
            ...
        }
    }
    ```

    Note that the order of categories should be the same as in the list of yields.
    If ordered_categories is provided, the function will sort the yields accordingly.
    Note that this also filters out any categories not present in ordered_categories.

    :param inputs: List of paths to JSON files containing event yields
    :param category_names: Optional dictionary containing the category clear names
    :param ordered_categories: Optional list of categories specifying the order
        and list of categories to use for plotting, defaults to None
    :return: dictionary containing the event yields
    """    
    data = {
        "categories": [],
        "yields": dict(),
    }
    input_pbar = tqdm(inputs, desc="Loading inputs")
    for i, input_file in enumerate(input_pbar):
        input_pbar.set_description(f"Processing file {i}")
        with open(input_file, "r") as f:
            input_data = json.load(f)
            if not "categories" in input_data:
                raise KeyError(f"No categories found in input file {input_file}")

            if any(x in data["categories"] for x in input_data["categories"]):
                raise ValueError(f"Duplicate categories found in input file {input_file}")
            data["categories"] += input_data["categories"]


            yield_data = data["yields"]
            for key, yield_list in input_data["yields"].items():
                if not key in yield_data and not i == 0:
                    raise KeyError(f"Process {key} not found in first input file")
                yield_data[key] = yield_data.get(key, []) + yield_list
            data["yields"].update(yield_data)

    # after merging the input files, convert to numpy arrays
    data["categories"] = np.array(data["categories"])
    for key, value in data["yields"].items():
        data["yields"][key] = np.array(value)

    if ordered_categories:
        order_index = np.array(list(map(
            lambda x: input_data["categories"].tolist().index(x) 
                if x in input_data["categories"] 
                else np.nan,
            cat_order
        )))
        # filter out any categories not present in ordered_categories
        order_index = order_index[~np.isnan(order_index)]
        # apply the ordering to the categories and yields
        data["categories"] = data["categories"][order_index]
        for key, value in data["yields"].items():
            data["yields"][key] = value[order_index]
    
    # finally, apply the category names if provided
    def parse_root_tex(tex_str):
        return r"$\bf{{{}}}$".format(tex_str.replace("#", "\\"))

    def build_final_category_name(cat):
        name = parse_root_tex(cat)
        if cat in category_names:
            subdict = category_names[cat]
            name = "\n".join(list(map(
                parse_root_tex,
                [subdict.get("top", cat), r"\text{{{}}}".format(subdict.get("bottom", ""))]
            )))
        return name

    if category_names:
        data["categories"] = np.array(list(map(
            build_final_category_name,
            data["categories"]
        )))
    return data

def main(*args, **kwargs):
    config = load_keyword(kwargs, "config")
    plot_config = init_module(config)
    draw_total = load_keyword(kwargs, "draw_total")
    extensions = load_keyword(kwargs, "extensions")
    output = load_keyword(kwargs, "output")
    inputs = load_keyword(kwargs, "inputs")
    draw_objects = load_keyword(kwargs, "draw_objects")
    category_config_path = load_keyword(kwargs, "label_config")
    with open(category_config_path, "r") as f:
        category_names = json.load(f)
    # from IPython import embed; embed(header="Starting main")
    
    data = prepare_inputs(inputs, category_names=category_names)

    draw_yield_bar_chart(
        yields_dict = data,
        output_path = output,
        objects_to_draw = draw_objects,
        draw_total = draw_total,
        extensions = extensions,
        plot_config = plot_config.samples,
    )
    

if __name__ == '__main__':
    args = parse_arguments()
    main(**vars(args))