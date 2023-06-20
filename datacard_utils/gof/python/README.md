# Goodness of Fit Scripts

[[_TOC_]]

## unroll_histos.py

### Input

paths to rootfiles containing TH2 histograms that are to be converted to TH1 histos

### Output

rootfiles for each input file, respectively, which begin with `unrolled_` and then use the name of the input file

### Workflow

First, the script checks whether the input file exists.
The script loops over all keys in each input rootfile and creates for all objects that inherit from the `TH2` class a corresponding `n X m` `TH1` histo.
Here, `n` and `m` are the number of bins of the `x` and `y` axis of the input `TH2` histogram, respectively.
Afterwards, the unrolled `TH1` histograms are written to the output file.
The name of this output file is equal to the name of the input file where `unrolled_` is prepended.

## start_gof.py

### Input

- paths to datacards with which the Goodness Of Fit (GOF) test are to be performed
- different options (see `--help` option)

### Output

- shell scripts containing `combine`'s GOF syntax
- folders for array job submittion and log files of jobs
- output of Goodness Of Fit test in the directory of the respective input datacards

### Workflow

The script loops over all given datacards.
First, the script changes into the datacard directory.
There, it creates two shell scripts containing the necessary steps for the GOF test -> one fit to data and fits to toys.
Currently, the default command is

```bash
combine -M GoodnessOfFit --algo "saturated" $DATACARD -n $SUFFIX (-t $NTOYS --toysFreq)
```

where `$DATACARD` is the path to the datacard.
The options in brackets are only used in the fit to toys, where `$NTOYS` is the number of toys to be used.
For more information, please see to the [`combine` documentation](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/)

The shell scripts are collected and subsequently submitted as an array job.