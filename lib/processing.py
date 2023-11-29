import math
import sys
from itertools import combinations
import random
import numpy as np
import scipy.signal as sgn

rssi_start = -100
rssi_end = -20

def orientation(point0, point1):
    # returns the orientation of a line passing two points as a scale in [-1, 1]
    if point1 == point0:
        return None
    if point1[0] == point0[0]:
        return 1.0

    return math.atan((point1[1] - point0[1]) / (point1[0] - point0[0]))/\
           math.pi * 2

def are_aligned(interpoint, point0, point1, th=0.2):
    # check if three points are aligned
    # threashold is the length of the normal to the point0-point1 segment

    lengthNormal = abs((point1[1] - point0[1]) * interpoint[0]
                       - (point1[0] - point0[0]) * interpoint[1]
                       + point1[0] * point0[1] - point1[1] * point0[0]) \
                   / math.sqrt((point1[1] - point0[1]) ** 2
                               + (point1[0] - point0[0]) ** 2
                               )
    if lengthNormal < th:
        return True
    else:
        return False

def dist_euclid(point0, point1):
    if len(point0) == 3 and len(point1) == 3:
        return math.sqrt((point0[0] - point1[0]) ** 2 +
                         (point0[1] - point1[1]) ** 2 +
                         (point0[2] - point1[2]) ** 2)
    else:
        return math.sqrt((point0[0] - point1[0])**2 +
                     (point0[1] - point1[1])**2 )

def find_close_points(point, pointList, radius=1.25, numMax=0):
    # return the <numMax> points that are in the circle of radius <radius> in
    #  meters
    closest = []
    retClose = []
    for otherPoint in pointList:
        dist = dist_euclid(otherPoint, point)
        # automatically pass the same point
        if dist == 0:
            continue
        if dist < radius:
            closest.append((otherPoint, dist))

    closest = sorted(closest, key=lambda pair: pair[1])
    counter = 0
    for i in closest:
        retClose.append(i[0])
        counter += 1
        if not numMax == 0:
            if counter == numMax:
                break
    return retClose

def find_all_pairs(point, pointList, ori=None, tol=.05, align=0.2):
    # find all the closest pairs that are aligned with the point
    # with specific orientation (if given)
    combs = combinations(pointList, 2)
    retCombs = []
    if not ori == None:
        if ori + 1 < tol:
            tolRange = [ori - tol + 2, ori + tol]
        else:
            if 1 - ori < tol:
                tolRange = [ori - tol, ori + tol - 2]
            else:
                tolRange = [ori - tol, ori + tol]

    for comb in combs:
        if are_aligned(point, comb[0], comb[1], th=align):
            if not ori == None:
                sampleOri = orientation(comb[0], comb[1])
                if tolRange[1] < tolRange[0]:  # different edges
                    if sampleOri < tolRange[1] or sampleOri > tolRange[0]:
                        retCombs.append(comb)
                else:
                    if tolRange[0] < sampleOri and sampleOri < tolRange[1]:
                        retCombs.append(comb)
            else:
                retCombs.append(comb)
    return retCombs


def sampleRandomPoint2dUniform(rect):
    # Generate random points given the area
    return (round(random.uniform(rect[0][0], rect[1][0]), 3),
            round(random.uniform(rect[0][1], rect[1][1]), 3))


def sampleRandomPoint2dNormal(point, sigma):
    # Generate random points given a reference point and a variance
    return (random.normalvariate(point[0], sigma),
            random.normalvariate(point[1], sigma))

def sampleFrom(cumulative, pattern = None):
    rnd = random.uniform(0, 1)
    for i in range(len(cumulative)):
        if rnd <= cumulative[i]:
            if pattern == None:
                ret = i
            else:
                ret = pattern[i]
            break
    return ret


def getCumulative(prob_vector):
    # prepare the cumulative sum for inversion
    cumulative = list(np.cumsum(prob_vector))
    s = float(cumulative[-1])
    # normalize
    if s == 0.0:
        cumulative[0] = 1/len(cumulative)
        for i in range(1, len(cumulative)):
            cumulative[i] = cumulative[i-1] + cumulative[0]
    else:
        for i in range(len(cumulative)):
            cumulative[i] = cumulative[i] / s

    return cumulative

def randgen(cumul_vector, sampleSize, pattern=None):
    # generate a random value given a discrete vector of probabilities
    # pattern should have the same size with prob_vector
    ret = [None] * sampleSize
    for j in range(sampleSize):
        ret[j] = sampleFrom(cumul_vector, pattern)

    return ret

def find_best_pair(point, pointList, orient=None, radius=None):
    # print(point)
    # print(pointList)
    # radius = self.ui.sliderR.value() / 100.0 * round(math.sqrt(
    #         self.params["limits"][1][0]**2 +
    #         self.params["limits"][1][1]**2
    #     ),2)
    points = find_close_points(point, pointList, radius)
    pairs = find_all_pairs(point, points, ori=orient)
    # print(points)
    # pair = find_best_pair(latest,pairs)
    return points, pairs


def calculate_t(pointx, point1, point2, type='linear'):
    # t estimation via distance to the fingerprints
    dist1 = dist_euclid(pointx, point1)
    dist2 = dist_euclid(pointx, point2)
    dist0 = dist_euclid(point1, point2)

    if type == 'linear':
        d1 = dist1
        d2 = dist2
        d0 = dist0
    elif type == 'quad':
        d1 = dist1 ** 2
        d2 = dist2 ** 2
        d0 = dist0 ** 2
    elif type == 'log':
        d1 = math.log(dist1)
        d2 = math.log(dist2)
        d0 = math.log(dist0)
    elif type == 'exp':
        d1 = math.exp(dist1)
        d2 = math.exp(dist2)
        d0 = math.exp(dist0)
    elif type == 'cubic':
        d1 = dist1 ** 3
        d2 = dist2 ** 3
        d0 = dist0 ** 3
    else:
        print("No type mapping supplied.")
        sys.exit(0)

    if d1 >= d0:
        return d1 / d0

    if d2 >= d0:
        return -d1 / d0

    return d1 / d0

def hist_wasserstein(hist0, hist1):
    # calculate the wasserstein metric
    # and generate the mapping between hist0 to hist1
    assert(validate(hist0, hist1))

    x = np.array(hist0,dtype=np.float128)
    y = np.array(hist1,dtype=np.float128)
    WasserMap = {}
    SIZE = len(x)

    SUM = np.float128(0.0)
    i = np.float128(0.0)
    j = np.float128(0.0)

    while i < SIZE and j < SIZE:
        if x[int(i)] == 0 and not i == SIZE - 1:
            i = i + 1.0
            continue
        if y[int(j)] == 0 and not j == SIZE - 1:
            j = j + 1.0
            continue

        if x[int(i)] < y[int(j)]:
            y[int(j)] = y[int(j)] - x[int(i)]
            SUM = SUM + x[int(i)] * abs(i-j)
            WasserMap[(i,j)] = x[int(i)]
            x[int(i)] = np.float128(0)
            i = i + 1
        else:
            x[int(i)] = x[int(i)] - y[int(j)]
            SUM = SUM + y[int(j)] * abs(i-j)
            WasserMap[(i,j)] = y[int(j)]
            y[int(j)] = np.float128(0)
            j = j + 1

    return SUM, WasserMap

def hist_wasserstein_matrix(hist0, hist1, bins = None):
    assert(validate(hist0, hist1))

    x = np.array(hist0,dtype=np.float128)
    y = np.array(hist1,dtype=np.float128)
    WasserMap = np.zeros([len(x), len(y)],dtype=np.float128)
    SIZE = len(x)

    SUM = 0
    i = 0
    j = 0

    while i < SIZE and j < SIZE:
        if x[i] == 0 and not i == SIZE - 1:
            i = i + 1
            continue
        if y[j] == 0 and not j == SIZE - 1:
            j = j + 1
            continue

        if x[i] < y[j]:
            y[j] = y[j] - x[i]
            if bins is not None:
                SUM = SUM + x[i] * abs(bins[i] - bins[j])
            else:
                SUM = SUM + x[i] * abs(i-j)
            WasserMap[(i,j)] = x[i]
            x[i] = 0
            # print(i,j,'x')
            i = i + 1
        else:
            x[i] = x[i] - y[j]
            if bins is not None:
                SUM = SUM + x[i] * abs(bins[i] - bins[j])
            else:
                SUM = SUM + x[i] * abs(i-j)
            WasserMap[(i,j)] = y[j]
            y[j] = 0
            # print(i,j,'y')
            j = j + 1

    return SUM, WasserMap


def hist_wasserstein_interpolation(mapping, t, beta, bins):
    # print mapping
    hist = np.zeros(len(bins))

    # print alpha, beta
    for each in mapping.keys():
        # k = each[0] + alpha * (each[1]-each[0])
        # k1 = int(k + (each[0]-k) * (1-beta))
        # k2 = int(k + (each[1]-k) * (1-beta))
        k1 = int(np.ceil(each[0] + t * beta * (each[1] - each[0])))
        k2 = int(np.ceil(each[1] + (1-t) * beta * (each[0] - each[1])))
        if k1 < 0 or k1 >= len(hist) or k2 < 0 or k2 >= len(hist):
            continue

        hist[k1] = hist[k1] + abs(1-t)/float(abs(1-t) + abs(t)) * mapping[each]
        hist[k2] = hist[k2] + abs(t)/float(abs(1-t) + abs(t)) * mapping[each]
    return hist


def hist_wasserstein_interpolation_smooth(mapping, t, beta,
                                   limits=(rssi_start, rssi_end)):
    # print mapping
    hist = np.zeros(limits[1] - limits[0], dtype=np.float128)
    t = np.float128(t)

    ltest = []

    for each in mapping.keys():
        k = np.float128(each[0] + t * (each[1]-each[0]))
        k1 = k + (each[0]-k) * (1.0 - beta)
        k2 = k + (each[1]-k) * (1.0 - beta)

        ltest.append((each, k,k1,k2,mapping[each]))
        if k1 == np.floor(k1):
            hist[int(np.ceil(k1))] = \
                hist[int(np.ceil(k1))] + (1.0 - t) * mapping[each]

        else:
            w11 = k1 - np.floor(k1)
            k11 = int(np.floor(k1))
            w12 = 1.0-w11
            k12 = int(np.ceil(k1))

            hist[k11] = hist[k11] + \
                        abs(1 - t) / float(abs(1 - t) + abs(t)) \
                        * mapping[each] * w12
            hist[k12] = hist[k12] + \
                        abs(1 - t) / float(abs(1 - t) + abs(t)) \
                        * mapping[each] * w11


        if k2 == np.floor(k2):
            hist[int(np.floor(k2))] = \
                hist[int(np.floor(k2))] + t * mapping[each]

        else:
            w21 = k2 - np.floor(k2)
            k21 = int(np.floor(k2))
            w22 = 1.0-w21
            k22 = int(np.ceil(k2))

            hist[k21] = hist[k21] + \
                        abs(t) / float(abs(1 - t) + abs(t)) \
                        * mapping[each] * w22
            hist[k22] = hist[k22] + \
                        abs(t) / float(abs(1 - t) + abs(t)) \
                        * mapping[each] * w21

    ltest.sort(key=lambda tup: tup[1])
    # for i in ltest:
    #     print(i[0],round(i[1],2),i[2],i[3],i[4])

    return hist


def validate(hist0, hist1):
    if len(hist0) == len(hist1):
        return True
    else:
        print("Error: Vector lengths not equal")
        return False

def get_grid_best_mode(data_grid, params_grid):

    data_grid_maxed = {}
    params_grid_maxed = params_grid.copy()
    params_grid_maxed["bins"] = [0]

    for ind in data_grid.keys():
        for dongle in data_grid[ind].keys():
            for beacon in data_grid[ind][dongle].keys():
                if ind not in data_grid_maxed.keys():
                    data_grid_maxed[ind] = {}
                if dongle not in data_grid_maxed[ind].keys():
                    data_grid_maxed[ind][dongle] = {}
                hst = data_grid[ind][dongle][beacon]
                peaks = sgn.find_peaks(hst, height=.1)
                best_rssi = params_grid["bins"][peaks[0][-1]]
                data_grid_maxed[ind][dongle][beacon] = [best_rssi]

    return data_grid_maxed, params_grid_maxed

def get_grid_mode(data_grid, params_grid):

    data_grid_maxed = {}
    params_grid_maxed = params_grid.copy()
    params_grid_maxed["bins"] = [0]

    for ind in data_grid.keys():
        for dongle in data_grid[ind].keys():
            for beacon in data_grid[ind][dongle].keys():
                if ind not in data_grid_maxed.keys():
                    data_grid_maxed[ind] = {}
                if dongle not in data_grid_maxed[ind].keys():
                    data_grid_maxed[ind][dongle] = {}
                hst = data_grid[ind][dongle][beacon]
                bins = params_grid["bins"]
                # assert(False)
                SUM = 0
                WEIGHT = 0
                for i in range(len(params_grid['bins'])):
                    SUM += hst[i] * bins[i]
                    WEIGHT += hst[i]
                best_freq = SUM / WEIGHT
                print(best_freq)
                data_grid_maxed[ind][dongle][beacon] = [best_freq]

    return data_grid_maxed, params_grid_maxed

