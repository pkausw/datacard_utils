#!/bin/bash

set -e

if [ "$#" -ne 1 ]; then

  printf "\n%s\n" " >>> ERROR -- invalid command-line arguments: ./combinecards.sh [1]"
  printf "%s\n\n" "           [1] path to input directory containing sub-folders for impacts of each channel (fails if dir does not exist)"
  exit
fi

INPUT_DIR=$1

if [ ! -d ${INPUT_DIR} ]; then

  printf "%s\n" "target input directory ${INPUT_DIR}/ does not exist, will not proceed"
  exit
fi

SUB_DIRS=(

 2016_fh
 2016_sl
 2016_dl

 2016

 2017_fh
 2017_fh_3b
 2017_fh_4b

 2017_sl
 2017_sl_4j
 2017_sl_5j
 2017_sl_6j

 2017_dl
 2017_dl_3j
 2017_dl_4j

 2017

 2016p2017
)

for i_subdir in ${SUB_DIRS[@]}; do

  if [ -d ${INPUT_DIR}/${i_subdir} ]; then

    cd    ${INPUT_DIR}/${i_subdir}

    if [ -f higgsCombine_${i_subdir}.Impacts.mH125.sh ]; then
          ./higgsCombine_${i_subdir}.Impacts.mH125.sh
    fi

    rm robustHesse*.root

    cd ${OLDPWD}
  fi

done
unset -v i_subdir

unset -v INPUT_DIR SUB_DIRS
