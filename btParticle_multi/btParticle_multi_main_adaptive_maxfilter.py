import sys, os, time, re
sys.path.append("..")

from lib.parsers import *
from lib.paths import *
from lib.simulationThread_multi import *
from btParticle_multi.btParticle_multi_gui import *
from queue import Queue
import json

# is_gui_enabled = True

SEC_SLEEP = 0.00001
# SEC_SLEEP = 1.0
GRD_PATTERN = '_'\
              r'([a-f0-9]{12})_'\
              r'([0-9]{,2}\.[0-9]{,3})\.grd'
TRK_PATTERN = r'(sensor[0-9]{2})_' \
              r'[0-9]{,2}\.[0-9]{,3}_' \
              r'[0-9]{,2}\.[0-9]{,3}_' \
              r'[0-9]{,2}\.[0-9]{,3}.mbd'

simQueue = Queue()
dataQueue = Queue()
guiQueue = Queue()

class btParticle_multi(threading.Thread):
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
        self.params_pf = {}
        self.simQueue = simControlQueue
        self.dataQueue = dataReadQueue
        self.logQueue = logQueue
        self.guiQueue = guiQueue
        self.config_file = config_file
        self.flagExit = False
        self.diffusion_sub_limit = None

        self.p_particles = None
        self.p_particles_hat = None
        self.d_particles = None
        self.d_particles_hat = None
        self.p_weights = None
        self.d_weights = None
        self.p_best_weights = None
        self.p_best_indexes = None
        self.d_best_weights = None
        self.d_best_indexes = None
        self.particles_to_send = None
        self.weights_to_send = None
        self.ground = None
        self.Neff = 0
        self.d_particle_weighted_mean = 0.1

        self.read_config_file(config_file)
        self.read_grid_dir()
        self.read_occupancy()
        self.rssi_window = {}
        self.time_window = {}
        self.time_window_size = None


    def pf_initialize(self):
        # ATTENTION: this is size_p per d
        self.size_p = self.params_pf["size_p"]
        self.size_d = self.params_pf["size_d"]
        self.sensitivity = self.params_pf["sensitivity"]
        self.size_total = self.size_p * self.size_d
        self.time_window_size = self.params_pf["sec_window"]


        # variable list
        # updated particles
        self.p_particles = [None] * self.size_total
        self.d_particles = [0.0] * self.size_d

        # predicted particles
        self.p_particles_hat = [None] * self.size_total
        self.d_particles_hat = [0.0] * self.size_d

        # weights
        self.p_weights = [0.0] * self.size_total
        self.p_best_weights = [0.0] * self.size_total

        self.d_weights =  [0.0] * self.size_d
        self.d_best_weights = [0.0] * self.size_d

        if self.params_pf['size_visuals'] > 0:
            self.particles_to_send = [0] * self.params_pf['size_visuals']
            self.weights_to_send = [0] * self.params_pf['size_visuals']
        else:
            self.log("GUI is disabled")

        self.log("Randomly initializing particles")
        for i in range(self.size_d):
            for j in range(self.size_p):
                ind_p = i * self.size_p + j
                self.p_particles[ind_p] = \
                        sampleRandomPoint2dUniform(self.params_pf['limits'])
                counter = 0
                # be sure that the particles are in the non-occupied area
                while not self.pf_check_limits(self.p_particles[ind_p]):
                    self.p_particles[ind_p] = \
                        sampleRandomPoint2dUniform(self.params_pf['limits'])
                    counter += 1
                if counter > 1000:
                    self.log("Too many resampling attempts!")

            for i in range(self.size_d):
                self.d_particles[i] = random.uniform(0.00001, 5.0)

    def read_config_file(self, config_file = None):
        if not config_file == None:
            with open(config_file, 'r') as f:
                config = json.load(f)
            for key in config.keys():
                self.params_pf[key] = config[key]
            self.log("Config file loaded: %s" % (config_file))

    def read_grid_dir(self):
        self.data_grid, params_grid = parse_grids_dir_multi(
            self.params_pf["grddir"],
            default_pattern_multi_data_grid)
        for key in params_grid.keys():
            self.params_pf[key] = params_grid[key]
        self.diffusion_sub_limit = self.params_pf['diffusion_limit']
        self.log("Grids loaded: %s" % (self.params_pf["grddir"]))

    def read_occupancy(self):
        self.data_occ, params_occ = parse_occupancy(self.params_pf["occ"],
                                                          self.data_occ)
        self.log("Occupancy loaded: %s" %(self.params_pf["occ"]))

    def run(self):
        # waiting for gui

        # send track file
        if "track_file" in self.params_pf.keys():
            self.simQueue.put(("F", self.params_pf["track_file"]))

        self.times = []
        self.times_real = []
        self.mean = []
        self.mean_d = []
        self.var = []
        self.error = []
        self.acc_err = 0.0
        self.err = 0
        self.count = 0
        self.burnin_complete = False

        # send wait amount
        if self.params_pf['size_visuals'] > 0:
            send_wait_seconds = 10
        else:
            send_wait_seconds = 0
        if self.simQueue:
            self.simQueue.put(('W', send_wait_seconds))
        # send the start signal
        if self.simQueue:
            self.simQueue.put(( 'S', None ))

        while True:
            retVal = self.pf_single_step()
            if retVal == "EoF":
                break
            time.sleep(SEC_SLEEP)

        self.exit()

    def pf_single_step(self):

        # data input loop
        if self.dataQueue.qsize() > 0:
            data = self.dataQueue.get()
            # print(data)

            if self.count == self.params_pf['size_burnin']:
                self.burnin_complete = True
                self.log("Burn-in period ended")

            # if ending
            if data == "EoF":
                if not self.burnin_complete:
                    # aveErr = sum(self.error) / len(self.error)
                    # self.log("Average Error = " + str(aveErr))
                    self.log("with " + str(self.count) + " data points.")
                    self.log("with burn-in at " + \
                          str(self.params_pf["size_burnin"]))
                else:
                    # aveErr = sum(self.error) / len(self.error)
                    # self.log("Average Error = " + str(aveErr))
                    self.log("with " + str(self.count) + " data points.")

                ferror = open(self.params_pf['error_output_file'], 'a+')
                for i in range(len(self.mean)):
                    ferror.write(
                        str([ self.times[i],
                              self.mean[i],
                              self.error[i],
                              self.mean_d[i]]) + "\n")
                ferror.close()
                return "EoF"

            # get new data
            time_real = data[0]
            time_stamp = time.time()
            dongle_mac = data[2]
            beacon_mac = data[3]
            rssi = data[4]
            self.ground = data[1][0:2]

            # O-0.0
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

            self.pf_importance_sampling_diffusion(dongle_mac, beacon_mac, mxRssi)
            self.pf_mean_point()
            if self.params_pf['size_visuals'] > 0:
                self.send_particles()

            # effective population size addition
            if self.params_pf["nthr"] < 1.0:
                # if there is a N_thr defined
                # calculate efficient particle size
                Neff = 0

                Neff = 1 / (self.p_weights ** 2).sum()
                if self.Neff < self.size_d *  \
                        self.size_p * \
                        self.params_pf["nthr"]:
                    self.pf_selectParticles()
                else:
                    self.p_particles = self.p_particles_hat.copy()
                    self.d_particles = self.d_particles_hat.copy()
            else:
                self.pf_selectParticles()

            # O-5.0
            self.err = dist_euclid(self.ground, self.p_particle_weighted_mean)

            if self.acc_err == 0.0:
                self.acc_err = self.err
                self.accumulation = 1
            else:
                self.acc_err = (self.acc_err * self.accumulation + self.err) / (self.accumulation + 1)
                self.accumulation += 1

            self.times.append(time_stamp)
            self.times_real.append(time_real)
            self.mean.append(list(self.p_particle_weighted_mean))
            self.mean_d.append(self.d_particle_weighted_mean)
            self.error.append(self.err)
            self.log(("Count:", '{:03d}'.format(self.count),
                      "Wdif:",'{:.3f}'.format(round(
                self.d_particle_weighted_mean,3)),
                      "Wpos:", '{:.3f}'.format(round(
                self.p_particle_weighted_mean[0], 3)), '{:.3f}'.format(round(
                self.p_particle_weighted_mean[1], 3)),
                      "Err:",'{:.3f}'.format(round(self.err,3))
                      ))
                          # self.confidence, self.br, self.ep))

            self.count += 1

        # initialize if the particles are empty
        if self.p_particles == None:
            if self.params_pf['size_visuals'] > 0:
                self.guiQueue.put(("S", self.params_pf["size_visuals"]))
            self.pf_initialize()


    def pf_importance_sampling_diffusion(self, sensor, beacon, rssi, offset = \
        None, sigma = None):
        # O-1.0
        # generate particles according to the model
        for i in range(self.size_d):
            for j in range(self.size_p):
                ind_p = i * self.size_p + j
                self.p_particles_hat[ind_p] = sampleRandomPoint2dNormal(
                    self.p_particles[ind_p],self.d_particles[i])

            # print(self.d_particles)
            self.d_particles_hat[i] = random.gammavariate(
                    self.d_particles[i] ** 2 / self.sensitivity + 1,
                    self.sensitivity/ self.d_particles[i])

            # self.d_particles_hat[i] = max(
            #     random.normalvariate(
            #         self.d_particles[i],
            #         self.params_pf['sensitivity']),
            #     self.diffusion_sub_limit)


        # evaluate the newly generated particles
        self.pf_evaluateParticles(sensor, beacon, rssi)
        self.pf_sort_select_normalize_weights()


    def pf_evaluateParticles(self, sensor, beacon, rssi):
        # O-1.1
        self.weights_sum = 0
        for i in range(self.size_d):
            d_weight_sum = 0
            for j in range(self.size_p):
                ind_p = i * self.size_p + j
                if self.pf_check_limits(self.p_particles_hat[ind_p]):
                    self.p_weights[ind_p] = self.pf_likelihood(
                        self.p_particles_hat[ind_p], sensor, beacon, rssi)
                else:
                    self.p_weights[ind_p] = 0
                d_weight_sum += self.p_weights[ind_p]
            self.d_weights[i] = d_weight_sum
            self.weights_sum += d_weight_sum
        # print(self.p_weights)
        # print(self.d_weights)

    def pf_check_limits(self, point):
        # O-1.2
        # with occupancy map, we assume that there is an occupied frame
        # around the map
        point_grd = (
            round(round(point[0] / self.params_pf["size_grid"]) *
                  self.params_pf["size_grid"], 1),
            round(round(point[1] / self.params_pf["size_grid"]) *
                  self.params_pf["size_grid"], 1)
        )
        if point_grd not in self.data_occ.keys() or \
                self.data_occ[point_grd]:
            return False

        return True

    def pf_likelihood(self, point, sensor, beacon, value):
        # O-1.3
        # get the closest grid point
        x = round(int((point[0] + self.params_pf["size_grid"]/2)/self.params_pf[
            "size_grid"]) * self.params_pf["size_grid"],1)
        y = round(int((point[1] + self.params_pf["size_grid"]/2)/self.params_pf[
            "size_grid"]) * self.params_pf["size_grid"],1)

        binIndex = int(value-self.params_pf['bins'][0])

        return self.data_grid[(x,y)][sensor][beacon][binIndex]

    def pf_sort_select_normalize_weights(self):
        # O-1.4

        # if all weights are null, redistribute
        if self.weights_sum == 0:
            for i in range(self.size_d):
                for j in range(self.size_p):
                    ind_p = i * self.size_p + j
                    self.p_weights[ind_p] = 1.0/self.size_total
                self.d_weights[i] = 1.0/self.size_d
            # and don't continue
            return

        self.p_best_indexes = sorted(
                range(self.size_total),
                key=lambda x:self.p_weights[x],
                reverse=True)

        self.d_best_indexes = sorted(
                range(self.size_d),
                key=lambda  x: self.d_weights[x],
                reverse=True)

        for i in range(self.size_total):
            self.p_best_weights[i] = self.p_weights[
                self.p_best_indexes[i]]

        # print(self.p_weights_sorted)
        for i in range(self.size_d):
            self.d_best_weights[i] = self.d_weights[
                self.d_best_indexes[i]]

        # normalize weights
        for i in range(self.size_d):
            for j in range(self.size_p):
                ind_p = i * self.size_p + j
                self.p_weights[ind_p] = \
                    self.p_weights[ind_p]/self.weights_sum
            self.d_weights[i] = self.d_weights[i]/self.weights_sum

        if self.params_pf['size_visuals'] > 0:
            assert(self.params_pf['size_visuals'] <= self.size_total)
            for i in range(self.params_pf['size_visuals']):
                self.particles_to_send[i] = self.p_particles[
                    self.p_best_indexes[i]]
                self.weights_to_send[i] = self.p_weights[
                    self.p_best_indexes[i]]

    def pf_mean_point(self):
        # O-2.0
        
        S0 = 0.0
        S1 = 0.0
        W = 0.0
        D = 0.0
        for i in range(self.size_d):
            for j in range(self.size_p):
                ind_p = i * self.size_p + j
            
                S0 += self.p_particles[ind_p][0] * self.p_weights[ind_p]
                S1 += self.p_particles[ind_p][1] * self.p_weights[ind_p]
                W += self.p_weights[ind_p]
            D += self.d_particles[i] * self.d_weights[i]

        # print(W)
        self.p_particle_weighted_mean = (S0/W, S1/W)
        self.d_particle_weighted_mean = D/W

    def pf_selectParticles(self):
        # O-4.0

        # multinomial
        # d_cumul = getCumulative(self.d_weights)
        # p_cumul = getCumulative(self.p_weights)
        #
        # d_indexes = randgen(d_cumul, self.size_d)
        # for i in range(self.params_pf["size_d"]):
        #     self.d_particles[i] = self.d_particles_hat[d_indexes[i]]
        #
        # p_indexes = randgen(p_cumul, self.size_p * self.size_d)
        # for i in range(self.size_p * self.size_d):
        #     self.p_particles[i] = self.p_particles_hat[p_indexes[i]]

        # systematic
        d_cumul = getCumulative(self.d_best_weights)
        p_cumul = getCumulative(self.p_best_weights)
        m = 0
        u0 = random.uniform(0, 1)
        for i in range(self.size_d):

            for j in range(self.size_p):
                ind_i = i * self.size_p + j
                u = (u0 + ind_i)/ (self.size_d *
                               self.size_p )
                # print(u, ' ', end='')
                while(p_cumul[m] < u):
                    m += 1
                # print(m)
                try:
                    self.p_particles[ind_i] = self.p_particles_hat[
                        self.p_best_indexes[m]]
                except TypeError:
                    print(self.p_weights)
                    print(self.p_best_weights)
                    print(self.p_best_indexes)
                    self.p_particles[ind_i] = self.p_particles_hat[
                        self.p_best_indexes[m]]

        m = 0
        u0 = random.uniform(0, 1)
        for i in range(self.size_d):
            u = (u0 + i) / self.size_d
            while(d_cumul[m] < u):
                m+=1
            self.d_particles[i] = self.d_particles_hat[
                self.d_best_indexes[m]]

    def print_particles(self):
        print(self.p_particles)
        print(self.p_weights)
        print("--------------------------------")

    def send_particles(self):
        # O-3.0

        if self.guiQueue:
            self.guiQueue.put(('P',
                               self.particles_to_send,
                               self.weights_to_send,
                               self.ground,
                               self.p_particle_weighted_mean,
                              'D: %d, P: %d, \u03bd: %s, k: %.3f, Err: %.3f' % (
                                  self.size_d,
                                  self.size_p,
                                  self.sensitivity,
                                  self.d_particle_weighted_mean,
                                  self.acc_err)
                              ))

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
        print("ParticleFilter: Not enough parameters.")
        sys.exit()

    pfThread = btParticle_multi(
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
    pfThread.start()
    if pfThread.params_pf['size_visuals'] > 0:
        app = btParticle_viewer("ParticleViewerWidget", config_gui, guiQueue)
        app.run()
    pfThread.join()
    simThread.join()


if __name__ == '__main__':
    main()
