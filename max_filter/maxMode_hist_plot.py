import sys, os, time, re
sys.path.append("..")
from lib.histograms import *
from lib.parsers import *
import matplotlib.pyplot as plt
from scipy.stats import norm

dataDirectory = "../data/fpt/tetam_multi/"
# dataFile = "../data/fpt/tetam_multi/sensor32_0.16_2.19_1.85.mbd"
dataFile = "../../data/fpt/tetam_multi/sensor30_12.95_4.38_1.85.mbd"

rssiData = {}
timeData = {}

mxmnColor = "darkgreen"
mxColor = "black"

# rssiData, timeData = parseDataDir_multi(dataDirectory, default_pattern_multi_data)
rssiData, timeData = parseDataFile_multi(dataFile, rssiData, timeData, default_pattern_multi_data)

timeWindowSize = 2.0
print(rssiData.keys())

# pos = (0.16, 2.19, 1.85)
pos = (12.95, 4.38, 1.85)
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

rng = [290,310]
prob_yrange = [0, 1.0]
rssi_range = [-100, -40]

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
    mxRssi.append(np.max(rssiWindow))

plt.rcParams["mathtext.fontset"] = "stix"
fig, splt = plt.subplots(1, 1, figsize=(10,4))
splt.set_title("$\mathrm{Maximal~Filter~with}~l = "+ str(timeWindowSize) + "$", fontsize = 20)
splt.grid(True)
splt.bar(bins[:-1], rssiHist, color='black', alpha=.1, edgecolor='black', label="Original RSSI Histogram")
splt.bar(bins[:-1], mxDataHistWin, color=mxColor, alpha=.3, edgecolor=mxColor, width=.4, label="Processed RSSI Histogram")
splt.plot(x_bins, mxmn_pdf, color = mxmnColor, linewidth = 5, label = "Gaussian Distribution")
splt.tick_params(labelsize=14)
splt.set_xlim([-90, -65])
splt.set_xlabel("$\mathrm{RSSI~(dB)}$", fontsize = 20)
splt.plot([mxmn, mxmn],[0, 1.0], '--', color = mxmnColor, linewidth = 2)
splt.text(mxmn-1.1, 0.75, '$\mu = $' + str(round(mxmn,2)), fontsize=20, color=mxmnColor)
# splt.legend()
splt.set_ylim(prob_yrange)
order = [1,2,0]
handles, labels = plt.gca().get_legend_handles_labels()
splt.legend([handles[idx] for idx in order],[labels[idx] for idx in order], fontsize=14)
fig.align_ylabels()

plt.tight_layout()
plt.show()
