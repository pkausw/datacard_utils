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
# obtained from CMSSW and combine
from ROOT import gROOT
from HiggsAnalysis.CombinedLimit.tool_base import rounding

# setup CMS style for matplotlib
hep.style.use("CMS")

from matplotlib.colors import ListedColormap
petroff10 = ListedColormap([
    "#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6", "#a96b59",
    "#e76300", "#b9ac70", "#717581", "#92dadd",
])

default_color_iterator = iter(petroff10.colors)

default_objects = [
    "ttlf", "ttcc", "ttbb", "singlet", "vjets", "ttbarV", "diboson",
    "ttbarGamma", "multijet", "tHq", "tHW", "TotalSig", 
]

sl_node_order = [
    "ttlf_node", "ttcc_node", "tt2b_node", "tHq_node", "tHW_node", 
    "ttH_ttmb_ratioObservable",
]

dl_node_order = [
    "ttlf", "ttcc", "ttHbb_ratioObservable"
]

default_category_order = (
    [
        "fh_j7_t4_DNN_Node0", "fh_j8_t4_DNN_Node0", "fh_j9_t4_DNN_Node0"
    ] + [
        f"ljets_{jet_cat}j_ge4t_{node}"
            for jet_cat in ["5", "ge6"]
            for node in sl_node_order
    ] + [
        "ttH_hbb_13TeV_dl_3j3b_ttHbb",
    ] + [
        f"ttH_hbb_13TeV_dl_4j3b_DNN_{node}"
            for node in dl_node_order
    ]
)

def parse_arguments():
    parser = ArgumentParser()
    usage_group = parser.add_argument_group("Options for basic usage")
    usage_group.add_argument(
        "inputs", type=str, nargs="+",
        help="Input JSON files containing event yields",
    )
    usage_group.add_argument(
        "-o", "--output", type=str, required=True,
        help="Path to output file (without extension)",
    )
    usage_group.add_argument(
        "-e", "--extensions", type=str, nargs="+", default=[],
        help="File extensions to save. Default: pdf, png",
    )
    usage_group.add_argument(
        "-d", "--draw-total", action="store_true",
        help="If true, draw the total MC and observed data yields under category name",
    )
    usage_group.add_argument(
        "-c", "--config", type=str, default=None,
        metavar="path/to/config.py",
        help="Path to configuration file with style settings for processes",
    )
    usage_group.add_argument(
        "-l", "--label-config", type=str, default=None,
        metavar="path/to/cateorgy_label_config.json",
        help="Path to configuration file for category labels",
    )
    usage_group.add_argument(
        "--draw-objects", type=str, nargs="+", default=default_objects,
        help="Objects to draw in the bar chart. Default: {}".format(", ".join(default_objects)),
    )
    usage_group.add_argument(
        "--draw-categories", type=str, nargs="+", default=default_category_order,
        dest="ordered_categories",
        help="Objects to draw in the bar chart. Default: {}".format(", ".join(default_category_order)),
    )
    window_group = parser.add_argument_group("Options for window styling")
    window_group.add_argument(
        "--window-height", type=float, default=4.8*19,
        help=f"Window height is set as n_categories * scale_window_height. Default: {4.8*19:.2f}",
    )
    window_group.add_argument(
        "--window-width", type=float, default=50.,
        help=f"Window width is set as n_categories * scale_window_width. Default: {50.:.2f}",
    )
    window_group.add_argument(
        "--margin-left", type=float, default=0.25,
        help="Set left margin of window to this fraction. Default: 0.25",
    )
    window_group.add_argument(
        "--margin-right", type=float, default=0.87,
        help="Set right margin of window to this fraction. Default: 0.87",
    )
    window_group.add_argument(
        "--margin-top", type=float, default=0.95,
        help="Set top margin of window to this fraction. Default: 0.95",
    )
    window_group.add_argument(
        "--margin-bottom", type=float, default=0.05,
        help="Set bottom margin of window to this fraction. Default: 0.05",
    )
    scaling_group = parser.add_argument_group("Options for scaling text in figure")
    scaling_group.add_argument(
        "--scale-legend", type=float, default=4.5,
        help="Legend font size is set as n_categories * scale_legend. Default: 4.5",
    )
    scaling_group.add_argument(
        "--scale-ticks", type=float, default=3.6,
        help="Tick font size is set as n_categories * scale_ticks. Default: 3.6",
    )
    scaling_group.add_argument(
        "--scale-x-title", type=float, default=5.2,
        help="Title for x-axis font size is set as n_categories * scale_labels. Default: 5.2",
    )
    optional_args = parser.add_argument_group("Optional arguments")
    optional_args.add_argument(
        "--additional-text", type=str, default=None,
        help="Additional text to add to the plot in the top left corner (e.g. Postfit)",
    )

    args = parser.parse_args()

    if not args.extensions:
        args.extensions = ["pdf", "png"]
    
    if not args.draw_objects:
        args.draw_objects = default_objects
    return args

def roundUnc(unc, method="Publication", prec=None):
    """By default, rounds uncertainty 'unc' according to the PDG rules plus one significant digit ("Publication").

    Optionally it rounds according with 'method':
        - "PDG" applies the PDG algorithm
        - "Publication" is like "PDG" with an extra significant digit (for results that need to be combined later)
        - "OneDigit" forces one single significant digit (useful when there are multiple uncertainties that vary by more than a factor 10 among themselves)

    Returns a tuple with (uncString, uncMagnitude), where magnitude is the power of 10 that applies to the string to recover the uncertainty.

    """

    # PDG rules (from the Introduction, Section 5.3)
    #
    # Uncertainty leading digits in range:
    #  100 to 354 -> keep 2 digits
    #  355 to 949 -> keep 1 digit
    #  950 to 999 -> keep 2 digits, rounding up to 1000 (e.g. 0.099 -> 0.10, not 0.1)

    uncDigs, uncMagnitude = rounding.getDigsMag(unc)

    # prec = 1
    unc3Digs = int(round(100 * uncDigs))

    if not prec:
        prec = 1
        if method == "SingleDigit":
            pass
        elif method == "PDG" or method == "Publication":
            if method == "Publication":
                prec += 1
            if 100 <= unc3Digs <= 354:
                prec += 1
        else:
            raise TypeError('Unknown precision method ("%s")' % method)
    else:
        prec = int(prec)
        # print(f"Using precision {prec}")
        

    uncStr = rounding.matchPrec(uncDigs, str(10 ** int(1 - prec)))

    # put String in integer form
    uncString = str((rounding.Decimal(uncStr) * (10 ** int(prec - 1))).quantize(rounding.Decimal("1")))
    uncMagnitude -= prec - 1

    return (uncString, uncMagnitude)

def draw_yield_bar_chart(
    yields_dict: dict[str, np.ndarray],
    output_path: str,
    objects_to_draw: list[str],
    plot_config: dict[str, Any] = None,
    extensions: list[str] = ["pdf", "png"],
    draw_total: bool = True,
    scale_legend: float = 4.5,
    scale_ticks: float = 3.6,
    scale_x_title: float = 5.2,
    margin_left: float = 0.25,
    margin_right: float = 0.87,
    margin_top: float = 0.95,
    margin_bottom: float = 0.05,
    window_height: float = 4.8*19,
    window_width: float = 50.,
    additional_text: str or None = None,
    **kwargs,
) -> None:
    """
    """
    data = yields_dict["yields"]
    keys = list(data.keys())
    shape = data[keys[0]].shape
    final_xlabels = yields_dict["categories"]
    n_cats = final_xlabels.shape[0]
    bottom = np.zeros(n_cats)
    mc_sum = np.sum((data[x] for x in objects_to_draw), axis=0)
    if not plot_config:
        plot_config = dict()

    
    if draw_total:
        stacked_values = np.column_stack((
            final_xlabels,
            data["TotalProcs"],
            data["TotalProcs_err"],
            data["data_obs"],
        ))
        def PubRoundSym(val, unc):
            """Rounds a value with a single symmetric uncertainty according to the PDG rules and calculates the order of magnitude of both.

            Returns (valStr, [uncStr], uncMag)

            """

            assert unc > 0
            uncStr, uncMag = roundUnc(unc, prec=2)
            valStr = rounding.matchPrec(val / pow(10, uncMag), uncStr)
            return (valStr, [uncStr], uncMag)

        def build_summary_str(entry):
            val = float(entry[1])
            err = float(entry[2])
            round_val, round_err, magnitude = PubRoundSym(val, err)
            final_val = float(round_val) * 10**magnitude
            final_err = float(round_err[0]) * 10**magnitude                
            return (f"{entry[0]}\n"
                f"Total: ${final_val:.0f}\\pm"
                f"{final_err:.0f}$\n"
                f"Data: {np.ceil(float(entry[3])):.0f}"
            )

        final_xlabels = list(map(
            build_summary_str,
            stacked_values,
        ))

    fig = plt.figure(figsize=(window_width, window_height))
    ax = plt.subplot(111)
    exptext, expsuffix, supptext = hep.cms.label(
        "Supplementary",
        loc=0, ax=ax, data=True, lumi=138,
        fontsize=4.5*n_cats,
    )

    expsuffix._y = 1.001

    for key in objects_to_draw:
        values = data[key]/mc_sum
        if key == "TotalSig":
            key = "ttH"
        info = plot_config.get(key, {}).get("info", {})
        color = info.get("color", None)
        if not color:
            print(f"Color not found for process {key}, using default")
            color = next(default_color_iterator)
        # check if color is a ROOT color
        if isinstance(color, int):
            color = gROOT.GetColor(color).AsHexString()
        label = r"${}$".format(info.get("label", key).replace("#", "\\"))

        
        ax.barh(
            final_xlabels, values, edgecolor="black", left=bottom, color=color,
            label=label)
        bottom += values

    ax.set_xlabel("Fraction of events", fontsize=scale_x_title*n_cats)
    # fine tune styling of the plot
    # increase size of ticks labels
    plt.yticks(fontsize=scale_ticks*n_cats)
    plt.xticks(fontsize=scale_ticks*n_cats)

    # remove additional padding on the y axis
    plt.margins(y=0.01)
    

    # increase padding between ticks and labels
    ax.tick_params(axis='y', which='major', pad=25)

    if additional_text:
        ax.set_ylim(None, ax.get_ylim()[1] + 0.5)

        ax.text(
            x=0.01, y=0.99, s = additional_text, ha='left', va="top", fontsize=5*n_cats,
            fontweight="bold", transform=ax.transAxes,
        )

    plt.subplots_adjust(left=margin_left, right=margin_right, top=margin_top, bottom=margin_bottom)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=scale_legend*n_cats)
    
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
            lambda x: data["categories"].tolist().index(x) 
                if x in data["categories"] 
                else np.nan,
            ordered_categories
        )))
        # filter out any categories not present in ordered_categories
        order_index = order_index[~np.isnan(order_index)].astype(int)
        
        # apply the ordering to the categories and yields
        data["categories"] = data["categories"][order_index]
        for key, value in data["yields"].items():
            data["yields"][key] = value[order_index]
    
    # finally, apply the category names if provided
    def parse_root_tex(tex_str):
        s = tex_str.replace("#", "\\")
        s = s.replace("tags", r"\ tags").replace("jets", r"\ jets")
        for num in [3, 5, 7, 8]:
            if (str(num) in s and 
                not any(f"{op} {num}" in s for op in ["geq", "leq", "gt", "lt"])
            ):
                s = s.replace(str(num), r"\ {}".format(num))
        return r"$\mathbf{{{}}}$".format(s)

    def build_final_category_name(cat):
        name = parse_root_tex(cat)
        if cat in category_names:
            subdict = category_names[cat]
            top = subdict.get("top", cat)
            bottom = subdict.get("bottom", "")
            label_list = [top]
            if bottom:
                label_list = [top, r"\text{{{}}}".format(bottom)]
            name = "\n".join(list(map(
                parse_root_tex,
                label_list,
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
    output = load_keyword(kwargs, "output")
    inputs = load_keyword(kwargs, "inputs")
    draw_objects = load_keyword(kwargs, "draw_objects")
    ordered_categories = load_keyword(kwargs, "ordered_categories")
    category_config_path = load_keyword(kwargs, "label_config")
    with open(category_config_path, "r") as f:
        category_names = json.load(f)
    # from IPython import embed; embed(header="Starting main")
    
    data = prepare_inputs(
        inputs,
        category_names = category_names,
        ordered_categories = reversed(ordered_categories),
)

    draw_yield_bar_chart(
        yields_dict = data,
        output_path = output,
        objects_to_draw = draw_objects,
        plot_config = plot_config.samples,
        **kwargs,
    )
    

if __name__ == '__main__':
    args = parse_arguments()
    main(**vars(args))