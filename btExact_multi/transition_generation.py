import sys, os, time, re
sys.path.append("..")

from lib.simulationThread_multi import *
# from btParticle_multi.btParticle_multi_gui import *
from queue import Queue
import json
from scipy.stats import multivariate_normal
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix

def ind_to_coord(ind, params):
    # single index to coordinates
    coord_ind = (ind % params["limits_ind"][0], ind // params["limits_ind"][0])
    return (coord_ind[0] * params["size_grid"],
            coord_ind[1] * params["size_grid"])

def ind2d_to_coord(coord_ind, params):
    return (round(coord_ind[0] * params["size_grid"],1),
            round(coord_ind[1] * params["size_grid"],1))


def coord_to_ind(coord, params):
    # coordinates to single index
    # coordinates are metric
    coord_ind = (
        int(round(coord[0] / params["size_grid"])),
        int(round(coord[1] / params["size_grid"]))
                 )
    return coord_ind[1] * params["limits_ind"][0] + coord_ind[0]

def coord_to_ind2d(coord, params):
    return (
        int(coord[0] / params["size_grid"]),
        int(coord[1] / params["size_grid"])
                 )

def gauss_filter(size, cov=2.0):
    filter_size = size * 2 + 1
    x = np.linspace(0, filter_size, filter_size, endpoint=False)
    y = multivariate_normal.pdf(x, size, cov)

    y = y.reshape(1, filter_size)
    # normalize
    y = y / y.sum()

    GF = y.T @ y
    return GF

grid_size = "1.0"

mask_size = 1
gauss_mask = gauss_filter(mask_size, cov = 1.0)
# gauss_mask = np.array([[0.05, 0.1, 0.05],[0.1,0.4,0.1],[0.05, 0.1,0.05]])
print(gauss_mask)

data_grid = {}
data_grid, params_grid = parse_grids_multi(
    "/home/serhan/btlocalization_data/grd/tetam_multi"
    "/wassBest_" +
    grid_size + "/tetam_multi_rssi_000000000101_" +
    grid_size + ".grd",data_grid)

params_grid["limits_ind"] = (
        int(np.ceil(params_grid["limits"][1][0]/params_grid["size_grid"])) + 1,
        int(np.ceil(params_grid["limits"][1][1]/params_grid["size_grid"])) + 1
)

occ_grid = {}
occ_grid, params_occ = parse_occupancy(
    "/home/serhan/btlocalization_data/occ/tetam_" + grid_size + ".occ",occ_grid)

# print(occ_grid)
print(params_grid["limits_ind"])

N = len(data_grid.keys())
A = np.zeros((N, N))
flag = (
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 0),
    (1, 1),
    (1, 2),
    (2, 0),
    (2, 1),
    (2, 2)
)
for coord in data_grid.keys():
    # print(counter)
    coord_ind = coord_to_ind2d(coord, params_grid)
    ind = coord_to_ind(coord, params_grid)

    # if not (coord_ind in flag):
    #     continue
    # print(ind, coord_ind)

    for i in range(gauss_mask.shape[0]):
        x_diff = i - mask_size
        temp_x_ind = coord_ind[0] + x_diff
        # if temp_x_ind < 0 or temp_x_ind >= params_grid["limits_ind"][0]:
        #     continue
        for j in range(gauss_mask.shape[1]):
            y_diff = j - mask_size
            temp_y_ind = coord_ind[1] + y_diff
            if temp_y_ind < 0 or \
                    temp_y_ind >= params_grid["limits_ind"][1] or \
                    temp_x_ind < 0 or \
                    temp_x_ind >= params_grid["limits_ind"][0] or \
                    occ_grid[ind2d_to_coord(
                        (temp_x_ind, temp_y_ind),params_grid)
                        ] == 1:
                A[ind, ind] = A[ind, ind] + gauss_mask[i,j]
                # print(ind, coord_ind[0], coord_ind[1], x_diff, y_diff,
                #       temp_x_ind,
                #       temp_y_ind)
                continue

            temp_ind = temp_y_ind * params_grid["limits_ind"][0] + temp_x_ind
            # print(temp_x_ind, temp_y_ind, temp_single_ind)
            A[ind, temp_ind] = A[ind, temp_ind] + gauss_mask[i,j]
            # print(x_diff, y_diff, temp_x_ind, temp_y_ind, temp_ind)
            # print(ind, coord_ind[0], coord_ind[1], x_diff, y_diff,
            #       temp_x_ind,
            #       temp_y_ind, temp_ind)

# vector = np.random.rand(A.shape[0],1) * 5
# print(vector)
sparse_A = csr_matrix(A)
overProb = np.where(A > 1.0)
# print(A[:10,:10])
# print(np.sum(A))
np.set_printoptions(threshold=sys.maxsize)
print(np.sum(A, axis=1))
# print(A[:,2])
# print(sparse_A)
# for i in range(30):
#     start_time = time.time()
#     B = A @ vector
#     print(time.time() - start_time)

plt.imshow(A, cmap='gray_r')
plt.show()
