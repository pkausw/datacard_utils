resultsdir="$1"

FULLPATH=`realpath $0`
THISDIR=`dirname $FULLPATH`

for y in 2016 2017 2018 1617 1718 all_years; do
  python ${THISDIR}/translate_to_result_json.py -o ${y}_nominal_fits.json -c ${THISDIR}/naming_config_nominal_fit_with_ratio.py ${resultsdir}/combined_DLFHSL_${y}_separate_DNN_with_ratio__r.json ${resultsdir}/combined_DL_${y}_DNN_with_ratio__r.json ${resultsdir}/combined_SL_${y}_separate_DNN_with_ratio__r.json ${resultsdir}/combined_ttRateFactors_FH_${y}_DNN__r.json
done
python ${THISDIR}/translate_to_result_json.py -o all_years_packaged_fits.json -c ${THISDIR}/naming_config_packaged_fit_with_ratio.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus__r_{FH,DL,SL}.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
python ${THISDIR}/translate_to_result_json.py -o all_years_packaged_fits_per_year.json -c ${THISDIR}/naming_config_packaged_fit_per_year_with_ratio.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus_per_year__r_201?.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json
python ${THISDIR}/translate_to_result_json.py -o all_years_packaged_fits_per_year_per_channel.json -c ${THISDIR}/naming_config_packaged_fit_per_year_per_channel_with_ratio.py ${resultsdir}/combined_DLFHSL_all_years_packaged_mus_per_year_per_channel__r_??_201?.json ${resultsdir}/combined_DLFHSL_all_years_separate_DNN_with_ratio__r.json




for f in md tex; do
    python ${THISDIR}/bestFit.py -j 2016_nominal_fits.json -o HIG-19-011_nominial_2016 -l 36 -t $f
    python ${THISDIR}/bestFit.py -j 2017_nominal_fits.json -o HIG-19-011_nominial_2017 -l 41 -t $f
    python ${THISDIR}/bestFit.py -j 2018_nominal_fits.json -o HIG-19-011_nominial_2018 -l 59 -t $f
    python ${THISDIR}/bestFit.py -j 1617_nominal_fits.json -o HIG-19-011_nominial_1617 -l `echo $((36+41))` -t $f
    python ${THISDIR}/bestFit.py -j 1718_nominal_fits.json -o HIG-19-011_nominial_1718 -l `echo $((41+59))` -t $f
    python ${THISDIR}/bestFit.py -j all_years_nominal_fits.json -o HIG-19-011_nominial_all_years -l `echo $((36+41+59))` -t $f

    python ${THISDIR}/bestFit.py -j all_years_packaged_fits.json -o HIG-19-011_packaged_all_years -l `echo $((36+41+59))` -t $f
    python ${THISDIR}/bestFit.py -j all_years_packaged_fits_per_year.json -o HIG-19-011_packaged_all_years_per_year -l `echo $((36+41+59))` -t $f
    python ${THISDIR}/bestFit.py -j all_years_packaged_fits_per_year_per_channel.json -o HIG-19-011_packaged_all_years_per_year_per_channel -l `echo $((36+41+59))` -t $f

done
