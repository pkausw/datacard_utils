# create prefit/postfit yield tables

In order to obtain prefit/postfit yield tables with meaningfull uncertainties, you should make sure that

- the fit you performed has a positive-definite covariance matrix
- you have generated the shapes according to the documentation [here](../PreFitPostFitPlots/README.md#generate-prefit-and-postfit-plots), using the option `-y` (which is the default at the moment).

## Workflow

When producing the prefit and postfit shapes with the scripts in this repository and using the [fork](https://github.com/pkausw/CombineHarvester/tree/HIG-19-011) of the CombineHarvester, you should have .root file(s) with a directory for each of the channels you have produced templates for.
Apart from the templates, you will find `RooRealVar` objects that begin with `yield_*`, which contain the yield as values and the correct uncertainties under consideration of the covariance matrix.

You can then use [get_yields.py](get_yields.py) to create the prefit/postfit yield tables like this:

```bash
python path/to/eventyields/get_yields.py -c path/to/config.py -s 1 -i OUTPUT_SHAPES.root -m MODE --prefix PREFIX -o output_tag --drawFromHarvester
```
Explanation:

- `path/to/config.py` is the path to the config with information about your model (e.g. [this file](./yields_config_HIG-19-011_SL_5j_no_tH_harvester.py)). The files here in this repository should give you a hint of the structure. A config should contain

  - the list of processes to consider
  - the tex code for the processes
  - the list of categories to consider
  - the tex code for the categories
  - the names of the total background and total signal templates in your input file

- the `-s` option will scale the signal templates. Set this to `0` to effectively blind the yield tables, otherwise leave it at `1`.
- `OUTPUT_SHAPES.root` is the output of the `PostFitShapesFromWorkspace` step
- the `prefix` option can be used if you have categories that differ due to a prefix, e.g. `ttH_2016_ljets_ge6j_ge4t` and `ttH_2017_ljets_ge6j_ge4t`. You can then specify `ljets_ge6j_ge4t` in your config and switch between the different categories by specifing the `prefix`
- the output tag is prependen before the category name as specified in the config

All this is already implemented in the following wrapper scripts

- standard ttH interpretation: [do_yield_tables.sh](./do_yield_tables.sh)
- STXS interpretation: [do_yield_tables_STXS.sh](./do_yield_tables_STXS.sh)

