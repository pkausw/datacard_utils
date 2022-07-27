FULLPATH=`realpath $0`
THISDIR=`dirname $FULLPATH`

cmd="python $THISDIR/breakdown_uncertainties.py -a \"--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 1e-2 --cminDefaultMinimizerPrecision 1e-12 --X-rtd MINIMIZER_analytic --setParameterRanges 'rgx{r.*}'=-10,10 \" -b all:autoMCStats:jes:btag:thy:exp:bgnorm_ttX=allConstrainedNuisances,'var{.*bgnorm_tt.*}':bgnorm=allConstrainedNuisances,'var{.*bgnorm.*}':bgnorm_ddQCD=allConstrainedNuisances,'var{.*bgnorm_ddQCD.*}':sig_thy='var{.*(pdf|QCDscale|scaleMuR|scaleMuF|ISR|FSR|PDF).*_ttH}':bkg_thy='var{(.*(pdf|QCDscale|ISR|FSR|PDF).*_tt(bar|bb|cc|lf))|(.*(scaleMuR|scaleMuF|UE)}':lumi='var{.*lumi.*}' -f $@" 
#cmd="$cmd -a \"--setParameters r=1\""
cmd="$cmd -a \"--setParameters 'rgx{r.*}'=1 -t -1\""
echo "$cmd"
eval "$cmd"
