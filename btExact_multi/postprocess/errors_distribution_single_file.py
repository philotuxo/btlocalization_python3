import json
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import ticklabel_format
import sys

TICK_FONTSIZE = 16
LABEL_FONTSIZE = 14
TITLE_FONTSIZE = 24

ticklabel_format(style="sci")


def main():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "/home/serhan/btlocalization_data/errors/errors_static/synthetic_from_hst/errors_duz_04_synthetic_from_hst_1000_1.5_042.txt"


    errors = []
    means_d = []
    print(file_name)
    with open(file_name) as f:
        for line_str in f:
            line_lst = json.loads(line_str)
            errors.append(line_lst[2])
            if len(line_lst) > 3:
                means_d.append(line_lst[3])
    stepsize = 0.1
    d_stepsize = 0.01

    MN = np.mean(errors)
    MD = np.median(errors)
    VR = np.var(errors)
    MX = np.max(errors)
    MXERR = max(errors)
    print("Error mean:", MN)
    print("Error median:", MD)
    print("Error var:", VR)
    print("Error max:", MX)
    fig, axes = plt.subplots(1,3, figsize=(12,3.2))
    plt.rcParams["mathtext.fontset"] = "stix"

    ## flat plot
    axes[0].plot(errors, color = '#000000')
    if len(means_d) > 0:
        axes[0].plot(means_d)
    axes[0].set_title("Trajectory errors", fontsize=LABEL_FONTSIZE)
    axes[0].plot([-15, len(errors) - 1 + 14], [MN, MN], 'r', alpha=.8)
    axes[0].plot([-15, len(errors) - 1 + 14], [MD, MD], 'g', alpha=.8)
    axes[0].set_xlim([-15, len(errors) - 1 + 14])
    axes[0].set_ylim([0, MXERR+0.5])
    axes[0].set_xlabel('$\mathrm{Time~(s)}$', fontsize=TICK_FONTSIZE)
    axes[0].set_ylabel('$\mathrm{Error~(m)}$', fontsize=TICK_FONTSIZE)

    ## histogram
    hst, bins = np.histogram(errors, bins = np.arange(0,10,stepsize))
    hst = hst/hst.sum()
    MX = hst.max()
    axes[1].bar(x=bins[:-1], height=hst, width=stepsize, alpha = 1,
                    color = '#000000')
    axes[1].set_title("Error histogram", fontsize=LABEL_FONTSIZE)
    axes[1].plot([MD,MD], [0,MX+.05], 'g', alpha=.8)
    axes[1].plot([MN,MN], [0,MX+.05], 'r', alpha=.8)
    axes[1].set_ylim([0,MX+.05])
    axes[1].set_xlabel('$\mathrm{Error~(m)}$', fontsize=TICK_FONTSIZE)
    axes[1].set_ylabel('$\mathrm{Probability}$', fontsize=TICK_FONTSIZE)

    ## cumulative
    cum = np.cumsum(hst)
    axes[2].plot(bins[:-1], cum, linewidth=4, color = '#000000', alpha = 1)
    axes[2].set_title("Cumulative Error Distribution",
                      fontsize=LABEL_FONTSIZE)
    axes[2].plot([MD,MD], [0,1.05], 'g', alpha=.8)
    axes[2].plot([MN,MN], [0,1.05], 'r', alpha=.8)
    axes[2].set_ylim([0,1.05])
    axes[2].set_xlabel('$\mathrm{Error~(m)}$', fontsize=TICK_FONTSIZE)
    axes[2].set_ylabel('$\mathrm{Cum.~Probability}$', fontsize=TICK_FONTSIZE)
    fig.tight_layout()

    if len(means_d) > 0:
        MN = np.mean(means_d)
        MD = np.median(means_d)
        MXERR = max(means_d)

        print("Diffusion mean:", MN)
        print("Diffusion median:", MD)

    ## histogram
    if len(means_d) > 0:
        hst, bins = np.histogram(means_d, bins=np.arange(0, 0.5 , d_stepsize))
        hst = hst / hst.sum()
        MX = hst.max()
        axes[3].bar(x=bins[:-1], height=hst, width=d_stepsize, alpha=.8,
                    color = '#000000')
        axes[3].set_title("Sample error histogram")
        axes[3].plot([MD, MD], [0, MX + .05], 'g', alpha=.8)
        axes[3].plot([MN, MN], [0, MX + .05], 'r', alpha=.8)
        axes[3].set_ylim([0, MX + .05])
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
