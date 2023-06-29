resultsdir="$1"

FULLPATH=`realpath $0`
THISDIR=`dirname $FULLPATH`

for y in 2016 2017 2018 all_years; do
    for dec in "DLFHSL" "DLSL"; do 
        python ${THISDIR}/translate_to_result_json.py -o ${dec}_${y}_stxs.json -c ${THISDIR}/naming_config_stxs.py ${resultsdir}/combined_${dec}_${y}__r_ttH_PTH_*.json
    done
    for dec in DL SL FH; do 
        python ${THISDIR}/translate_to_result_json.py -o ${dec}_${y}_stxs.json -c ${THISDIR}/naming_config_stxs.py ${resultsdir}/combined_${dec}_${y}_DNN__r_ttH_PTH_*.json
    done
done
# python ${THISDIR}/translate_to_result_json.py -o all_years_packaged_fits.json -c ${THISDIR}/naming_config_packaged_fit_with_ratio.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus__r_{FH,DL,SL}.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
# python ${THISDIR}/translate_to_result_json.py -o all_years_packaged_fits_per_year.json -c ${THISDIR}/naming_config_packaged_fit_per_year_with_ratio.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus_per_year__r_201?.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
# python ${THISDIR}/translate_to_result_json.py -o all_years_packaged_fits_per_year_per_channel.json -c ${THISDIR}/naming_config_packaged_fit_per_year_per_channel_with_ratio.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus_per_year_per_channel__r_??_201?.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
# python ${THISDIR}/translate_to_result_json.py -o all_years_bgnorms.json -c ${THISDIR}/naming_config_bgnorms.py ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__CMS_ttHbb_bgnorm_tt??.json ${resultsdir}/combined_DLFHSL_20??_separate_DNN_with_ratio__CMS_ttHbb_bgnorm_tt??.json

# python ${THISDIR}/translate_to_result_json.py -o paper_table_ttH.json -c ${THISDIR}/naming_config_paper_table_ttH.py ${resultsdir}/combined_ttRateFactors_FH_all_years_DNN__r.json ${resultsdir}/combined_SL_all_years_separate_DNN_with_ratio__r.json ${resultsdir}/combined_DL_all_years_DNN_with_ratio__r.json ${resultsdir}/combined_DLFHSL_all_years_packaged_mus__r_??.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
# python ${THISDIR}/translate_to_result_json.py -o paper_plot_ttH_uncorrelated.json -c ${THISDIR}/naming_config_paper_plot_ttH_uncorrelated.py ${resultsdir}/combined_ttRateFactors_FH_all_years_DNN__r.json ${resultsdir}/combined_SL_all_years_separate_DNN_with_ratio__r.json ${resultsdir}/combined_DL_all_years_DNN_with_ratio__r.json ${resultsdir}/combined_DLFHSL_20??_separate_DNN_with_ratio__r.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
# python ${THISDIR}/translate_to_result_json.py -o paper_plot_ttH_correlated.json -c ${THISDIR}/naming_config_paper_plot_ttH_correlated.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus__r_??.json ${resultsdir}/combined_DLFHSL_all_years_packaged_mus_per_year__r_20??.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json


for f in md tex paper; do
    for dec in DL FH SL DLSL DLFHSL; do
        python ${THISDIR}/bestFit.py -j ${dec}_2016_stxs.json -o HIG-19-011_${dec}_stxs_2016 -l 36.3 -t $f
        python ${THISDIR}/bestFit.py -j ${dec}_2017_stxs.json -o HIG-19-011_${dec}_stxs_2017 -l 41.5 -t $f
        python ${THISDIR}/bestFit.py -j ${dec}_2018_stxs.json -o HIG-19-011_${dec}_stxs_2018 -l 59.7 -t $f
        python ${THISDIR}/bestFit.py -j ${dec}_all_years_stxs.json -o HIG-19-011_${dec}_stxs_all_years -l 138 -t $f
    done
done

# The FH-only fits are done with 50% prior on ttB/C: mark with dagger in tables
# sed -i 's|FH |FH${}^{\\dagger}$ |g' HIG-19-011_nominal_*.tex

# python ${THISDIR}/bestFit.py -j all_years_bgnorms.json -o HIG-19-011_bgnorms_summary -l `echo $((36+41+59))` -t paper

# # for the paper
# python ${THISDIR}/bestFit.py -j paper_table_ttH.json -o HIG-19-011_results-table_ttH -l 138 -t paper
# python ${THISDIR}/bestFit.py -j paper_plot_ttH_uncorrelated.json -o HIG-19-011_results-plot_ttH-uncorrelated -l 138 -t paper
# python ${THISDIR}/bestFit.py -j paper_plot_ttH_correlated.json -o HIG-19-011_results-plot_ttH-correlated -l 138 -t paper


