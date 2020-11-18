# Generate bias tests

You can generate bias tests using `generate_bias_tests.py`.
The help function should give a some idea what the script can do and what you need to provide.

## Generate Poisson distributed toys
In order to generate a test with Poisson distributed toys around the MC prediction, you can do

```
python generate_bias_tests.py -d PATH/TO/WORKSPACE.root -o OUTPUT/PATH -n 500 --addToyCommand "--toysNoSystematics" --addFitCommand "--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 1e-2 --cminFallbackAlgo Minuit2,Migrad,1:1e-2 --X-rtd MINIMIZER_analytic"
```

Some comments:
  - `PATH/TO/WORKSPACE.root` is the path to the workspace you want to use in the fit to your toys. By default, this workspace is also used to generate the toys
  - `OUTPUT/PATH` is the path where the script will generate a folder per signal strength and a temp folder.
    - the `temp` folder contains the shell scripts and the submit script for the HTCondor system. There is one shell script that generates folders for the individual toys and calls `generateToysAndFits.sh`. The latter contains the `combine` commands to generate toys and do the fits.
    - the signal strength folders contain one folder for the `Asimov` toy and folders for each of the randomly-generated toys
  - `--addToyCommand`: put here all `combine` commands that you want to consider for the toy generation.
  - `--addFitCommand`: put here all `combine` commands that you want to consider in the fit. Ideally, you should use the same options you use in the normal fits you do
  - You can control the number of generated toys with the `-n` option and can also manipulate how many toys you want to generate per batch job. Please have look at the help function!

## Generate Poisson distributed toys with specific parameter setup

If you'd like to generate toys with a different parameter setup, e.g. scale ttbb by X percent, simply add a `--setParameters` statement to the `--addToyCommand` option.
To scale ttbb by 30%, add `--setParameters CMS_ttHbb_bgnorm_ttbb=1.3`.

## Generate Poisson distributed toys from different workspace

If you want to generate toys from a different workspace, e.g. for a different ttbb model, you can use the `--scaledDatacard` option.
Please read the help function for more information!