# Datacard utilities

[[_TOC_]]

## Usage of `collect_all_results.py`

`collect_all_results.py` is a wrapper script to easily collect the best-fit, stat-only fit and significance results.
Before you start, you should

- check the list of combinations that the script will look for. This is defined in a dedicated config, such as [config_collect_all_results.py](./config_collect_all_results.py).
- check the wild card expressions to load the correct files

You can then call the script like this:

```bash
python path/to/collect_all_results.py path/to/results
```

, where `path/to/results` is the top level directory containing the files that you want to reach with the wild cards.
The script will generate .json and .tex files for each combination separately, which you can use in other steps.

## Usage of the `dc_manipulator`

The `dc_manipulator` is a wrapper for the CombineHarvester package.
It is designed to perform all the modification (or just a subset of them) to the statistical models in the respective channels.
The current modifications are:

- remove JEC from minor backgrounds
- drop signal processes with < 0.1% signal contribution
- drop background processes with < 0.1% contribution
- build a binning based on the yields in individual bins of the discriminators
- coarser binning in DL and SL (scheme left)
- change uncertainties with small shape effect to lnN uncertainties
- drop lnN uncertainties with an effect of < 0.1 %

Additionally, the script will

- introduce the Higgs mass scaling
- define the nuisance groups in the datacards
- introduce the correct lumi uncertainty scheme

For a full overview over the different options available, please use `python dc_manipulator.py -h`.

Here is one example which will apply everything at once:

```bash
python path/to/dc_manipulator.py -i 'INPUT_GROUP' --apply-validation -s left --remove-minor-jec --remove-minor-bkgs
```

If you are planning on using options that change the binning of the templates, it's recommended to first apply the rebinning and then apply the validation (i.e. run the tool twice with different options).
This will make sure that the true shape effect is correctly accounted for.

The `INPUT_GROUP` clarifies how to load datacards into the CombineHarvester instance.
It relies on the functions in the CombineHarvester package to parse multiple datacards at once, which are described [here](http://cms-analysis.github.io/CombineHarvester/intro1.html#ex1-p2) in more detail.

Assume that the datacards for a given channel `CHANNEL` are ordered in the following structure:

```
CHANNEL
|
|
|----2016
|    |
|    |------datacards
|           |
|           | ---- card1.txt ...
|----2017
|    |
|    |------datacards
|           |
|           |----- card1.txt ...
| ...
```

You can define an `INPUT_GROUP` like this: `'$CHANNEL/$ERA/datacards/.*.txt:CHANNEL/201?/datacards/*.txt'`.
The first part (before the `:`) is the template after which the CombineHarvester will try to extract additional information, in this case the `$CHANNEL` and the `$ERA`, i.e. the year.
The second part is the actual wild card to the datacards you'd like to modify.
The CombineHarvester will then attribute the datacards to the channel `CHANNEL` and the given years automatically.
The modified datacards are also sorted according to the era, i.e. the year.

*IMPORTANT*: FH has a dedicated binning scheme.
Therefore, you should drop the option `-s left` when modifying FH cards.

The tool can also perform the final modifications for the STXS datacards.
You can activate this with the option `--stxs`.
This will

- remove the scaleMuR/F, ISR/FSR and QCDscale parameters for all ttH processes and
- add the migration uncertainties to the STXS bins.

The rest of the workflow is the same as for the other datacards.

You should use this script to modify basic datacards for the different input channels.
After this, you can follow the instructions in the already established work flow.

## Producing correlation matrices

Correlation matrices can be produced using the [corrMat.py](./corrMat.py) script.
This can be used like this

```bash
python corrMat.py -f FIT_RESULT_OBJECT path/to/file_with_roofitresult.root -o . -t name_config_for_nuisance.json
```

where
- `-f` specifies the name of the `RooFitResult` object in the source file. This will be
  - `fit_s` for s+b fit or `fit_b` for background-only fit if you used the `FitDiagnostics` method
  - `fit_mdf` if you used the `MultiDimFit` method
- `-o`: path to the output directory in which you want to save the files in
- `-t`: path to a config containing clear names for the parameters. This follows the conventions used for the CombineHarvester, e.g. [this config](./impact_scripts/scripts/nuisance_names.json) that is used for the impacts.

Additionally, the script requires the path to the file containing the fit results as positional arguments.

This will produce two plots: One containing the full correlation matrix, and one that only include the correlations between POIs (everything that starts with `r_`).
You can also specify a list of parameters that you want to use to construct a correlation matrix with the `-a` option.
For more information, please use the help function with `python corrMat.py -h`.
