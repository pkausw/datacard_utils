FULLPATH=`realpath $0`
THISDIR=`dirname $FULLPATH`

cmd="python $THISDIR/breakdown_uncertainties.py -a \"--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 1e-2 --cminDefaultMinimizerPrecision 1e-12 --X-rtd MINIMIZER_analytic --rMin -10 --rMax 10 --setParameters r=1\" -b all:autoMCStats:jes:btag:thy:exp:bgnorm_ttX=allConstrainedNuisances,'var{.*bgnorm_tt.*}':bgnorm=allConstrainedNuisances,'var{.*bgnorm.*}':bgnorm_ddQCD=allConstrainedNuisances,'var{.*bgnorm_ddQCD.*}' -f $@" 
echo "$cmd"
#eval "$cmd"
