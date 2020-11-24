# Generate prefit and postfit plots

This README should give you an idea how to produce prefit and post plots.

## Generate the shapes to draw

In principle, there are two ways to generate the shapes that you'd like to draw.

You can use `combine`'s `FitDiagnostics` method to produce the shapes directly when you're running the fit.
To do this, add the options `--saveShapes --saveWithUncertainties`.
For more information, check out the [combine documentation](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#plotting)

If you already have a file containing a `RooFitResult` object, e.g. `fit_s` in `fitDiagnostics.root`, but didn't produce the shapes yet, you can use `PostFitShapesFromWorkspace` from the `CombineHarvester` package.
If you have run `FitDiagnostics`, you can generate the shapes e.g. with this command:

```bash
PostFitShapesFromWorkspace -w path/to/workspace.root -d .path/to/datacard.txt -f fitDiagnostics.root:fit_s --postfit --sampling --samples 300 --skip-proc-errs -o outputfile.root
```

For more information, checkout the [`CombineHarvester` documentation](http://cms-analysis.github.io/CombineHarvester/post-fit-shapes-ws.html)

## Generate the plots

You need
1) the .root file containing the shapes you'd like to plot (`input.root`)
2) the `plotconfig` which contains information about how to draw what. `PlotScript.py` can also generate an example config, see help function
3) If you want the proper x-axis shown instead of anonymus numbering you also need to provide the path to the datacard belonging to the fit result file. The script will take the x-axis from the `data_obs` object belonging to the datacard

For more options you can set, such as titles, logarithmic y-axis, labels printed on the canvas, etc., please consult `PlotScript.py -h`. You can specify the options either in your `plotconfig` or as options at runtime.

The script has been tested for datacards from UHZ, DESY, Cornell and KIT and yielded correct plots in all cases.

If you want to produce prefit distributions with uncertainty bands, you can e.g. use

```bash
python PlotScript.py -p plotconfig.py --combineflag shapes_prefit -r path/to/input.root --channelname CHANNEL_YOU_WANT_TO_DRAW --combineDatacard path/to/datacard.txt
```
, where `CHANNEL_YOU_WANT_TO_DRAW` is the name of the channel you would like to draw as specified in the corresponding datacard.

If you would like to produce the plots for all channels in one go, you can also use the wrapper `draw_prefit_postfit.py`.
You need to provide a .json file containing the labels to draw (e.g. `config_labels.json` in this repo) and the plotconfig to be parsed to the `PlotScript` (e.g. `plotconfig_FHCRs_blinded.py`).
For more options, please have a look at the help function of the wrapper.
