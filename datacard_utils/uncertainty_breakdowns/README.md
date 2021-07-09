# Uncertainty Breakdowns

## Submit Uncertainty Breakdowns
You can generate a breakdown for different uncertainty groups by using the script `breakdown_uncertainties.py`.
It's based on [the combine reference page](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/index.html) and [this presentation](https://indico.cern.ch/event/747340/contributions/3198653/attachments/1744339/2823486/HComb-Tutorial-FitDiagnostics.pdf).
The script will generate a folder for each ROOT workspace it's given. Afterwards, it will generate
- `.sh` files for the different fits that are to be done
- subfolders for the different breakdowns
For more information, please have a look at the help functionality of the script.
You can call the script for example by using

```
python breakdown_uncertainties.py -a "--cminDefaultMinimizerTolerance 1e-2 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerPrecision 1e-12 --X-rtd MINIMIZER_analytic" --murange 10 -b all,thy,exp -s test -f path/to/workspace.root
```

Things to keep in mind:
- In order to unsure a maximum compatibility with the nominal fit, you should use the same combine options as in the nominal fit by using the option `-a`
- The option `--murange` in combination with the option `--mu` will generate a symmetric fit interval for the signal strength with the width `2*murange` and the center at the expected signal strength `mu`
- The input for option `-b` are the names of the uncertainty groups as defined in the datacard/workspace. To generate a breakdown for the autoMCStat uncertainties, use the group `autoMCStats` (see [the combine reference page](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part2/bin-wise-stats.html))
- The option `-f` will skip the generation of likelihood scans, which greatly enhances the runtime


## Collect Results of Uncertainty Breakdowns
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
