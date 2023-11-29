import os, sys
sys.path.append("..")
from lib.histograms import *
from lib.parsers import *
from lib.paths import *
from multiprocessing import Queue
from multiprocessing import Process
import threading

class FileThread (threading.Thread):
    def __init__(self, name, fileBase, dongles, wQueue, grid_size):
        threading.Thread.__init__(self)
        self.name = name
        self.fids = {}
        for dongle in dongles:
            self.fids[dongle] = open(fileBase + "_" +
                                     dongle + "_" +
                                     str(grid_size) +
                                     ".grd", 'w+')
        self.wQueue = wQueue

    def save(self,dongle, message):
        self.fids[dongle].write(message)
        self.fids[dongle].flush()

    def run(self):
        while True:
            dongle, to_be_logged = self.wQueue.get()
            if to_be_logged == "QUIT":
                break
            self.save(dongle, to_be_logged)

        for dongle in dongles:
            self.fids[dongle].close()

def workerFunction(pQueue, wQueue, dataHist, beacons, dongles, beta = 1.0):

    while True:
        align=0.5
        if pQueue.qsize() > 0:
            data = pQueue.get()
            if data == "QUIT":
                print("Ending Process")
                break

            i = data[0]
            j = data[1]
            point = data[2]

            # find the closest points to the given point with a radius of 15m
            pointList = find_close_points(point, dataHist.keys(), radius = 15)

            # get all the possible pairs in this point list
            pairs = find_all_pairs(point, pointList, align = align)
            while not len(pairs):
                align = align + 0.01
                pairs = find_all_pairs(point, pointList, align=align)

            # get the first pair
            pair = pairs[0]

            print(j, i, len(pairs), align)
            for dongle in dongles.keys():
                for beacon in beacons.keys():
                    # get t value for the triplet
                    S, mapping = hist_wasserstein(
                        dataHist[pair[0]][dongle][beacon],
                        dataHist[pair[1]][dongle][beacon]
                    )

                    t = calculate_t(point, pair[0], pair[1])
                    hist = hist_wasserstein_interpolation(mapping, t, beta,
                                                          bins)

                    # apply a gaussian smoother here
                    # hist = np.convolve(hist,[0.001, 0.157, 0.684, 0.157, 0.001])

                    wQueue.put([dongle,
                        str(list(point)) + delimiter  +\
                        str(beacon) + delimiter + \
                        str(list(hist)) + "\n"
                               ])

if len(sys.argv) > 3:
    hstFile = sys.argv[1]
    parFile = sys.argv[2]
    grid_size = float(sys.argv[3])
else:
    print("Not enough parameters.")
    print("Usage: gridder <histFile> <parFile> <grid_size>")
    sys.exit()

dataHist, bins, beacons, dongles = parse_hist_multi(hstFile)

numProcess = 4

params = parseParameters(parFile)

fileBase = os.path.splitext(os.path.basename(hstFile))[0]

beta = 1.0,
delimiter = "::"

# write queue
wQueue = Queue()
fThread = FileThread("FileThread", fileBase, dongles, wQueue, grid_size)
fThread.start()

# divide the world into grids
widthGrid =  int(np.ceil(
        params["limits"][1][0]/grid_size)) + 1
heightGrid = int(np.ceil(
        params["limits"][1][1]/grid_size)) + 1

hist = np.zeros(rssi_end - rssi_start)
header = str([ list(params["limits"][0]),list(params["limits"][1])]) +\
         delimiter + str(grid_size) + delimiter + str(bins) + "\n"
for dongle in dongles:
    header_with_dongle = dongle + delimiter + header
    wQueue.put([dongle, header_with_dongle])

# create and start processes
processes = []

# process queue
pQueue = Queue()
for i in range(numProcess):
    p = Process(target=workerFunction, args=(pQueue,
                                             wQueue,
                                             dataHist,
                                             beacons,
                                             dongles))
    processes.append(p)

for p in processes:
    p.start()

# generate cellVisuals
for j in range(heightGrid):
    for i in range(widthGrid):
        point = (round(params["limits"][0][0] + i
                       *grid_size,2),
                 round(params["limits"][0][1] + j
                       *grid_size,2) )
        pQueue.put([i,j,point])

# ending processes
for p in range(numProcess):
    pQueue.put("QUIT")

for p in processes:
    p.join()

wQueue.put([None, "QUIT"])
fThread.join()
