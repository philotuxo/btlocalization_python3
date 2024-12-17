#!/bin/bash

ROOT_DIR="/home/serhan/workspace/btlocalization"
#EXP_NAMES="zigzag_rotsuz_combined kare_rotsuz_combined duz_01_combined"
EXP_NAMES="duz_01_combined"
GRIDS="0.1 0.2 0.5 1.0"
MASKS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25"
#WINDOWS="0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0"
WINDOWS="2.0"
#DIFFS="0.01 0.02 0.05 0.1 0.2 0.5 1.0 2.0 5.0"
DIFFS="1.0"
# EXP_NAMES=" zigzag_rotsuz_combined kare_rotsuz_combined"
ERR_DIR="errors/"
CONF_DIR="conf/"
SCREEN_NAME="btExact"

# if the configuration directory is empty fill it with files

echo "Configuration directory \"${CONF_DIR}\" is empty, populating with new experiments."
# queue the experiments and generate conf files
for EXP_NAME in ${EXP_NAMES}
do
    for GRID in ${GRIDS}
    do
        for MASK in ${MASKS}
        do
            for DIFF in ${DIFFS}
            do
                for WINDOW in ${WINDOWS}
                do
                    for NUMBER in $(seq -f "%03g" 1 $SIZE)
                    do
                        echo "{
 \"limits\": [[0.0, 0.0], [20.660138018121128, 17.64103475472807]],
 \"gui\": 0,
 \"diffusion\": ${DIFF},
 \"mask_size\": ${MASK},
 \"sec_window\": ${WINDOW},
 \"size_visuals\": 0,
 \"error_output_file\": \"${ERR_DIR}/errors_${EXP_NAME}_${GRID}_${MASK}_${DIFF}_${WINDOW}_${NUMBER}.txt\",
 \"grddir\": \"${ROOT_DIR}/data/grd/tetam_multi/wassBest_mxrssi_${WINDOW}_${GRID}/\",
 \"track_file\": \"${ROOT_DIR}/data/trk/tetam_multi_with_ground_truth/${EXP_NAME}.mbd\",
 \"occ\": \"${ROOT_DIR}/data/occ/tetam_${GRID}.occ\"
}" > ${CONF_DIR}${EXP_NAME}_${GRID}_${MASK}_${DIFF}_${WINDOW}_${NUMBER}.conf
                    done
                done
            done
        done
    done
done
