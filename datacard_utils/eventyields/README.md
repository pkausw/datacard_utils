# create prefit/postfit yield tables

In order to obtain prefit/postfit yield tables with meaningfull uncertainties, you should make sure that
- the fit you performed has a positive-definite covariance matrix
- you have a separate workspace where all templates have one bin. You can use the [rebin distribution](https://gitlab.cern.ch/ttH/datacards/-/blob/master/utilities/manipulator_methods/rebin_distributions.py) module for this.

## Workflow

First, fit your usual complete datacard and stuff. Do save with uncertainties.
Next, transfer the post-fit nuisance values of the real fit to the 1 bin workspace like this :
```bash
PostFitShapesFromWorkspace -w WORKSPACE.root -d DATACARD.txt -o OUTPUT_SHAPES.root -m 125.38 -f path/to/fitDiagnostics.root:fit_s --postfit --sampling --print --samples 300
```
or check the [docu](http://cms-analysis.github.io/CombineHarvester/post-fit-shapes-ws.html):

Finally, you can use `get_yields.py` to create the prefit/postfit yield tables like this:
```
python $ANALYSIS/../eventyields/get_yields.py -c path/to/config.py -s 1 -i OUTPUT_SHAPES.root -m MODE --prefix PREFIX -o output_tag --drawFromHarvester
```
Explanation:
- `path/to/config.py` is the path to the config with information about your modell. The files here in this repository should give you a hint of the structure. A config should contain
  - the list of processes to consider
  - the tex code for the processes
  - the list of categories to consider
  - the tex code for the categories
  - the names of the total background and total signal templates in your input file
- the `-s` option will scale the signal templates. Use the postfit value of mu
- `OUTPUT_SHAPES.root` is the output of the `PostFitShapesFromWorkspace` step
- the `prefix` option can be used if you have categories that are differential by a prefix, e.g. `ttH_2016_ljets_ge4j_3t` and `ttH_2017_ljets_ge4j_3t`. You can then specify `ljets_ge4j_3t` in your config and switch between the different categories by specifing the `prefix`
- the output tag is prependen before the category name as specified in the config
