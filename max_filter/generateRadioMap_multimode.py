import numpy as np
from scipy.stats import beta, norm
from matplotlib import pyplot as plt

def m(input, params):
    # input in [0,1]
    # base, ceil, scale should be different for each sensor
    base, ceil, scale = params
    return base + scale * input, ceil - scale*input

def s(input, params):
    # input in [0,1]
    # base, ceil, scale should be different for each sensor
    base, ceil, scale = params
    return base + scale * input, ceil - scale * input

def generate_hist(x, y, params, rssi_range, map_range):
    xParam = x / (map_range[1][0] - map_range[0][0])
    yParam = y / (map_range[1][1] - map_range[0][1])
    assert (xParam <= 1 and xParam >= 0 and yParam <=1 and yParam >=0 )

    mParams = params[0:3]
    sParams = params[3:6]

    p = np.arange(rssi_range[0], rssi_range[1], 1)
    m1, m2 = m(xParam, mParams)
    s1, s2 = s(xParam, sParams)

    gauss1 = norm.pdf(p, loc=m1, scale=s1)
    gauss2 = norm.pdf(p, loc=m2, scale=s2)

    mixture = params[6] * gauss1 + (1-params[6]) * gauss2

    mixture = mixture/sum(mixture)

    return p, mixture


# first three for m, second three for s
sensor_params = [
    [ -100, -40, 10, 1, 3, 3, .4 ],
    [ -92, -30, 5, 1, 3, 2, .6 ],
    [ -90, -60, 8, 1, 3, 1.5, .8],
    [ -80, -40, 15, 1, 3, 2.5, .3],
]

rssiRange = [-120, -20]
mapRange = [[0,0],[8, 6]]

for i in sensor_params:
    bins, hist = generate_hist(2, .2, i,rssiRange,mapRange)
    plt.bar(bins,hist)

plt.show()