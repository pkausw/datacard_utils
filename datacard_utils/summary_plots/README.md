# Create summary plots and tables

Before you get started, you should

- do the [standard fit tests](https://gitlab.cern.ch/ttH/datacards/-/tree/master/utilities/fittings_scripts)
- [collect the results](https://gitlab.cern.ch/ttH/datacards/-/blob/master/utilities/README.md#usage-of-collect_all_resultspy)

## Step 1: Collect fit results in final format

After collecting the results for the different combinations, you should have one .json file per combination.
You can use `translate_to_result_json.py` to create a source file with a better format to create the summary plots and tables.
For more information about the input the script needs, please use `translate_to_result_json.py -h`.

The script has to options:

- `c`: path to the config which contains the clear names, what parameters to use and the order in which they should be displayed. You can use the options in this directory:
  - `naming_config_nominal_fits.py`: config to display channels `SL`, `DL` and `FH` as well as the combination. Use this config for the final version of the table/plot.
  - `naming_config_nominal_fits_internal.py`: config with additional output, e.g. `DL+SL`
  - `naming_config_packaged_fits.py`: config to display the results where nuisances are fully correlated across the channels but each channel has its own POI. Use this config to create lines for `Combined (multi POI)` part in the final table.
  - `naming_config_stxs.py`: config for STXS summary plot/table
- `o`: path to output.json file containing the final data format

## Step 2: Create plot and table

After applying the required data format, you can use `bestFit.py` to draw the plot and create the table.
Please use `bestFit.py -h` to get an overview of the options in place.

The required options are:

- `j`: path to the output.json file from Step 1
- `o`: name of the files to output. The extensions `.pdf`, `.png` and `.tex` are appended automatically

There are also a number of style options in case you want to adjust the style (default options should be fine).
Don't forget to provide one of these lumi label with `-l`, depending on the year you want to display:

- 2016: 36.3
- 2017: 41.5
- 2018: 59.7
- all years: 138

If you are creating summary plots for the standard ttH or STXS combination fits, you can use the following wrapper scripts:

- standard ttH interpretation: [create_all_results.sh](create_all_results.sh)
- STXS interpretation: [create_all_results_STXS.sh](create_all_results_STXS.sh)
