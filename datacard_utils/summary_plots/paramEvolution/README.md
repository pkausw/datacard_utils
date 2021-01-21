# Parameter Evolution
These scripts can be used to plot the postfit values of various parameters of different combinations.
# HOWTO
Before creating the plots, one needs to collect some results.
Easiest way to do so is if the impacts have already been run.

The collection can be done via:
    python collect_ParamsForEvolution_fromImpacts.py /path/to/impacts/

The actual plots can then be created via
       python drawParamEvolution.py param.json

where `param.json` is the json created via the first step.

# Careful:
The parameters to draw, as well as the combinations to compare are defined in `drawParamEvolution.py` itself.
Please check there, when using this workflow. 
