# Uncertainty Breakdowns

## Step 1 Submit Uncertainty Breakdowns
You can generate a breakdown for different uncertainty groups by using the script `breakdown_uncertainties.py`.
It's based on [the combine reference page](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/index.html) and [this presentation](https://indico.cern.ch/event/747340/contributions/3198653/attachments/1744339/2823486/HComb-Tutorial-FitDiagnostics.pdf).
The script will generate a folder for each ROOT workspace it's given. Afterwards, it will generate
- `.sh` files for the different fits that are to be done
- subfolders for the different breakdowns
For more information, please have a look at the help functionality of the script.
You can call the script for example by using

```
python breakdown_uncertainties.py -a "--cminDefaultMinimizerTolerance 1e-2 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerPrecision 1e-12 --X-rtd MINIMIZER_analytic" --murange 10 -b all:thy:exp:bgnorm_ttX=allConstrainedNuisances,'var{.*bgnorm_tt.*}' -s test -f path/to/workspace.root
```

Things to keep in mind:
- In order to unsure a maximum compatibility with the nominal fit, you should use the same combine options as in the nominal fit by using the option `-a`
- The option `--murange` in combination with the option `--mu` will generate a symmetric fit interval for the signal strength with the width `2*murange` and the center at the expected signal strength `mu`
- The input for option `-b` are the names of the uncertainty groups as defined in the datacard/workspace. To generate a breakdown for the autoMCStat uncertainties, use the group `autoMCStats` (see [the combine reference page](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/bin-wise-stats.html)). You can also define groups on the fly with the syntax `GROUPNAME=LIST,OF,PARAMETERS,TO,FREEZE`. The syntax to freeze nuisances is the same as in the standard combine fit and will be parsed to the fitting routing (e.g. the example above will freeze all constrained nuisances and additionally the freely-floating bgnorm rateParams for ttbb and ttcc). Use `:` as separator for groups.
- The option `-f` will skip the generation of likelihood scans, which greatly enhances the runtime


## Step 2 Collect Results of Uncertainty Breakdowns
You can use the script `collect_breakdown_results.py` to collect the results from fits submitted above.
You can use the script for example like this:
```
python collect_breakdown_results.py -o OUTPUT_FILENAME -f '*bestfit*:*breakdown_*' -c /path/to/config.py -a [input-files]
```
The script offers a help function with more information regarding the different options available. Here is a short summary
- `-o`: name of the output .json file
- `-f`: wildcards to filter files from the list of input-files. Currently, the identification of the total uncertainty relies on the keyword `bestfit`, which should consequently also be in the name of the file containing the nominal bestfit.
- `-c`: path to the config file which contains the function to get the uncertainty group name. An exemplary config file is `config_breakdowns.py`
- `-a`: produce the asymmetric uncertainty splitting

The input files are all files that you want to consider in the collection.
Normally, you want to consider all files produces in Step 1.
You should be able to do that by using `*bestfit*.root breakdown_*/*.root` in the directory that is created for a given workspace.

## Step 3 Create Table for Breakdowns

You can use `create_breakdown_table.py` to produce a latex table from the .json file created in Step 2.

```
python create_breakdown_table.py -c config_breakdowns.py -f tex path/to/file.json
```

The config is used to determine the order of the entries and should contain either a `list` or an `OrderedDict` object.
For more information, please use the `-h` option.