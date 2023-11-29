import numpy as np
from lib.colors import *
from random import random, uniform, normalvariate
from decimal import *
from lib.processing import *


def data_generate_rssi(N,params = None):
    if not params:
        params = (np.random.poisson(30)-120,np.random.uniform(.5, 4))
    data = np.random.normal(params[0],params[1],N)
    b = np.empty((len(data),),dtype='int')
    data_int = np.round(data)
    return data_int

def data_generate_rssi_two_peaks(N):
    params = (np.random.poisson(30)-120,np.random.uniform(.5,4),
                np.random.poisson(30)-120,np.random.uniform(.5,4))

    data0 = np.random.normal(params[0],params[1],int(N/2))
    data1 = np.random.normal(params[2],params[3],N-int(N/2))

    return np.append(data0, data1)

def hist_normalize(hist):
    data = np.array(hist,np.dtype(Decimal))
    return data/float(np.sum(data))

def rssiHistFromData(data, limits=(rssi_start, rssi_end)):
    # generate histogram from the given data (list)
    hist, bins = np.histogram(
        data, limits[1] - limits[0], range=(limits[0], limits[1]),
    )
    return hist, bins

def timeHistFromData(timeData, limits = (0., 10.), resol = .5):
    timeDiff = []
    for index in range(1, len(timeData)):
        timeDiff.append(timeData[index] - timeData[index - 1])

    binSize = int((limits[1] - limits[0])/resol)
    timeHist, bins = np.histogram(timeDiff,binSize,range=limits)
    return timeHist, bins

def freqHistFromData(dataTime,
                     limits= (0,5),
                     stepSize= .2,
                     timeWindowSize = 10):

    bins = np.arange(limits[0],limits[1],stepSize).round(2)

    # length of the data
    N = len(dataTime)
    # get indices of sorted timestamps
    indices = sorted(range(N), key=lambda k: dataTime[k])

    freqHist = np.zeros(int(bins.shape[0]), dtype=int)

    # don't need two passes, we write the histogram function here instead of
    # calling it from numpy
    for ind in range(timeWindowSize,N):
        k = indices[ind]
        k_first = indices[ind-timeWindowSize]
        diff = dataTime[k] - dataTime[k_first]
        try:
            freq = timeWindowSize/diff
        except ZeroDivisionError:
            continue

        hit = False
        for i in range(bins.shape[0]):
            if freq < bins[i] + stepSize/2:
                freqHist[i] += 1
                hit = True
                break
        if not hit:
            freqHist[-1] += 1
    return freqHist, bins

def maxRssiHistFromData(rssiData, timeData, timeWindowSize = 5.0, limits=(rssi_start, rssi_end)):
    # timeWindowsSize
    mxRssi = []
    timeWindow = []
    rssiWindow = []

    for index in range(0,len(timeData)):
        rssiWindow.append(rssiData[index])
        timeWindow.append(timeData[index])
        while timeWindow[-1] - timeWindow[0] > timeWindowSize:
            timeWindow.pop(0)
            rssiWindow.pop(0)
        # print(len(timeWindow), end=" ")
        mxRssi.append(np.max(rssiWindow))

    rssiHist, bins = np.histogram(mxRssi, limits[1] - limits[0],
                                  range=(limits[0], limits[1]))

    return rssiHist, bins

def maxModeRssiDistFromData(rssiData, timeData, timeWindowSize = 5.0, limits=(rssi_start, rssi_end)):
    # timeWindowsSize
    mxRssi = []
    timeWindow = []
    rssiWindow = []

    for index in range(0,len(timeData)):
        rssiWindow.append(rssiData[index])
        timeWindow.append(timeData[index])
        while timeWindow[-1] - timeWindow[0] > timeWindowSize:
            timeWindow.pop(0)
            rssiWindow.pop(0)
        # print(len(timeWindow), end=" ")
        mxRssi.append(np.max(rssiWindow))

    mxRssiHist, bins = np.histogram(mxRssi, limits[1] - limits[0],
                                  range=(limits[0], limits[1]))

    mxRssiHist = hist_normalize(mxRssiHist)

    # compute mean
    mx_mean = np.mean(mxRssi)

    # compute stdev
    mx_std = np.std(mxRssi)

    # compute median
    mx_median = np.median(mxRssi)

    # compute argmax
    mx_max = np.argmax(mxRssiHist) + rssi_start

    mxMdDataHist  = [np.round(mx_mean,2), np.round(mx_std,5), np.round(mx_median,2), np.round(mx_max, 2)]
    bins = ['mean', 'std', 'median', 'mode']

    return mxMdDataHist, bins


def meanRssiHistFromData(rssiData, timeData, timeWindowSize=5.0, limits=(rssi_start, rssi_end)):
    # timeWindowsSize
    mnRssi = []
    timeWindow = []
    rssiWindow = []

    for index in range(0, len(timeData)):
        rssiWindow.append(rssiData[index])
        timeWindow.append(timeData[index])
        while timeWindow[-1] - timeWindow[0] > timeWindowSize:
            timeWindow.pop(0)
            rssiWindow.pop(0)
        # print(len(timeWindow), end=" ")
        mnRssi.append(np.mean(rssiWindow))

    rssiHist, bins = np.histogram(mnRssi, limits[1] - limits[0],
                                  range=(limits[0], limits[1]))

    return rssiHist, bins

def medianRssiHistFromData(rssiData, timeData, timeWindowSize=5.0, limits=(rssi_start, rssi_end)):
    # timeWindowsSize
    mdRssi = []
    timeWindow = []
    rssiWindow = []

    for index in range(0, len(timeData)):
        rssiWindow.append(rssiData[index])
        timeWindow.append(timeData[index])
        while timeWindow[-1] - timeWindow[0] > timeWindowSize:
            timeWindow.pop(0)
            rssiWindow.pop(0)
        # print(len(timeWindow), end=" ")
        mdRssi.append(np.median(rssiWindow))

    rssiHist, bins = np.histogram(mdRssi, limits[1] - limits[0],
                                  range=(limits[0], limits[1]))

    return rssiHist, bins


def maxRssiHistFromDataDict_multi(dataValue, dataTime, sec_window, normalized = False):
    dataHist = {}
    bins = []
    for point in dataValue.keys():
        for dongle in dataValue[point].keys():
            for beacon in dataValue[point][dongle].keys():
                if not point in dataHist.keys():
                    dataHist[point] = {}
                if not dongle in dataHist[point].keys():
                    dataHist[point][dongle] = {}
                dataHist[point][dongle][beacon], bins = maxRssiHistFromData(
                    dataValue[point][dongle][beacon], dataTime[point][dongle][beacon], sec_window
                )
                if normalized:
                    dataHist[point][dongle][beacon] = hist_normalize(
                        dataHist[point][dongle][beacon])

    return dataHist, bins

def maxModeRssiDistFromDataDict_multi(dataValue, dataTime, sec_window):
    dataHist = {}
    bins = []
    for point in dataValue.keys():
        for dongle in dataValue[point].keys():
            for beacon in dataValue[point][dongle].keys():
                if not point in dataHist.keys():
                    dataHist[point] = {}
                if not dongle in dataHist[point].keys():
                    dataHist[point][dongle] = {}
                dataHist[point][dongle][beacon], bins = maxModeRssiDistFromData(
                    dataValue[point][dongle][beacon], dataTime[point][dongle][beacon], sec_window
                )

    return dataHist, bins


def rssiHistFromDataDict_multi(dataValue, normalized = False):
    dataHist = {}
    bins = []
    for point in dataValue.keys():
        for dongle in dataValue[point].keys():
            for beacon in dataValue[point][dongle].keys():

                if not point in dataHist.keys():
                    dataHist[point] = {}
                if not dongle in dataHist[point].keys():
                    dataHist[point][dongle] = {}
                dataHist[point][dongle][beacon], bins = rssiHistFromData(
                    dataValue[point][dongle][beacon]
                )
                if normalized:
                    dataHist[point][dongle][beacon] = hist_normalize(
                        dataHist[point][dongle][beacon])

    return dataHist, bins

def freqHistFromDataDict_multi(dataTime,
                           limits = (0, 5),
                           stepSize = .2,
                           timeWindowSize = 10,
                           normalized = False):
    freqHist = {}
    bins = []

    for point in dataTime.keys():
        for dongle in dataTime[point].keys():
            for beacon in dataTime[point][dongle]:
                if not point in freqHist.keys():
                    freqHist[point] = {}
                if not dongle in freqHist[point].keys():
                    freqHist[point][dongle] = {}

                freqHist[point][dongle][beacon], bins = freqHistFromData(
                    dataTime[point][dongle][beacon],
                    limits=limits,
                    stepSize = stepSize,
                    timeWindowSize=timeWindowSize
                )

                if normalized:
                    freqHist[point][dongle][beacon] = hist_normalize(
                        freqHist[point][dongle][beacon])

    return freqHist, bins

def sampleRandomPoint2dUniform(rect):
    # Generate random points given the area
    return (round(uniform(rect[0][0], rect[1][0]),3),
            round(uniform(rect[0][1], rect[1][1]),3))

def sampleRandomPoint2dNormal(point, sigma):
    # Generate random points given a reference point and a variance
    return (normalvariate(point[0], sigma),
           normalvariate(point[1], sigma))


def hist_merge(hists, weights, type='prop'):
    hist = np.zeros(len(hists[0]))
    if type == 'inv':
        weights = 1 - weights
        weights = weights / float(sum(weights))
    if not sum(weights) == 1:
        weights = weights / float(sum(weights))

    # print type(hists)
    for i in range(0, len(hists)):
        for j in range(0, len(hists[i])):
            hist[j] += hists[i][j] * weights[i]
    return hist

def hist_convex_combination(hist0, hist1, alpha):
    # compute the comvex combination of two vectors
    assert(validate(hist0,hist1))
    hist = np.zeros(len(hist0))
    for i in range(0,len(hist0)):
        hist[i] = hist0[i] * alpha + hist1[i] * (1-alpha)
    return hist

def hist_multiple_convex_combination(hists, alpha):
    # compute the comvex combination of multiple vectors
    # assert(validate(hist0,hist1))
    alpha = hist_normalize(alpha)
    hist = np.zeros(len(hists[0]))
    for i in range(0,len(hists[0])):
        for j in range(0,len(hists)):
            hist[i] += hists[j][i] * alpha[j]
    return hist
