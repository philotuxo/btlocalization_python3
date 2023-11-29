import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import random
import sys

def scaler(distance):
    return distance * -7 - 25

def get_histogram(distance, bins):
    hist = norm.pdf(bins,loc=scaler(distance), scale=1)
    return hist

def euclid_dist(beacon, point):
    return np.sqrt((beacon[0] - point[0]) **2 +
                   (beacon[1] - point[1]) ** 2)

def sigmoid(x):
    return 1/(1+np.exp(-x))

def sigmoidDeriv(x):
    return np.multiply(x,(1-x))

def ann_forward(X,W,V,K):
    # feedforward hidden layer
    Z = sigmoid(np.dot(X,W))
    Z = np.concatenate((Z, np.ones([K,1])), axis=1)
    Yhat = sigmoid(np.dot(Z,V))
    return Yhat, Z

area_rect = [[0,0], [10,10]]
beacon_pos = [0,5]

X = []
Y = []

bins = range(-120, -20)

# sample area with 1 meters
for i in range(area_rect[0][0],area_rect[1][0]):
    for j in range(area_rect[0][1],area_rect[1][1]):
        dist = euclid_dist(beacon_pos, [i,j])
        hist = get_histogram(dist, bins)
        X.append(dist)
        Y.append(hist)

# divide training and validation sets
perm = np.random.permutation(len(X)).tolist()
Xtrain = np.matrix([X[i] for i in perm[:70]]).T
Xvalid = np.matrix([X[i] for i in perm[70:]]).T
Ytrain = np.matrix([Y[i] for i in perm[:70]])
Yvalid = np.matrix([Y[i] for i in perm[70:]])


minError = 50000
N = 1 # input size
M = 40 # hidden layer size
K = 70
H = len(bins)
R = 5000
replay = 10

Xtrain = np.append(Xtrain, np.ones([70,1]),axis=1)

# weights: initialize all weights randomly
W = np.random.random((N + 1, M)) - 1  # last index is the bias
V = np.random.random((M + 1, H)) - 1  # last index is the bias

for j in range(R):
    # print(j)

    # estimation
    Yhat, Z = ann_forward(Xtrain, W, V, K)

    # obtain l2 error
    Y_error = Ytrain - Yhat

    ErrorTotal = np.mean(np.sum(abs(Y_error)))

    if ErrorTotal < minError:
        minError = ErrorTotal
        minW = W
        minV = V

        # # in what direction is the target value?
        # # were we really sure? if so, don't change too much.

        Y_delta = np.multiply(Y_error, sigmoidDeriv(Yhat))

        # how much did each l1 value contribute to the l2 error (according to the
        # weights)?
        Z_error = Y_delta.dot(V.T)

        # # in what direction is the target l1?
        # # were we really sure? if so, don't change too much.

        Z_delta = np.multiply(sigmoidDeriv(Z),Z_error)

        # print W.shape
        # print X.T.shape
        # print Z_delta.shape
        V += Z.T.dot(Y_delta)
        W += Xtrain.T.dot(Z_delta)[:, :-1]


# print(W.shape)
# print(V.shape)
sample = np.append(Xvalid[0],[[1]],axis=1)

print(Xvalid[0])
print(Yvalid[0])
Yhat, Z = ann_forward(sample,W,V,1)
print(Yhat)
