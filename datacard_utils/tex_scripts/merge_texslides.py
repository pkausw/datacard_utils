import os
import sys
import json


def merge_files(infos1, infos2):
    lines = []
    path1 = infos1["path"]
    path2 = infos2["path"]

    



    return lines

def main(args = sys.argv[1:]):
    path_to_config = args[0]
    output_path = args[1]
    if not os.path.exists(path_to_config):
        sys.exit("Could not find file '%s'!" % path_to_config)
    if not path_to_config.endswith("json"):
        sys.exit("Input needs to be .json file!")

    with open(path_to_config) as f:
        config = json.load(f)

    lines = []
    f1 = config["info"][0]["path"]
    f2 = config["info"][1]["path"]
    print f1
    print f2

    lines = merge_files(infos1 = config["info"][0], infos2 = config["info"][0])




if __name__ == '__main__':
    main()