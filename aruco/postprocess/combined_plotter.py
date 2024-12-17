from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
import json

FONTSIZE_TICKS = 20
FONTSIZE_LABELS = 24

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = mplot3d.proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)


def parse_mbd_file(filePath):
    rssi_pose_data = []
    with open(filePath, 'r') as fid:
        for line in fid:
            lineList = line.strip().split(',')
            rssi_pose_data.append([
                float(lineList[0]),
                int(lineList[3]),
                float(lineList[4]),
                float(lineList[5]),
                float(lineList[6])
                ]
            )
    return rssi_pose_data

exp_name = "zigzag_rotsuz"

segmentFile = "/mnt/yedek/aruco_data/test02/segments/" + exp_name + "_segment.txt"
fileName = "/mnt/yedek/aruco_data/test02/registered/" + exp_name + "/sensor10_0.00_0.00_0.00.mbd"
rssi_pose_data = np.array(parse_mbd_file(fileName))

time_start = rssi_pose_data[0][0]
time_end = rssi_pose_data[-1][0]
timeStep = 1/(time_end - time_start)


fig = plt.figure(figsize=(12,6))
ax = plt.axes(projection='3d', proj_type='persp')

for line in rssi_pose_data:
    h = 1-(line[0] - time_start) * timeStep
    rgb = colors.hsv_to_rgb((0.3,1.0,h))
    ax.plot3D([line[2], line[2]], [line[3], line[3]],[-100, line[1]],'-',
              linewidth=5, color = rgb, alpha=.4)
    ax.plot3D([line[2]], [line[3]], [line[1]], '+',
          alpha=1, markersize=5, color = rgb)

fid = open(segmentFile, 'r')
for line in fid:
    lineJson = json.loads(line.strip())
    arrow = Arrow3D([lineJson[0][1], lineJson[1][1]],
              [lineJson[0][2], lineJson[1][2]],
              [-100, -100], lw=3, arrowstyle="->", color="k", alpha=.8,
                    mutation_scale=12)
    ax.add_artist(arrow)
    # ax.set_title("RSSI overlay")
fid.close()
ax.set_xlim3d(0.0,20.7)
ax.set_ylim3d(3.5,14)
ax.set_zlim3d(-100,-60)

ax.set_xlabel('\nx (m)', fontsize=FONTSIZE_LABELS)
ax.set_ylabel('\ny (m)', fontsize=FONTSIZE_LABELS)
ax.set_zlabel('\nRSSI (dB)', fontsize=FONTSIZE_LABELS)
ax.set_xticks(np.arange(0,21,3))
ax.set_yticks(np.arange(4,14,3))
ax.set_zticks(np.arange(-100,-50,10))
ax.view_init(elev=25., azim=40)
# limits = np.array([getattr(ax, f'get_{axis}lim')() for axis in 'xyz'])
# print([getattr(ax, f'get_{axis}lim')() for axis in 'xyz'])
ax.set_box_aspect(np.ptp([(0.0, 20.7), (0.0, 17.5), (0, 7)], axis = 1))
plt.setp(ax.get_xticklabels(), fontsize=FONTSIZE_TICKS)
plt.setp(ax.get_yticklabels(), fontsize=FONTSIZE_TICKS)
plt.setp(ax.get_zticklabels(), fontsize=FONTSIZE_TICKS)

legend_custom = [Line2D([0],[0], color = colors.hsv_to_rgb((0.3,1.0,1)),lw = 8),
                 Line2D([0],[0], color = colors.hsv_to_rgb((0.3,1.0,0)),lw = 8)]

ax.legend(legend_custom, ['Start', 'Finish'], fontsize=FONTSIZE_LABELS)
plt.show()
