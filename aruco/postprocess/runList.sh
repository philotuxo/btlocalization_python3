#!/bin/bash
SAVEPWD=$PWD

for kalman in 0.01 0.05 0.1 0.2 0.5 1.0 2.0 5.0
do
    for name in "duz_01" "duz_02" "duz_03" "duz_04" "duz_05" "kare_rotsuz" "kare_rotlu" "zigzag_rotsuz" "zigzag_rotlu"
    do
	echo
        echo $name
        cd ../
	python3 arLocalization.py ../../conf/tetam.par ../../maps/tetam.png data/markers/tetam_markers.dat `sh $SAVEPWD/generate_options.sh $name $kalman 20 10`
        cd $SAVEPWD
    done
done
