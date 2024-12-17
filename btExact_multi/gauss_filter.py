
import sys, os, time, re
sys.path.append("..")

from scipy.stats import multivariate_normal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def gauss_filter(size, cov=2.0):
    filter_size = size * 2 + 1
    x = np.linspace(0, filter_size, filter_size, endpoint=False)
    y = multivariate_normal.pdf(x, size, cov)

    y = y.reshape(1, filter_size)
    # normalize
    y = y / y.sum()

    GF = y.T @ y
    return GF

FONTSIZE_TICKS = 16
FONTSIZE_LABELS = 20

plt.rcParams["mathtext.fontset"] = "stix"

sizes = [3,5,7]
diffs = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
im = None

fig3 = plt.figure(constrained_layout=True, figsize=(len(diffs)*2,len(sizes)*2))
gs = fig3.add_gridspec(len(sizes), len(diffs))

for i in range(len(sizes)):
    for j in range(len(diffs)):
        print(i,j)
        gauss_mask = gauss_filter(sizes[i], diffs[j])
        axl = fig3.add_subplot(gs[i, j])
        axl.imshow(gauss_mask,cmap="gray_r",vmin=0, vmax=0.18)
        if i == 0:
            axl.set_title("$k =" + str(diffs[j]) + "$", fontsize=FONTSIZE_LABELS)
        if j == 0:
            axl.set_ylabel("$m =" + str(sizes[i]) + "$", fontsize=FONTSIZE_LABELS)
        axl.set_xticks([])
        axl.set_yticks([])

# plt.tight_layout()

fig, ax = plt.subplots()
im = ax.imshow(gauss_filter(5,0.0000000001), cmap='gray_r')
cbar = fig.colorbar(im, orientation='vertical')
cbar.set_ticks([0, 1.0])
cbar.ax.tick_params(labelsize=FONTSIZE_TICKS)


# fig = plt.figure()
# cbar = fig.colorbar()
# cbar.set_ticks([0, 0.18])
# cbar.ax.tick_params(labelsize=FONTSIZE_TICKS)


# cbar.set_ticklabels(['low', 'medium', 'high'])

# plt.colorbar()
plt.show()
