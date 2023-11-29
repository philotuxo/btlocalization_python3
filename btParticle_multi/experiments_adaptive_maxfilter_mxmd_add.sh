#!/bin/bash

ROOT_DIR="/home/serhan/workspace/btlocalization"
SIZE=4
RUNSIZE=4
D_POP_SIZES="50"
P_POP_SIZES="19"
EXP_NAMES="zigzag_rotsuz_combined kare_rotsuz_combined duz_03_combined duz_01_combined"
#EXP_NAMES="duz_03_combined duz_01_combined"
DIFF_LIMIT="0.0001"
SENSES="0.000001 0.000002 0.000005 0.00001 0.00002 0.00005 0.0001 0.0002 0.0005 0.001 0.002 0.005 0.01 0.02 0.05"
#SIGMAS="3.5 4.0 4.5 5.0"
SIGMAS="0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0"
MUS="3"
ERR_DIR="errors/"
CONF_DIR="conf/"
SCREEN_NAME="btParticle"
#WINDOWS="1.0 1.5 2.0 2.5 3.0"
WINDOWS="1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0"
#WINDOWS="3.5 4.0 4.5 5.0"


# if the configuration directory is empty fill it with files

echo "Configuration directory \"${CONF_DIR}\" is empty, populating with new experiments."
# queue the experiments and generate conf files
for EXP_NAME in ${EXP_NAMES}
do
    for D_POP_SIZE in ${D_POP_SIZES}
    do
        for P_POP_SIZE in ${P_POP_SIZES}
        do
            for SENSE in ${SENSES}
            do
                for WINDOW in ${WINDOWS}
                do
                    for MU in ${MUS}
                    do
                        for SIGMA in ${SIGMAS}
                        do
                           for NUMBER in $(seq -f "%03g" 1 $SIZE)
                           do
                               echo "{
 \"limits\": [[0.0, 0.0], [20.660138018121128, 17.64103475472807]],
 \"nthr\": 1.0,
 \"size_burnin\": 25,
 \"size_d\": ${D_POP_SIZE},
 \"size_p\": ${P_POP_SIZE},
 \"diffusion_limit\": ${DIFF_LIMIT},
 \"sec_window\": ${WINDOW},
 \"fp_sigma\": ${SIGMA},
 \"fp_mu\": ${MU},
 \"sensitivity\" : ${SENSE},
 \"size_visuals\": 0,
 \"error_output_file\": \"${ERR_DIR}/errors_${EXP_NAME}_${D_POP_SIZE}_${P_POP_SIZE}_${SENSE}_${WINDOW}_${MU}_${SIGMA}_${NUMBER}.txt\",
 \"grddir\": \"${ROOT_DIR}/data/grd/tetam_multi/avc_20_mxmdrssi_${WINDOW}_0.2/\",
 \"track_file\": \"${ROOT_DIR}/data/trk/tetam_multi_with_ground_truth/${EXP_NAME}.mbd\",
 \"occ\": \"${ROOT_DIR}/data/occ/tetam_0.2.occ\"
}" > ${CONF_DIR}${EXP_NAME}_${D_POP_SIZE}_${P_POP_SIZE}_${SENSE}_${WINDOW}_${MU}_${SIGMA}_${NUMBER}.conf
                            done
                        done
                    done
                done
            done
        done
    done
done
