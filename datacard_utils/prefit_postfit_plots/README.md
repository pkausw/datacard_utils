# Generate prefit and postfit plots

This README should give you an idea how to produce prefit and post plots.

## Generate the shapes to draw

In principle, there are two ways to generate the shapes that you'd like to draw.

You can use `combine`'s `FitDiagnostics` method to produce the shapes directly when you're running the fit.
To do this, add the options `--saveShapes --saveWithUncertainties`.
For more information, check out the [combine documentation](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#plotting).
Note that this way usually takes a significant amount of time, depending on the size of the workspace and the number of toys you use to generate the post-fit templates with uncertainties.

If you already have a file containing a `RooFitResult` object, e.g. `fit_s` in `fitDiagnostics.root`, but didn't produce the shapes yet, you can use `PostFitShapesFromWorkspace` from the `CombineHarvester` package.
If you have run `FitDiagnostics`, you can generate the shapes e.g. with this command:

```bash
PostFitShapesFromWorkspace -w path/to/workspace.root -d .path/to/datacard.txt -f fitDiagnostics.root:fit_s --postfit --sampling --samples 300 --skip-proc-errs -o outputfile.root
```

For more information, checkout the [`CombineHarvester` documentation](http://cms-analysis.github.io/CombineHarvester/post-fit-shapes-ws.html)

### Parallelize the shape generation

You can parallelize the shape generation if you create workspaces for the individual categories.
**Important**: The parameter names have to be *exactly* like they are in the fit results file you want to use for the post-fit shape generation.
Otherwise, the mapping of parameters will not work correctly.

You can generate such workspaces with the setup in the datacards repo with this recipe:

- when using `makeCombinedCards.py`, specify the option `-i`. This will create datacards for the individual categories with the correct naming
- if you want to use the full Run-II fit results, you should create a full Run-II workspace for the categories. You can do this with `build_cards_across_years.py` if you use the option `-a`

After creating suitable workspaces, you can use `submit_shape_generation.py` to create the pre-fit and post-fit shapes.
Please have a look at the help function of the script for more information.

**Important**: The current version of the script will only work correctly with [this](https://github.com/pkausw/CombineHarvester/tree/HIG-19-011) fork of the CombineHarvester (branch `HIG-19-011`)!
The PR to the main version is currently ongoing.

## Generate the plots

You can generate plots with [PlotScript.py](./PlotScript.py). You need

1) the .root file containing the shapes you'd like to plot (`input.root`)
2) the `plotconfig` which contains information about how to draw what. `PlotScript.py` can also generate an example config, see help function
3) If you want the proper x-axis shown instead of anonymus numbering you also need to provide the path to the datacard belonging to the fit result file. The script will take the x-axis from the `data_obs` object belonging to the datacard

For more options you can set, such as titles, logarithmic y-axis, labels printed on the canvas, etc., please consult `PlotScript.py -h`. You can specify the options either in your `plotconfig` (e.g. [plotconfig_FHCRs.py](./plotconfig_FHCRs.py)) or as options at runtime.

The script has been tested for datacards from UHZ, DESY, Cornell and KIT and yielded correct plots in all cases.

If you want to produce prefit distributions with uncertainty bands, you can e.g. use

```bash
python PlotScript.py -p plotconfig.py --combineflag shapes_prefit -r path/to/input.root --channelname CHANNEL_YOU_WANT_TO_DRAW --combineDatacard path/to/datacard.txt
```

, where `CHANNEL_YOU_WANT_TO_DRAW` is the name of the channel you would like to draw as specified in the corresponding datacard.

If you would like to produce the plots for all channels in one go, you can also use the wrapper `draw_prefit_postfit.py`.
You need to provide a .json file containing the labels to draw (e.g. [this](./config_labels_other_SL_cats.json) file in this repo) and the plotconfig to be parsed to the `PlotScript` (e.g. [plotconfig_FHCRs.py](./plotconfig_FHCRs.py)).
For more options, please have a look at the help function of the wrapper.

To draw prefit and postfit plots for the respective channels, you can use `../PreFitPostFitPlots/draw_prefit_postfit.py`.
Example:

```bash
python draw_prefit_postfit.py -l config_labels_other_SL_cats.json -p plotconfig_FHCRs_blinded.py -s path/to/file/with/prefitpostfit_shapes.root -d path/to/original/datacard
```

You can also use [draw_prefit_postfit.py](./draw_prefit_postfit.py) to draw the full Run-II distributions using the option `--total`.
Note that when producing these distributions with the CombineHarvester, the "usual" naming scheme is broken and the distributions are located in a folder called e.g. `total_prefit`.
In order to match the entry in the `labels_config` file, the name of the source file name must include the key in the config.
For example, if you want to draw something with the options specified under the key `OBSERVABLE_NAME_1`, the .root file containing the distributions must contain `OBSERVABLE_NAME_1` in its name (e.g. `some_prefix_OBSERVABLE_NAME_1_some_suffix.root`).
The final plot is then saved as e.g. `OBSERVABLE_NAME_1_prefit.pdf` for prefit distributions.

For additional information about the different options, please have a look at `python ../PreFitPostFitPlots/draw_prefit_postfit.py -h`

If you are working on standard combinations (either inclusive or STXS), you can use the wrapper scripts:

- standard inclusive ttH: `draw_all_plots.sh`
- standard STXS: `draw_all_plots_STXS.sh`
