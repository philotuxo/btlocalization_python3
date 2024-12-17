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
import time

FONTSIZE_TICKS = 16
FONTSIZE_LABELS = 12

def ind_to_coord(ind, params):
    # single index to coordinates
    coord_ind = (ind % params["limits_ind"][0], ind // params["limits_ind"][0])
    return (coord_ind[0] * params["size_grid"],
            coord_ind[1] * params["size_grid"])

def coord_to_ind(coord, params):
    # coordinates to single index
    # coordinates are metric
    coord_ind = (
        int(coord[0] / params["size_grid"]),
        int(coord[1] / params["size_grid"])
                 )
    return coord_ind[1] * params["limits_ind"][0] + coord_ind[0]

def coord_to_ind2d(coord, params):
    return (
        int(coord[0] / params["size_grid"]),
        int(coord[1] / params["size_grid"])
                 )

search_dir = "/home/serhan/btlocalization_data/grd/tetam_multi" \
             "/wassBest_mxrssi_2.0_1.0/"
files = os.listdir(search_dir)
print(files)

beacon = 'e78f135624ce'
data_grid = {}
params_grid = None
for file in files:
    data_grid, params_grid = parse_grids_multi(search_dir + file,data_grid)

params_grid["limits_ind"] = (
        int(np.ceil(params_grid["limits"][1][0]/params_grid["size_grid"])) + 1,
        int(np.ceil(params_grid["limits"][1][1]/params_grid["size_grid"])) + 1
)

N = len(data_grid.keys())
A = np.zeros((N, N))

out_dict = {}

for coord in data_grid.keys():
    coord_ind = coord_to_ind2d(coord, params_grid)
    ind = coord_to_ind(coord, params_grid)
    for sensor in data_grid[coord].keys():
        if sensor not in out_dict.keys():
            out_dict[sensor] = np.zeros((len(params_grid["bins"]),N))

        for binind in range(len(data_grid[coord][sensor][beacon])):
            out_dict[sensor][binind,ind] = data_grid[coord][sensor][beacon][
                binind]

fig3 = plt.figure(constrained_layout=True, figsize=(12,8))
gs = fig3.add_gridspec(6, 2)

i = 0
for sensor in out_dict.keys():
    axl = fig3.add_subplot(gs[i%6, i//6])
    print(out_dict[sensor].shape)
    axl.imshow(out_dict[sensor], cmap="gray_r")
    # axl.set_title(str(sensor), fontsize=FONTSIZE_LABELS)
    axl.set_xticks([])
    axl.set_yticks([])
    i+=1

# for sensor in out_dict.keys():
#     plt.figure()
#     plt.imshow(out_dict[sensor], cmap='gray_r')
plt.show()


