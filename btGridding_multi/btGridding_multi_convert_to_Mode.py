import os, sys
sys.path.append("..")
from lib.parsers import *
from lib.paths import *
from lib.histograms import *
from lib.parsers import *
import scipy.signal as sgn
import json

class ModeExtractor(object):
    def __init__(self, config_file):
        self.data_grid = {}
        self.params_grid = {}
        self.config_file = config_file

        # parameters
        self.params = {"parity": None, "origin": None, "direction": None,
                       "limits": None, "points": [None, None]}

        self.readConfigFile(config_file)
        self.loadParameters()

        self.data_grid_maxed, self.params_grid_maxed = get_grid_mode(
            self.data_grid, self.params_grid)

        self.writeGrd()

    def log(self, logThis):
        print(logThis)
        return

    def loadParameters(self, parFile = None):
        if not parFile:
            return
        try:
            self.params = parseParameters(parFile, self.params)
            self.log("Parameters loaded: " + parFile)
        except:
            self.log("Incompatible File: " + parFile)

    def readGrd(self, grdFiles=None):
        if grdFiles:
            print("Preparing grids.")
            self.grids = True
            for grdFile in grdFiles:
                try:
                    self.data_grid, self.params_grid = \
                        parse_grids_multi(grdFile, self.data_grid)

                    self.log("File loaded: %s." % (grdFile))
                except AttributeError and IndexError:
                    self.log("Invalid grd file.")
                finally:
                    self.log("Grids imported from %s." % grdFile)

    def loadDevices(self, devFile = None):
        if not devFile:
            return
        try:
            self.beacons, self.dongles = parseDevices(devFile)
            self.log("Devices loaded: " + devFile)
        except:
            self.log("Incompatible File: " + devFile)

    def writeGrd(self):
        for dongle in self.dongles:
            file_name_base = self.params_grid['name'] + \
                             '_' + 'mode' + \
                             '_' + dongle

            write_grid_file(file_name_base,
                            self.data_grid_maxed,
                            self.params_grid_maxed,
                            dongle)

    def readConfigFile(self, configFile):
        with open(configFile, 'r') as f:
            config = json.load(f)
            if "par" in config.keys():
                self.loadParameters(
                    os.path.join(pathConf, config["par"]))
            if "dev" in config.keys():
                self.loadDevices(
                    os.path.join(pathConf, config["dev"]))
            if "grd" in config.keys():
                self.readGrd(config["grd"])

            self.log("Config file loaded: " + configFile)


def main():
    if len(sys.argv) > 1:
        configFile = sys.argv[1]
    else:
        configFile = None

    if configFile:
        p = ModeExtractor(configFile)
    else:
        print("No config given.")


if __name__ == '__main__':
    main()
