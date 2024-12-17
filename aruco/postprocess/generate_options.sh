#!/bin/bash

VIDEODIR="data/test02/video/"
TIMESTARTDIR="data/test02/mbd/timeStart/"
TRJDIR="data/test02/trajectory/"
K=$2
S=$3
O=$4

if [ $# -eq 0 ]
then
    exit
fi

OPTIONS=${VIDEODIR}$1"_f.mp4 "${VIDEODIR}$1"_b.mp4 "${TIMESTARTDIR}$1".txt "

if [ $# -eq 4 ]
then
    OPTIONS+=$TRJDIR$1"_k"$2"_s"$3"_o"$4".csv"
fi

echo $OPTIONS $2
