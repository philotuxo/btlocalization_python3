import os
import numpy as np
from lib.visualization import *
from lib.colors import *
from lib.histograms import *
from lib.parsers import *
import matplotlib.pyplot as plt
from scipy.stats import norm

dataDirectory = "../data/fpt/tetam_multi/"
# dataFile = "../data/fpt/tetam_multi/sensor32_0.16_2.19_1.85.mbd"
dataFile = "../data/fpt/tetam_multi/sensor42_7.77_17.44_1.85.mbd"

rssiData = {}
timeData = {}

mxmnColor = "darkred"
mxColor = "black"

# rssiData, timeData = parseDataDir_multi(dataDirectory, default_pattern_multi_data)
rssiData, timeData = parseDataFile_multi(dataFile, rssiData, timeData, default_pattern_multi_data)

timeWindowSize = 2.0
print(rssiData.keys())

# pos = (0.16, 2.19, 1.85)
# pos = (15.52, 2.19, 1.90)
pos = (7.77, 17.44, 1.85)
sensor = list(rssiData[pos].keys())[0]
beacon = 'e78f135624ce'

mxDataHistWin, bins = maxRssiHistFromData(rssiData[pos][sensor][beacon],
                    timeData[pos][sensor][beacon],
                    timeWindowSize = timeWindowSize,
                    limits=(rssi_start, rssi_end))


mxDataHistWin = hist_normalize(mxDataHistWin)

mxmn = 0
for i in range(mxDataHistWin.shape[0]):
    mxmn += mxDataHistWin[i] * bins[i]

# we use the mean of the maxfilter output

var = 0
for i in range(mxDataHistWin.shape[0]):
    var += (bins[i] - mxmn)**2 * mxDataHistWin[i]
    # print(bins[i], (bins[i] - mxmn)**2 * mxDataHistWin[i])

mxmn_dist = norm(loc=mxmn, scale=np.sqrt(var))
x_bins = np.linspace(-100, -50, 200)
mxmn_pdf = []
for i in range(x_bins.shape[0]):
    mxmn_pdf.append(mxmn_dist.pdf(x_bins[i]))

print(mxmn_pdf)

rssiHist, bins = rssiHistFromData(rssiData[pos][sensor][beacon],
                                  limits=(rssi_start, rssi_end))
rssiHist = hist_normalize(rssiHist)

# plt.bar(bins[:-1], dataHistWin, alpha=.75)
plt.show()

rng = [210,250]
prob_yrange = [0, 1.0]
rssi_range = [-100, -60]

times = []
for i in timeData[pos][sensor][beacon][rng[0]:rng[1]]:
    times.append(i - timeData[pos][sensor][beacon][0])

mxRssi = []
timeWindow = []
rssiWindow = []

for index in range(rng[0],rng[1]):
    rssiWindow.append(rssiData[pos][sensor][beacon][index])
    timeWindow.append(timeData[pos][sensor][beacon][index])
    while timeWindow[-1] - timeWindow[0] > timeWindowSize:
        timeWindow.pop(0)
        rssiWindow.pop(0)
    # print(len(timeWindow), end=" ")
    mxRssi.append(np.max(rssiWindow))

plt.rcParams["mathtext.fontset"] = "stix"


fig, splt = plt.subplots(1, 2, figsize=(15,4))

fig.suptitle("$\mathrm{Maximal~Filter~with}~l = "+ str(timeWindowSize) + "$", fontsize = 20)
splt[0].grid(True)
splt[0].plot(times, rssiData[pos][sensor][beacon][rng[0]:rng[1]],'k+', markersize = 8, markeredgewidth=2, alpha=.3)
splt[0].plot(times, mxRssi,'x', markersize = 8, markeredgewidth = 2, alpha = .75, color = mxColor)
# splt[0,2].set_ylabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
splt[0].set_xlabel("$\mathrm{Time~(s)}$", fontsize=20)
splt[0].tick_params(labelsize=14)
splt[0].legend(['Raw RSSI values', 'Filtered RSSI values'], fontsize=14)
splt[0].set_ylim(rssi_range)

splt[1].grid(True)
splt[1].bar(bins[:-1], rssiHist, color='black', alpha=.1, edgecolor='black', label="Raw Histogram")
splt[1].plot(x_bins, mxmn_pdf, color = mxmnColor, linewidth = 3, alpha=1, label = "Estimated Gaussian Dist.")
splt[1].bar(bins[:-1], mxDataHistWin, color=mxColor, alpha=.5, edgecolor='black', width=.5, label="Maximalized Histogram")
# splt[1].bar(bins, mxmn_pdf, color = mxmnColor, edgecolor='black', width=.2)
splt[1].tick_params(labelsize=14)
# splt[0,2].set_yticks(labelsize=14)
splt[1].set_xlim([-95, -65])
splt[1].set_xlabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
# splt[1].legend(['Raw histogram', 'Maximalized histogram'], fontsize=14)
splt[1].set_ylim(prob_yrange)
splt[1].legend(fontsize=14)
fig.align_ylabels()

plt.tight_layout()
plt.show()
