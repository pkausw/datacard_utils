FULLPATH=`realpath $0`
THISDIR=`dirname $FULLPATH`

groups="all:autoMCStats:jes:btag:exp"
groups="${groups}:bgnorm_ttX=allConstrainedNuisances,\\\"var{.*bgnorm_tt.*}\\\""
groups="${groups}:bgnorm=allConstrainedNuisances,\\\"var{.*bgnorm.*}\\\""
groups="${groups}:bgnorm_ddQCD=allConstrainedNuisances,\\\"var{.*bgnorm_ddQCD.*}\\\""
groups="${groups}:sig_thy=\\\"var{.*(pdf|QCDscale|scaleMuR|scaleMuF|ISR|FSR|PDF).*_ttH}\\\""
groups="${groups}:bkg_thy=\\\"var{(.*(pdf|QCDscale|ISR|FSR|PDF).*_tt(bar|bb|cc|lf))|(.*(scaleMuR|scaleMuF|scaleMuR_ttbbNLO|scaleMuF_ttbbNLO|glusplit.*))}\\\""
groups="${groups}:lumi=\\\"var{.*lumi.*}\\\""
groups="${groups}:thy=\\\"var{.*(pdf|QCDscale|scaleMuR|scaleMuF|ISR|FSR|PDF|HDAMP|UE|glusplit).*}\\\""


cmd="python $THISDIR/breakdown_uncertainties.py -a \"--cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 1e-2 --X-rtd MINIMIZER_analytic\" -b \"${groups}\" -f $@" 
cmd="$cmd -a \"--setParameters r=1 --setParameterRanges r=-10,10\""
#cmd="$cmd -a \"--setParameters r=1 --setParameterRanges r=-10,10 -t -1\""
#cmd="$cmd -a \"--setParameters \\\"rgx{r.*}\\\"=1 --setParameterRanges \\\"rgx{r.*}\\\"=-10,10 -t -1\""
#cmd="$cmd --stxs -a \"--setParameters \\\"rgx{r.*}\\\"=1 --setParameterRanges \\\"rgx{r.*}\\\"=-10,10\""
echo "$cmd"
eval "$cmd"
