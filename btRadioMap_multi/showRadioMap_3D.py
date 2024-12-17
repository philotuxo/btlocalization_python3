import sys, os, time

import numpy as np

sys.path.append("..")
from lib.histograms import *
from lib.parsers import *
from lib.paths import *
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import matplotlib.colors as mcol

dir_name = '/home/danis/1.15_28.1_15.46_19.8/'
# dir_name = '/home/danis/1.14_25.5_19.04_19.78/'
dev_file = "/home/danis/workspace/btlocalization/conf/tetam.dev"
beacon = 'e78f135624ce'
sensor = '000000000301'

grdFiles = os.listdir(dir_name)

data_grid = {}
gridParams = {}

# read devices
beacons, dongles = parseDevices(dev_file)
print(dongles.keys())

# read data
for grdFile in grdFiles:
    data_grid, gridParams = parse_grids_multi(dir_name + grdFile, data_grid)
    sizeGrid = gridParams['size_grid']
    print("Grids imported from %s." % grdFile)
    # print(data_grid.keys())

# generate surface
x_width = np.ceil((gridParams['limits'][1][0] - gridParams['limits'][0][0])/ gridParams['size_grid'])
y_width = np.ceil((gridParams['limits'][1][1] - gridParams['limits'][0][1])/ gridParams['size_grid'])

X, Y = np.meshgrid(
    np.arange(gridParams['limits'][0][0], gridParams['limits'][1][0] + gridParams['size_grid'],0.2 ),
    np.arange(gridParams['limits'][0][1], gridParams['limits'][1][1] + gridParams['size_grid'],0.2 )
)
Z = np.array(X)
Z_quar1 = np.array(X)
Z_quar3 = np.array(X)
Z_std = np.array(X)

for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        Z[i,j] = data_grid[(round(X[i,j],1),round(Y[i,j],1))][sensor][beacon][0]
        # Z_std[i,j] = -100 + data_grid[(round(X[i, j], 1), round(Y[i, j], 1))][sensor][beacon][1]
        # Z_quar1[i,j] = data_grid[(round(X[i,j],1),round(Y[i,j],1))][sensor][beacon][0] + \
        #                3* data_grid[(round(X[i, j], 1), round(Y[i, j], 1))][sensor][beacon][1]
        # Z_quar3[i,j] = data_grid[(round(X[i,j],1),round(Y[i,j],1))][sensor][beacon][0] - \
        #                3* data_grid[(round(X[i, j], 1), round(Y[i, j], 1))][sensor][beacon][1]

# mappable = plt.cm.ScalarMappable()
# mappable.set_array(Z)
# ax = plt.axes(projection='3d')
# ax.plot_surface(X,Y,Z, cmap="jet", alpha=.75)
# # ax.plot_wireframe(X,Y,Z_quar1, color = 'k', alpha = .25)
# # ax.plot_wireframe(X,Y,Z_quar3, color = 'k', alpha = .25)
# ax.plot_wireframe(X,Y,Z_std, color = 'k', alpha = .25)
#
# ax.plot3D([dongles[sensor][0][0],dongles[sensor][0][0]],
#           [dongles[sensor][0][1],dongles[sensor][0][1]],
#           [-100, -50], 'k-x', linewidth=8, alpha=.75, markersize=8, markeredgewidth=3)
# ax.set_zlim([-100,-50])
# plt.colorbar(mappable)
plt.rcParams["mathtext.fontset"] = "stix"
fig = plt.figure(figsize=(17,20))
# levels = [-80, -78, -76, -74, -72, -70, -68, -66, -64, -62, -60, -58, -56]
levels = [-80, -76, -72, -68, -64, -60, -56]
# levels = [-80, -77, -74, -71, -68, -65, -62, -59]

plt.imshow(Z.T, cmap="afmhot", vmin=-80, vmax=-56)
cbar = plt.colorbar(ticks=levels)
ctr = plt.contour(Z.T, levels=levels, origin='lower', cmap = 'gray_r')
cbar.add_lines(ctr)
plt.yticks(np.arange(0,x_width,15), labels=[])
plt.xticks(np.arange(0,y_width,15),labels=[])
plt.plot(dongles[sensor][0][1]/0.2,dongles[sensor][0][0]/0.2,'kx',markersize=12, markeredgewidth=2, markerfacecolor = (0,0,0,0), markeredgecolor = 'k')
# plt.plot(dongles[sensor][0][0]/0.2,dongles[sensor][0][1]/0.2,'yo',markersize=8)
cbar.ax.tick_params(labelsize=24)
# plt.title("$\mathrm{Standard~deviations~of~an~estimated~PRM~for~the~sensor}: \mathtt{" + sensor +"}$", fontsize=28)
# plt.axis("equal")

plt.show()