#!/bin/bash

ROOT_DIR="/home/serhan/workspace/btlocalization"
SIZE=4
RUNSIZE=4
D_POP_SIZES="500"
P_POP_SIZES="1"
EXP_NAMES="duz_01_combined"
DIFF_LIMIT="0.0001"
SENSES="0.00000001 0.00000002 0.00000005 0.0000001 0.0000002 0.0000005 0.000001 0.000002 0.000005 0.00001 0.00002 0.00005 0.0001 0.0002 0.0005 0.001 0.002 0.005 0.01 0.02 0.05 0.1 0.2 0.5"
ERR_DIR="errors/"
CONF_DIR="conf/"
SCREEN_NAME="btParticle"

# if the configuration directory is empty fill it with files

if [ -z "$(ls -A ${CONF_DIR})" ]
then
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
                    for NUMBER in $(seq -f "%03g" 1 $SIZE)
                    do
                        echo "{
 \"limits\": [[0.0, 0.0], [20.660138018121128, 17.64103475472807]],
 \"nthr\": 1.0,
 \"size_burnin\": 50,
 \"size_d\": ${D_POP_SIZE},
 \"size_p\": ${P_POP_SIZE},
 \"diffusion_limit\": ${DIFF_LIMIT},
 \"sensitivity\" : ${SENSE},
 \"size_visuals\": 0,
 \"error_output_file\": \"${ERR_DIR}/errors_${EXP_NAME}_${D_POP_SIZE}_${P_POP_SIZE}_${SENSE}_${NUMBER}.txt\",
 \"grddir\": \"${ROOT_DIR}/data/grd/tetam_multi/wassBest_0.2/\",
 \"track_file\": \"${ROOT_DIR}//data/trk/tetam_multi_with_ground_truth/${EXP_NAME}.mbd\",
 \"occ\": \"${ROOT_DIR}/data/occ/tetam_0.2.occ\"
}" > ${CONF_DIR}${EXP_NAME}_${D_POP_SIZE}_${P_POP_SIZE}_${SENSE}_${NUMBER}.conf
                    done
                done
            done
        done
    done
else
    echo "Configuration files found in the directory \"${CONF_DIR}\"."
fi

while [ -n "`ls -1 ${CONF_DIR}`" ]
do 
    CONF_TEMP=""
    for conf_file in `ls -1 ${CONF_DIR} | sort -V | head -n $RUNSIZE`
    do
        echo "Current running configuration:" $conf_file
        screen -S ${SCREEN_NAME} -d -m python3 btParticle_multi_main_adaptive.py ${CONF_DIR}${conf_file}
        CONF_TEMP="$CONF_TEMP ${CONF_DIR}${conf_file}"
    done
    # wait if there are running screens
    echo "Waiting for the screens to finish"
    while [ `screen -ls | grep --color=None ${SCREEN_NAME} | wc -l` -gt 0 ]
    do
        sleep 1
    done
    rm $CONF_TEMP
done


BALL_NAME="errors_`date +%Y%m%d%H%M`.7z"
7z a $BALL_NAME $ERR_DIR
