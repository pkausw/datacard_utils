Script to produce prefit and postfit plots based on the combine output

You need
1) `fitDiagnostics.root` containing the shapes and error bands. So you need to call combine with 
`--saveShapes --saveWithUncertainties`. For more information, check out the [combine documentation](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/part3/nonstandard/#plotting)
2) the `plotconfig` which contains information about how to draw what. `PlotScript.py` can also generate an example config, see help function

3) If you want the proper x-axis shown instead of anonymus numbering you also need to provide the path to the datacard belonging to the fit result file. The script will take the x-axis from the `data_obs` object belonging to the datacard

For more options you can set, such as titles, logarithmic y-axis, labels printed on the canvas, etc., please consult `PlotScript.py -h`. You can specify the options either in your `plotconfig` or as options at runtime.

The script has been tested for datacards from UHZ, DESY, Cornell and KIT and yielded correct plots in all cases.

If you want to produce prefit distributions with uncertainty bands, you can e.g. use

```bash
python PlotScript.py -p plotconfig.py --combineflag prefit -r path/to/fitDiagnostics.root --channelname CHANNEL_YOU_WANT_TO_DRAW --combineDatacard path/to/datacard.txt
```
, where `CHANNEL_YOU_WANT_TO_DRAW` is the name of the channel you would like to draw as specified in the corresponding datacard.
