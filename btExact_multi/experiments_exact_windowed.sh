#!/bin/bash

ROOT_DIR="/home/serhan/workspace/btlocalization"
RUNSIZE=50
ERR_DIR="errors/"
CONF_DIR="conf/"
SCREEN_NAME="btExact"

while [ -n "`ls -1 ${CONF_DIR}`" ]
do 
    CONF_TEMP=""
    for conf_file in `ls -1 ${CONF_DIR} | sort -V | head -n $RUNSIZE`
    do
        echo "Current running configuration:" $conf_file
        screen -S ${SCREEN_NAME} -d -m python3 btExact_multi_main_windowed.py ${CONF_DIR}${conf_file}
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
#7z a $BALL_NAME $ERR_DIR
