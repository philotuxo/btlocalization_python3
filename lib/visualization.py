from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def hist_plot(hist, bins, color=None, outputFile=None, yRange=None,
              xRange=None):

    if not color:
        color = [0, 0, 1]

    if xRange:
        xRange = [xRange[0] - bins[0], xRange[1] - bins[0]]
        plt.bar(bins[xRange[0]:xRange[1]],
                      hist[xRange[0]:xRange[1]], color=color)
    else:
        plt.bar(bins[:-1], hist, color= color, width=(bins[1]-bins[0]))
    a = plt.gca()
    # a.axes.get_xaxis().set_ticklabels(bins)
    a.axes.get_xaxis().grid()
    # a.axes.set_xlim(bins[0], bins[-1])

    if yRange:
        plt.ylim(yRange)
    if outputFile:
        pp = PdfPages(outputFile)
        plt.savefig(pp, format='pdf')
        pp.close()
        print("Current figure saved to: " + outputFile)
