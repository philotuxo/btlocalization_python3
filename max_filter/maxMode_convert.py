import os
import numpy as np
from lib.visualization import *
from lib.colors import *
from lib.histograms import *
from lib.parsers import *
import matplotlib.pyplot as plt
from scipy.stats import norm

dataDirectory = "../data/fpt/tetam_multi/"

rssiData, timeData = parseDataDir_multi(dataDirectory, default_pattern_multi_data)

timeWindowSize = 1.5

mxMdDataHist = {}

beacons = []
sensors = []
bins = []

for pos in rssiData.keys():
    print(pos)
    if pos not in mxMdDataHist.keys():
        mxMdDataHist[pos] = {}
    for sensor in rssiData[pos].keys():
        if sensor not in mxMdDataHist[pos].keys():
            mxMdDataHist[pos][sensor] = {}
            if sensor not in sensors:
                sensors.append(sensor)
        for beacon in rssiData[pos][sensor].keys():
            if beacon not in beacons:
                beacons.append(beacon)

            mxMdData, bins = maxModeRssiHistFromData(rssiData[pos][sensor][beacon],
                    timeData[pos][sensor][beacon],
                    timeWindowSize = timeWindowSize,
                    limits=(rssi_start, rssi_end))

            mxMdDataHist[pos][sensor][beacon] = mxMdData

write_hist_file('/home/serhan/deneme.txt', mxMdDataHist, bins, beacons, sensors)
