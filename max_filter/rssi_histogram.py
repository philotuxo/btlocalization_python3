import os
import numpy as np
from lib.visualization import *
from lib.colors import *
from lib.histograms import *
from lib.parsers import *
import matplotlib.pyplot as plt

dataDirectory = "../data/fpt/tetam_multi/"
# dataFile = "../data/fpt/tetam_multi/sensor32_0.16_2.19_1.85.mbd"
dataFile = "../data/fpt/tetam_multi/sensor11_12.95_4.38_1.85.mbd"

rssiData = {}
timeData = {}

mnColor = "darkgreen"
mdColor = "darkred"
mxColor = "darkblue"

# rssiData, timeData = parseDataDir_multi(dataDirectory, default_pattern_multi_data)
rssiData, timeData = parseDataFile_multi(dataFile, rssiData, timeData, default_pattern_multi_data)


# pos = (0.16, 2.19, 1.85)
pos = (12.95, 4.38, 1.85)
sensor = list(rssiData[pos].keys())[0]
beacon = 'e78f135624ce'

rssiHist, bins = rssiHistFromData(rssiData[pos][sensor][beacon],
                                  limits=(rssi_start, rssi_end))

rssiHist = hist_normalize(rssiHist)

# plt.bar(bins[:-1], dataHistWin, alpha=.75)
plt.show()

rng = [290,310]
prob_yrange = [0, 1.0]
rssi_range = [-100, -60]

times = []
for i in timeData[pos][sensor][beacon][rng[0]:rng[1]]:
    times.append(i - timeData[pos][sensor][beacon][0])

mnRssi = []
mxRssi = []
mdRssi = []
timeWindow = []
rssiWindow = []

plt.rcParams["mathtext.fontset"] = "stix"

fig = plt.figure(figsize= (10,4))

plt.grid(True)
plt.bar(bins[:-1], rssiHist, color='blue', alpha=1, edgecolor='blue')
plt.tick_params(labelsize=14)
plt.xlim([-100, -50])
plt.xlabel("$\mathrm{RSSI~(dB)}$", fontsize = 24)
plt.ylabel("$\mathrm{Probability}$", fontsize = 24)
# plt.legend(['Original histogram', 'Mean filter histogram'], fontsize=14)
plt.ylim([0,.5])
plt.text(-68, 0.2, "   Possible\nLine of Sight", fontsize=24)
plt.text(-80, 0.35, "   Close\nReflection", fontsize=24)
plt.text(-91, 0.2, "     Far\nReflection", fontsize=24)

fig.align_ylabels()

plt.tight_layout()
plt.show()
