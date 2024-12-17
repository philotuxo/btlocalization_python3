from matplotlib import pyplot as plt
import os
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches

pd.set_option('precision',3)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
dir = "/home/serhan/btlocalization_data/test02/originals/mbd/zigzag_rotsuz/"

FONTSIZE_TICKS = 14
FONTSIZE_LABEL = 20

def onclick(event):
    print('%f' % (event.xdata))
    plt.show()

files = [ "sensor10_0.00_0.00_0.00.mbd", "sensor20_0.00_0.00_0.00.mbd"]
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["mathtext.bf"] = "stix bold"

N = 40
fig, ax = plt.subplots(figsize = (6,8))
counter = 0
df = None
for file in os.listdir(dir):
    if file in files:
        df = pd.read_csv(dir + file, usecols=[0,3], header=None)
        if counter == 0:
            ax.plot(df.iloc[:N,1], df.iloc[:N,0]-df.iloc[0,0], 'k+', markersize = 8, markerfacecolor=(0, 0, 0, 1), label = "Sensor-1a")
            ax.plot(df.iloc[:N, 1], df.iloc[:N, 0] - df.iloc[0, 0], 'k-', alpha=.2)
        if counter == 1:
            ax.plot(df.iloc[:N,1], df.iloc[:N, 0] - df.iloc[0, 0], 'k.', markersize = 8, markerfacecolor=(0, 0, 0, 1), label = "Sensor-2a")
            ax.plot(df.iloc[:N, 1], df.iloc[:N, 0] - df.iloc[0, 0], 'k-', alpha = .2)
        ax.fmt_ydata = lambda x: "{0:f}".format(x)
        ax.fmt_xdata = lambda x: "{0:f}".format(x)
        counter += 1

plt.text(-71, 2, '$\mathbf{Uncovered}$', fontsize=FONTSIZE_LABEL)
plt.text(-69.5, 3.4, '$\mathbf{Covering}$', fontsize=FONTSIZE_LABEL)
plt.text(-68.8, 8.5, '$\mathbf{Covered}$', fontsize=FONTSIZE_LABEL)
plt.text(-70, 14.4, '$\mathbf{Releasing}$', fontsize=FONTSIZE_LABEL)
plt.text(-71, 16, '$\mathbf{Uncovered}$', fontsize=FONTSIZE_LABEL)
rectcovering = mpatches.Rectangle((-100, 2.5), 40, 1, fill=True, color = '#b9b9b9')
rectcovered = mpatches.Rectangle((-100, 3.5), 40, 10, fill=True, color = '#777777')
rectreleasing = mpatches.Rectangle((-100, 13.5), 40, 1, fill=True, color = '#b9b9b9')
plt.gca().add_patch(rectcovered)
plt.gca().add_patch(rectcovering)
plt.gca().add_patch(rectreleasing)

plt.xlim([-100, -60])
plt.ylim([-5, df.iloc[N, 0]- df.iloc[0, 0]])
plt.gca().yaxis.tick_right()
plt.gca().yaxis.set_label_position("right")
plt.ylabel('$\mathrm{Time~(sec)}$', fontsize = FONTSIZE_LABEL)
plt.yticks([-5,0,5,10,15,20], fontsize = FONTSIZE_TICKS)
plt.xticks([-100, -90, -80, -70, -60], fontsize = FONTSIZE_TICKS)
plt.xlabel('$\mathrm{RSSI~(dB)}$', fontsize = FONTSIZE_LABEL)
plt.title('$\mathrm{Live~RSSI~data}$', fontsize = FONTSIZE_LABEL)
plt.gca().invert_yaxis()
plt.legend(fontsize = FONTSIZE_TICKS)
plt.show()

