import sys, os, time, re
sys.path.append("..")

from lib.simulationThread_multi import *
from btExact_multi.btExact_multi_gui import *
from scipy.stats import multivariate_normal
from scipy.sparse import csr_matrix
from queue import Queue
import json
import numpy as np

SEC_SLEEP = 0.00001

class btExact_multi(threading.Thread):
    def __init__(self,
                 threadName,
                 simControlQueue,
                 dataReadQueue,
                 config_file,
                 guiQueue = None,
                 logQueue = None):
        threading.Thread.__init__(self)
        self.name = threadName
        self.data_grid = {}
        self.data_occ = {}
        self.params = {}
        self.simQueue = simControlQueue
        self.dataQueue = dataReadQueue
        self.logQueue = logQueue
        self.guiQueue = guiQueue
        self.config_file = config_file
        self.flagExit = False
        self.ground = None
        self.best_cell_coord = None
        self.best_estimates = []

        self.rssi_window = {}
        self.time_window = {}
        self.time_window_size = None

        self.read_config_file(config_file)
        self.read_grid_dir()
        self.read_occupancy()
        self.hmm_initialize()


    def run(self):

        # TODO: GUI

        # send track file
        if "sec_window" in self.params.keys():
            self.time_window_size = self.params["sec_window"]

        if "track_file" in self.params.keys():
            self.simQueue.put(("F", self.params["track_file"]))

        self.times = []
        self.times_real = []
        self.error = []
        self.mult_times = []
        self.err = 0.0
        self.acc_err = 0.0
        self.accumulation = 0
        self.count = 0

        # send wait amount
        if self.params['gui'] == True:
            send_wait_seconds = 10
            self.guiQueue.put(('G', self.params['size_grid']))
        else:
            send_wait_seconds = 0
        if self.simQueue:
            self.simQueue.put(('W', send_wait_seconds))
        # send the start signal
        if self.simQueue:
            self.simQueue.put(( 'S', None ))

        while True:
            retVal = self.hmm_single_step()
            if retVal == "EoF":
                print("EoF received")
                break
            time.sleep(SEC_SLEEP)

        self.exit()

    def ind_to_coord(self, ind, params):
        # single index to coordinates
        coord_ind = (
            ind % params["limits_ind"][0], ind // params["limits_ind"][0])
        return (round(coord_ind[0] * params["size_grid"],1),
                round(coord_ind[1] * params["size_grid"],1))

    def coord_to_ind(self, coord, params):
        # coordinates to single index
        # coordinates are metric
        coord_ind = (
            int(round(coord[0] / params["size_grid"])),
            int(round(coord[1] / params["size_grid"]))
        )
        return coord_ind[1] * params["limits_ind"][0] + coord_ind[0]

    def coord_to_ind2d(self, coord, params):
        return (
            int(coord[0] / params["size_grid"]),
            int(coord[1] / params["size_grid"])
        )

    def ind2d_to_coord(self, coord_ind, params):
        return (round(coord_ind[0] * params["size_grid"],1),
                round(coord_ind[1] * params["size_grid"],1))


    def gauss_filter(self, size, cov=1.0):
        filter_size = size * 2 + 1
        x = np.linspace(0, filter_size, filter_size, endpoint=False)
        y = multivariate_normal.pdf(x, size, cov)

        y = y.reshape(1, filter_size)
        # normalize
        y = y / y.sum()

        GF = y.T @ y
        return GF

    def hmm_initialize(self):
        # size of grids (state space size)
        self.N = len(self.data_grid.keys())

        self.rssi_start  = int(self.params["bins"][0])

        # give a unique number for a grid cell and point to that number from
        # the grid cell

        self.time_cur = 0
        # PREPARE FORWARD MESSAGE
        # alpha message
        # self.logAlpha = np.empty((self.N,1))
        self.alpha = np.ones((self.N,1)) * 1.0/self.N
        # self.mx = 0

        # alpha predict
        # self.logAlphaPredict = np.zeros((self.N,1))
        self.alphaPredict = np.zeros((self.N, 1))

        self.hmm_get_transition()

    def hmm_get_transition(self):
        # create an empty transition matrix
        A = np.zeros((self.N, self.N))
        gauss_mask = self.gauss_filter(
            self.params['mask_size'],
            self.params['diffusion'])

        self.params["limits_ind"] = (
            int(np.ceil(
                self.params["limits"][1][0] /
                    self.params["size_grid"])) + 1,
            int(np.ceil(
                self.params["limits"][1][1] /
                    self.params["size_grid"])) + 1
        )

        print(self.params["limits_ind"])
        # print(self.data_occ.keys())

        for coord in self.data_grid.keys():
            coord_ind = self.coord_to_ind2d(coord, self.params)
            ind = self.coord_to_ind(coord, self.params)
            # print(coord, coord_ind, ind)

            for i in range(gauss_mask.shape[0]):
                x_diff = i - self.params['mask_size']
                temp_x_ind = coord_ind[0] - x_diff

                for j in range(gauss_mask.shape[1]):
                    y_diff = j - self.params['mask_size']
                    temp_y_ind = coord_ind[1] - y_diff
                    # convert temp_y_ind to metric coordinates
                    # self.ind

                    if temp_y_ind < 0 \
                            or temp_y_ind >= self.params["limits_ind"][1] \
                            or temp_x_ind < 0 \
                            or temp_x_ind >= self.params["limits_ind"][0] \
                            or self.data_occ[self.ind2d_to_coord(
                                (temp_x_ind, temp_y_ind),self.params)] == 1:
                        A[ind, ind] = A[ind, ind] + gauss_mask[i, j]
                        continue

                    temp_ind = temp_y_ind * self.params["limits_ind"][
                        0] + temp_x_ind

                    A[ind, temp_ind] += gauss_mask[i, j]
        self.sparse_A = csr_matrix(A.T)
        # self.sparse_A = A.T


    def hmm_single_step(self):

        # data input loop
        if self.dataQueue.qsize() > 0:
            data = self.dataQueue.get()

            # if ending
            if data == "EoF":
                self.log("with " + str(self.count) + " data points.")

                ferror = open(self.params['error_output_file'], 'a+')
                for i in range(len(self.best_estimates)):
                    ferror.write(
                        str([ self.times[i],
                              list(self.best_estimates[i]),
                              self.error[i],
                              self.mult_times[i]]) + "\n")
                ferror.close()
                return "EoF"

            # get new data
            time_real = data[0]
            time_stamp = time.time()
            dongle_mac = data[2]
            beacon_mac = data[3]
            rssi = data[4]
            self.ground = data[1][0:2]
            print(dongle_mac, beacon_mac, rssi)

            if dongle_mac not in self.rssi_window.keys():
                self.rssi_window[dongle_mac] = {}
                self.time_window[dongle_mac] = {}
            if beacon_mac not in self.rssi_window[dongle_mac].keys():
                self.rssi_window[dongle_mac][beacon_mac] = []
                self.time_window[dongle_mac][beacon_mac] = []
            self.rssi_window[dongle_mac][beacon_mac].append(rssi)
            self.time_window[dongle_mac][beacon_mac].append(time_real)

            while self.time_window[dongle_mac][beacon_mac][-1] - self.time_window[dongle_mac][beacon_mac][0] > self.time_window_size:
                self.time_window[dongle_mac][beacon_mac].pop(0)
                self.rssi_window[dongle_mac][beacon_mac].pop(0)
            mxRssi = max(self.rssi_window[dongle_mac][beacon_mac])


            # data prepared

            # PREDICT - Diffuse
            self.hmm_predict()

            # UPDATE - Rectify and NORMALIZE
            self.hmm_update(dongle_mac, beacon_mac, mxRssi)

            # SEND TO GUI
            # print(self.alpha.T)
            index = int(np.argmax(self.alpha))
            print(max(self.alpha))
            self.best_cell_coord = self.ind_to_coord(index,self.params)
            self.best_estimates.append(self.best_cell_coord)
            print(index, self.best_cell_coord)
            # if index == 0:
            #     print("Bu Mu?")
            #     self.exit()
            # O-5.0
            #
            # self.best_cell_coord = (0,0)
            self.err = dist_euclid(self.ground, self.best_cell_coord)
            if self.acc_err == 0.0:
                self.acc_err = self.err
                self.accumulation = 1
            else:
                self.acc_err = (self.acc_err * self.accumulation + self.err) / (self.accumulation + 1)
                self.accumulation += 1

            self.times.append(time_stamp)
            self.times_real.append(time_real)
            self.error.append(self.err)
            self.mult_times.append(self.time_cur)
            self.log(('{:03d}'.format(self.count),
                  "Diff:",'{:.3f}'.format(round(self.params['diffusion'], 3)),
                  "Err:",'{:.3f}'.format(round(self.err,3)),
                  "Time:",'{:.6f}'.format(round(self.time_cur,6))
                      ))

            self.count += 1

    def hmm_predict(self):
        # stable computation
        # print(self.logAlpha.T)
        # mx = max(self.logAlpha)
        # p = np.exp(self.logAlpha - mx)
        # self.logAlphaPredict = np.log(self.A.T @ p) + mx
        st = time.time()
        self.alphaPredict = self.sparse_A @ self.alpha
        et = time.time()
        self.time_cur = et - st
        # print(np.exp(self.logAlphaPredict).round(3))

    def hmm_update(self, dongle, beacon, rssi):
        for i in range(self.N):

            # if beacon not in self.data_grid[i].keys():
            #     # print i, beacon
            #     continue

            coord = self.ind_to_coord(i, self.params)
            # do the update
            self.alpha[i,0] = \
                self.data_grid[coord][dongle][beacon][rssi - self.rssi_start] \
             * self.alphaPredict[i,0]

        # self.mx = max(self.logAlpha)
        # self.alpha = np.exp(self.logAlpha)
        # reinitialize in need
        if sum(self.alpha) == 0.0:
            self.alpha = np.ones((self.N,1)) * 1.0/self.N
        else:
            self.alpha = self.alpha / sum(self.alpha)

    def read_config_file(self, config_file = None):
        if not config_file == None:
            with open(config_file, 'r') as f:
                config = json.load(f)
            for key in config.keys():
                self.params[key] = config[key]
            self.log("Config file loaded: %s" % (config_file))

    def read_grid_dir(self):
        self.data_grid, params_grid = parse_grids_dir_multi(
            self.params["grddir"],
            default_pattern_multi_data_grid)
        for key in params_grid.keys():
            self.params[key] = params_grid[key]
        self.log("Grids loaded: %s" % (self.params["grddir"]))

    def read_occupancy(self):
        self.data_occ = {}
        self.data_occ, params_occ = parse_occupancy(
            self.params["occ"], self.data_occ)
        self.log("Occupancy loaded: %s" % (self.params["occ"]))

    def log(self, log_string):
        if self.logQueue:
            self.logQueue.put(self.name + ": "+ str(log_string))
        else:
            print(self.name + ": " + str(log_string))

    def exit(self):
        if self.simQueue:
            self.simQueue.put(('Q', None))
        if self.guiQueue:
            self.guiQueue.put(('Q', None))
        # time.sleep(2)
        sys.exit()

def main():
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        if len(sys.argv) > 2:
            config_gui = sys.argv[2]
    else:
        config_file = None
        print("HMM Exact Filter: Not enough parameters.")
        sys.exit()

    simQueue = Queue()
    dataQueue = Queue()
    guiQueue = Queue()

    hmmThread = btExact_multi(
        "ParticleFilterThread",
        simQueue,
        dataQueue,
        config_file,
        guiQueue = guiQueue
    )
    simThread = SimulationFileThread("SimulationThread",
                                     simQueue,
                                     dataQueue,
                                     realTime=False,
                                     dataBuffer=5)
    simThread.start()
    hmmThread.start()
    # if hmmThread.params['size_visuals'] > 0:
    #     app = btHmm_viewer("HMM Exact Viewer", config_gui, guiQueue)
    #     app.run()
    hmmThread.join()
    simThread.join()


if __name__ == '__main__':
    main()
