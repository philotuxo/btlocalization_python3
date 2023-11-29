import os
import numpy as np
from lib.visualization import *
from lib.colors import *
from lib.histograms import *
from lib.parsers import *
import matplotlib.pyplot as plt

dataDirectory = "../data/fpt/tetam_multi/"
dataFile = "../data/fpt/tetam_multi/sensor12_0.16_2.19_1.85.mbd"
# dataFile = "../data/fpt/tetam_multi/sensor11_12.95_4.38_1.85.mbd"

rssiData = {}
timeData = {}

mnColor = "darkgreen"
mdColor = "darkred"
mxColor = "black"

# rssiData, timeData = parseDataDir_multi(dataDirectory, default_pattern_multi_data)
rssiData, timeData = parseDataFile_multi(dataFile, rssiData, timeData, default_pattern_multi_data)

timeWindowSize = 2.0

pos = (0.16, 2.19, 1.85)
# pos = (12.95, 4.38, 1.85)
sensor = list(rssiData[pos].keys())[0]
beacon = 'e78f135624ce'

mnDataHistWin, bins = meanRssiHistFromData(rssiData[pos][sensor][beacon],
                    timeData[pos][sensor][beacon],
                    timeWindowSize = timeWindowSize,
                    limits=(rssi_start, rssi_end))

mdDataHistWin, bins = medianRssiHistFromData(rssiData[pos][sensor][beacon],
                    timeData[pos][sensor][beacon],
                    timeWindowSize = timeWindowSize,
                    limits=(rssi_start, rssi_end))

mxDataHistWin, bins = maxRssiHistFromData(rssiData[pos][sensor][beacon],
                    timeData[pos][sensor][beacon],
                    timeWindowSize = timeWindowSize,
                    limits=(rssi_start, rssi_end))


mnDataHistWin = hist_normalize(mnDataHistWin)
mdDataHistWin = hist_normalize(mdDataHistWin)
mxDataHistWin = hist_normalize(mxDataHistWin)

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

for index in range(rng[0],rng[1]):
    rssiWindow.append(rssiData[pos][sensor][beacon][index])
    timeWindow.append(timeData[pos][sensor][beacon][index])
    while timeWindow[-1] - timeWindow[0] > timeWindowSize:
        timeWindow.pop(0)
        rssiWindow.pop(0)
    # print(len(timeWindow), end=" ")
    mnRssi.append(np.mean(rssiWindow))
    mdRssi.append(np.median(rssiWindow))
    mxRssi.append(np.max(rssiWindow))

plt.rcParams["mathtext.fontset"] = "stix"

fig = plt.figure(figsize= (10,5))
plt.grid(True)
plt.plot(times, rssiData[pos][sensor][beacon][rng[0]:rng[1]],'k+', markersize = 14, markeredgewidth=3, alpha=.9)
# plt.plot(times, mxRssi,'x', markersize = 12, markeredgewidth = 2, alpha = .75, color = mxColor)
plt.ylabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
plt.xlabel("$\mathrm{Time~(s)}$", fontsize=20)
plt.tick_params(labelsize=14)
# plt.legend(['Original RSSI values', 'Filtered RSSI values'], fontsize=14)
plt.ylim(rssi_range)


fig, splt = plt.subplots(2, 1, figsize=(8,8))

# splt[0,0].set_title("$\mathrm{Mean~Filter~with}~l = "+ str(timeWindowSize) + "$", fontsize = 20)
# splt[0,0].grid(True)
# splt[0,0].plot(times, rssiData[pos][sensor][beacon][rng[0]:rng[1]],'k+', markersize = 12, markeredgewidth=2, alpha=.3)
# splt[0,0].plot(times, mnRssi,'x', color=mnColor, markersize = 12, markeredgewidth = 2, alpha = .75)
# splt[0,0].set_ylabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
# splt[0,0].set_xlabel("$\mathrm{Time~(s)}$", fontsize=20)
# splt[0,0].tick_params(labelsize=14)
# splt[0,0].legend(['Original RSSI values', 'Filtered RSSI values'], fontsize=14)
# splt[0,0].set_ylim(rssi_range)
#
# splt[1,0].grid(True)
# splt[1,0].bar(bins[:-1], rssiHist, color='black', alpha=.2, edgecolor='black')
# splt[1,0].bar(bins[:-1], mnDataHistWin, color=mnColor, alpha=.75, edgecolor='black', width=.5)
# splt[1,0].tick_params(labelsize=14)
# # splt[0,0].set_yticks(labelsize=14)
# splt[1,0].set_xlim([-100, -50])
# splt[1,0].set_xlabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
# splt[1,0].set_ylabel("$\mathrm{Probability}$", fontsize = 20)
# splt[1,0].legend(['Original histogram', 'Mean filter histogram'], fontsize=14)
# splt[1,0].set_ylim(prob_yrange)
#
# splt[0,1].set_title("$\mathrm{Median~Filter~with}~l = "+ str(timeWindowSize) + "$", fontsize = 20)
# splt[0,1].grid(True)
# splt[0,1].plot(times, rssiData[pos][sensor][beacon][rng[0]:rng[1]],'k+', markersize = 12, markeredgewidth=2, alpha=.3)
# splt[0,1].plot(times, mdRssi,'x', markersize = 12, markeredgewidth = 2, alpha = .75, color = mdColor)
# # splt[0,1].set_ylabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
# splt[0,1].set_xlabel("$\mathrm{Time~(s)}$", fontsize=20)
# splt[0,1].tick_params(labelsize=14)
# splt[0,1].legend(['Original RSSI values', 'Filtered RSSI values'], fontsize=14)
# splt[0,1].set_ylim(rssi_range)
#
# splt[1,1].grid(True)
# splt[1,1].bar(bins[:-1], rssiHist, color='black', alpha=.2, edgecolor='black')
# splt[1,1].bar(bins[:-1], mdDataHistWin, color=mdColor, alpha=.75, edgecolor='black', width=.5)
# splt[1,1].tick_params(labelsize=14)
# # splt[0,1].set_yticks(labelsize=14)
# splt[1,1].set_xlim([-100, -50])
# splt[1,1].set_xlabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
# splt[1,1].legend(['Original histogram', 'Median filter histogram'], fontsize=14)
# splt[1,1].set_ylim(prob_yrange)

splt[0].set_title("$\mathrm{Maximal~Filter~with}~l = "+ str(timeWindowSize) + "$", fontsize = 20)
splt[0].grid(True)
splt[0].plot(times, rssiData[pos][sensor][beacon][rng[0]:rng[1]],'k+', markersize = 12, markeredgewidth=2, alpha=.3)
splt[0].plot(times, mxRssi,'x', markersize = 12, markeredgewidth = 2, alpha = .75, color = mxColor)
# splt[0].set_ylabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
splt[0].set_xlabel("$\mathrm{Time~(s)}$", fontsize=20)
splt[0].tick_params(labelsize=14)
splt[0].legend(['Original RSSI values', 'Filtered RSSI values'], fontsize=14)
splt[0].set_ylim(rssi_range)

splt[1].grid(True)
splt[1].bar(bins[:-1], rssiHist, color='black', alpha=.2, edgecolor='black')
splt[1].bar(bins[:-1], mxDataHistWin, color=mxColor, alpha=.75, edgecolor='black', width=.5)
splt[1].tick_params(labelsize=14)
# splt[0].set_yticks(labelsize=14)
splt[1].set_xlim([-100, -50])
splt[1].set_xlabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
splt[1].legend(['Original histogram', 'Maximal filter histogram'], fontsize=14)
splt[1].set_ylim(prob_yrange)
fig.align_ylabels()

plt.tight_layout()
plt.show()
