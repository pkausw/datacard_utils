import os
import sys
import json
import imp

from optparse import OptionParser


def create_entry(filepath, naming):
    results = {}
    try:
        with open(filepath) as f:
            input_data = json.load(f)
    except:
        raise ImportError("Could not load data from file '{}'".\
            format(filepath))
    combname, end = os.path.basename(filepath).split("__")
    print(combname)
    comb_translation = naming.get(combname, {})
    for param in input_data:
        translated_name = comb_translation.get(param)
        if translated_name:
            print("\tsaving results for '{}'".format(translated_name))
            results[translated_name] = input_data[param]
    return results

def load_config(configpath):

    try:
        config = imp.load_source('config', configpath)
    except:
        raise ValueError("Could not load path to config.py file!")

    return config
    
def load_property(config, prop):
    final_prop = None
    s = "{}.{}".format("config", prop)
    try:
        final_prop = eval(s)
    except:
        print("Could not load dict '{}' from config file".\
            format(prop))
    if final_prop:
        print(json.dumps(final_prop, indent = 4))

    return final_prop


def main(*files, **kwargs):
    configpath = kwargs.get("configpath")
    config = load_config(configpath)
    naming = load_property(config, "naming")
    if not naming:
        raise ImportError("Fatal error")

    outname = kwargs.get("outname", "outname.json")

    final_dict = {}
    final_dict["results"] = {}
    for fpath in files:
        if not os.path.exists(fpath):
            print("Could not find file '{}', skipping".format(fpath))
            continue
        if not fpath.endswith(".json"):
            print("File '{}' is not a json file, skipping".format(fpath))
            continue
        entry = create_entry(filepath = fpath, naming = naming)
        final_dict["results"].update(entry)
    # load optional order, labels
    order = load_property(config, "order")
    if order:
        final_dict["order"] = order
    labels = load_property(config, "labels")
    if labels:
        final_dict["labels"] = labels
    print(json.dumps(final_dict, indent = 4))
    with open(outname, "w") as f:
        json.dump(final_dict, f, indent = 4)
    


def parse_arguments():

    usage = """
    Script to translate the results from multiple json files
    with bestfits, stat-only and significance results into
    json which can be used to create result tables and mu plots.

    Required input: config.py which contains dictionary of form
    naming = {
        combination name : {
            param name : clear name in table/mu plot,
            ...
        },
        ...
    } 

    usage: python %prog [options] path/to/jsons/to/read/from.json
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--output",
                        help = " ".join("""
                        path to the file in which to save the results
                        """.split()),
                        dest = "outname",
                        metavar = "path/to/output.json",
                        type = "str"
                    )
    parser.add_option("-c", "--config",
                        help = " ".join("""
                        path to config.py containing naming details
                        """.split()),
                        dest = "configpath",
                        metavar = "path/to/config.py",
                        type = "str"
                    )

    options, args = parser.parse_args()

    if options.configpath is None or not os.path.exists(options.configpath):
        parser.error("You need to provide a path to a valid .py file")

    if options.outname is None:
        parser.error("You need to provide an output path!")

    return options, args

if __name__ == "__main__":
    options, files = parse_arguments()

    main(*files, **vars(options))
