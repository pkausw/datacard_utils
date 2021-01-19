# Usage of the `dc_manipulator`

The `dc_manipulator` is a wrapper for the CombineHarvester package.
It is designed to perform all the modification (or just a subset of them) to the statistical models in the respective channels.
The current modifications are:
- remove JEC from minor backgrounds
- drop signal processes with < 0.1% signal contribution
- coarser binning in DL and SL (scheme left)
- change uncertainties with small shape effect to lnN uncertainties

Additionally, the script will
- introduce the Higgs mass scaling
- define the nuisance groups in the datacards
- introduce the correct lumi uncertainty scheme

For a full overview over the different options available, please use `python dc_manipulator.py -h`.

Here is one example which will apply everything at once:

```
python path/to/dc_manipulator.py -i 'INPUT_GROUP' --apply-validation -s left --remove-minor-jec
```

The `INPUT_GROUP` clarifies how to load datacards into the CombineHarvester instance.
It relies on the functions in the CombineHarvester package to parse multiple datacards at once, which are described [here](http://cms-analysis.github.io/CombineHarvester/intro1.html#ex1-p2) in more detail.

Assume that the datacards for a given channel `CHANNEL` are ordered in the following structure:

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

You can define an `INPUT_GROUP` like this: `'$CHANNEL/$ERA/datacards/.*.txt:CHANNEL/201?/datacards/*.txt'`.
The first part (before the `:`) is the template after which the CombineHarvester will try to extract additional information, in this case the `$CHANNEL` and the `$ERA`, i.e. the year.
The second part is the actual wild card to the datacards you'd like to modify.
The CombineHarvester will then attribute the datacards to the channel `CHANNEL` and the given years automatically.
The modified datacards are also sorted according to the era, i.e. the year.

*IMPORTANT*: FH has a dedicated binning scheme. 
Therefore, you should drop the option `-s left` when modifying FH cards.

You should use this script to modify basic datacards for the different input channels.
After this, you can follow the instructions in the already established work flow.