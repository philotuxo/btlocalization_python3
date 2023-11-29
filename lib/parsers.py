import re
import os
import json
import numpy as np
from ast import literal_eval
from PyQt5 import QtCore

from lib.processing import *


default_pattern_single_data = r'.*_' \
                        r'([0-9]{1,3}\.[0-9]{1,3})-' \
                        r'([0-9]{1,3}\.[0-9]{1,3})-?' \
                        r'([0-9]{1,3}\.[0-9]{1,3})?\.sbd'
default_pattern_multi_data = r'.*_' \
                       r'([0-9]{1,3}\.[0-9]{1,3})_' \
                       r'([0-9]{1,3}\.[0-9]{1,3})_' \
                       r'([0-9]{1,3}\.[0-9]{1,3})\.mbd'
default_pattern_multi_data_grid = r'(.*)_' \
                           r'([0-9a-z]{12})_' \
                           r'([0-9]{1,3}\.[0-9]{1,3})\.grd' \


def parseDataDir_multi(directory, pattern, quiet = True):
    print("Parsing Dir:", directory)
    files = os.listdir(directory)
    dataValue = {}    # dongle-centric
    dataTime = {}
    for file in files:
        if re.match(pattern,file):
            dataValue, dataTime = parseDataFile_multi(
                os.path.join(directory, file), dataValue, dataTime, pattern, quiet)

    return dataValue, dataTime

def parseDataFile_single(dataFile, dataValue, dataTime, pattern):
    # old version, single dongle
    print("Parsing %s." % dataFile)

    # hour in range(0, 24) to seperate the data from a specific hour
    with open(dataFile, 'r') as f:
        searchObj = re.search(pattern, dataFile)
        if searchObj.lastindex == 3:
            point = (float(searchObj.group(1)),
                     float(searchObj.group(2)),
                     float(searchObj.group(3))
                    )

        if searchObj.lastindex == 2:
            point = (float(searchObj.group(1)),
                     float(searchObj.group(2))
                    )

        # readfile
        for line in f:
            each = line.split(',')
            timeStamp = float(each[0])
            mac = each[1].strip()
            rssi = int(each[3])

            if point not in dataValue.keys():
                dataValue[point] = {}
                dataTime[point] = {}

            if mac not in dataValue[point].keys():
                dataValue[point][mac] = []
                dataTime[point][mac] = []

            dataValue[point][mac].append(rssi)
            dataTime[point][mac].append(timeStamp)

        if f:
            print("Data file loaded "+ dataFile)
        else:
            print("Incompatible data file: " + dataFile)

    return dataValue, dataTime

def parseDataFile_multi(dataFile, dataValue, dataTime, pattern, quiet = False):
    # dataFile: path of the file to be parsed
    # pattern: pattern of the filename, for extracting the position info

    if not quiet:
        print("Parsing %s." % dataFile)

    # extract position from file name
    searchObj = re.search(pattern, dataFile)
    point = (float(searchObj.group(1)),
             float(searchObj.group(2)),
             float(searchObj.group(3))
             )

    with open(dataFile, 'r') as f:
        for line in f:
            spl = line.split(",")
            time = float(spl[0])
            dongle = spl[1].strip().lower().replace(":", "")
            beacon = spl[2].strip().lower().replace(":", "")
            rssi = int(spl[3].strip())
            if point not in dataValue.keys():
                dataValue[point] = {}
                dataTime[point] = {}
            if dongle not in dataValue[point].keys():
                dataValue[point][dongle] = {}
                dataTime[point][dongle] = {}
            if beacon not in dataValue[point][dongle].keys():
                dataValue[point][dongle][beacon] = []
                dataTime[point][dongle][beacon] = []
            dataValue[point][dongle][beacon].append(rssi)
            dataTime[point][dongle][beacon].append(time)

    return dataValue, dataTime

class btEncoder(json.JSONEncoder):
    def default(self, obj):
        # print(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(btEncoder, self).default(obj)

def write_hist_file(hist_file_name, dataHist, bins, beacons, dongles):

    with open(hist_file_name, 'w') as f:

        f.write("Bins:")
        json.dump(list(bins), f)
        f.write("\n")

        f.write("Dongles:")
        json.dump(dongles, f)
        f.write("\n")

        f.write("Beacons:")
        json.dump(beacons, f)
        f.write("\n")

        f.write("Fingerprints:")
        f.write("{ ")
        for key in dataHist.keys():
            json.dump(str(key), f)
            f.write(": ")
            json.dump(dataHist[key], f, cls=btEncoder)
            f.write(", ")
        f.seek(f.tell() - 2)
        # json.dump(dataHist, f, cls=btEncoder)
        f.write("}\n")

def parse_hist_single(hstFile):
    # returns a dictionary object with
    # points |
    #        -> mac |
    #                -> histogram

    dataHist = None
    bins = None
    beacons = None

    dataHist = {}
    with open(hstFile, 'r') as f:
        for line in f:
            lineArr = line.split(":", 1)
            if lineArr[0] == "Fingerprints":
                dataTemp = json.loads(lineArr[1])
                for pts in dataTemp.keys():
                    tuplePts = literal_eval(pts)
                    dataHist[tuplePts] = {}
                    for mac in dataTemp[pts]:
                        hist = dataTemp[pts][mac]
                        dataHist[tuplePts][mac] = hist

            elif lineArr[0] == "Bins":
                bins = json.loads(lineArr[1])
            elif lineArr[0] == "Beacons":
                beacons = json.loads(lineArr[1])
            else:
                print("Invalid file!")
                return None

    if not (dataHist and bins and beacons):
        print("Insufficient file!")
        return

    return dataHist, bins, beacons

def parse_log_regression_model(md_file):
    models = None
    with open(md_file, 'r') as f:
        unproc = f.read()
        models = literal_eval(unproc)
    if not models is None:
        return models

def parse_hist_multi(hstFile):
    # returns a dictionary object with
    # points |
    #        -> donglemac |
    #                 -> beaconmac |
    #                         -> histogram

    dataHist = {}
    beacons = {}
    dongles = {}
    bins = []
    with open(hstFile, 'r') as f:
        for line in f:
            lineArr = line.split(":",1)
            if lineArr[0] == "Fingerprints":
                data_temp = json.loads(lineArr[1])
                # print(data_temp)
                for pts in data_temp.keys():
                    tuplePts = literal_eval(pts)
                    dataHist[tuplePts] = {}
                    for macDev in data_temp[pts].keys():
                        dataHist[tuplePts][macDev] = {}
                        for macBea in data_temp[pts][macDev].keys():
                            hist = data_temp[pts][macDev][macBea]
                            dataHist[tuplePts][macDev][macBea] = hist

            elif lineArr[0] == "Bins":
                bins = json.loads(lineArr[1])
            elif lineArr[0] == "Beacons":
                beacons_temp = json.loads(lineArr[1])
                for mac in beacons_temp.keys():
                    beacons[mac] = [ beacons_temp[mac][0],
                                     beacons_temp[mac][1],
                                     beacons_temp[mac][2]
                                     ]
            elif lineArr[0] == "Dongles":
                dongles_temp = json.loads(lineArr[1])
                for mac in dongles_temp.keys():
                    dongles[mac] = [ dongles_temp[mac][0],
                                     dongles_temp[mac][1],
                                     dongles_temp[mac][2]
                                     ]
            else:
                print("Invalid file")
                return None

    return dataHist, bins, beacons, dongles

def parseDevices(devFile):
    # reads device position, color, alias
    beacons = {}
    dongles = {}

    with open(devFile, 'r') as f:

        for line in f:
            lineArr = line.split(":", 1)
            if lineArr[0] == "Beacons":
                beacons_temp = json.loads(lineArr[1])
                for mac in beacons_temp.keys():
                    beacons[mac] = [ beacons_temp[mac][0],
                                     beacons_temp[mac][1],
                                     beacons_temp[mac][2]
                                     ]
            elif lineArr[0] == "Dongles":
                dongles_temp = json.loads(lineArr[1])
                for mac in dongles_temp.keys():
                    dongles[mac] = [ dongles_temp[mac][0],
                                     dongles_temp[mac][1],
                                     dongles_temp[mac][2]
                                     ]
            else:
                print("Invalid file!")
                return None

    return beacons, dongles

def parseParameters(parFile, oldParams = None):
    with open(parFile, 'r') as f:
        params_temp = json.load(f)
        params_temp["origin"] = QtCore.QPoint(params_temp["origin"][0],
                                             params_temp["origin"][1])
        params_temp["direction"] =  (params_temp["direction"][0],
                                     params_temp["direction"][1],
                                     params_temp["direction"][2],
                                     params_temp["direction"][3])

        params_temp["limits"] = ((params_temp["limits"][0],
                                 params_temp["limits"][1]),
                                (params_temp["limits"][2],
                                 params_temp["limits"][3]))
        if type(oldParams) == dict:
            for key in oldParams.keys():
                if key not in params_temp.keys():
                    params_temp[key] = oldParams[key]
    return params_temp

def parse_grids_single(grid_file_name, data_grid):
    # format
    # [limits]::sizeGrid::bins
    # sensorBased = False
    # [gridIndices]::[dongle]::[beacon]::[histogram]\n
    # sensorBased = True
    # [positions]::gridIndex_x::gridIndex_y::"beacon"::[histogram]\n

    params_grid = {}
    # read header
    f = open(grid_file_name, 'r')
    line = f.readline().strip().split(':')

    params_grid['limits'] = json.loads(line[0])
    params_grid['size_grid'] = json.loads(line[1])
    # params_grid['bins'] = json.loads(line[2])
    # read others
    for line in f:
        splitLine = line.strip().split(':')
        point = tuple(json.loads(splitLine[0]))
        # point = (round(params_grid['limits'][0][0] + ind[0]
        #                * params_grid['size_grid'], 2),
        #          round(params_grid["limits"][0][1] + ind[1]
        #                * params_grid['size_grid'], 2)
        #          )

        # dongle = json.loads(splitLine[1])
        beacon = splitLine[3]
        hist = json.loads(splitLine[4])

        if point not in data_grid.keys():
            data_grid[point] = {}
        # if dongle not in data_grid[point].keys():
        #     data_grid[point][dongle] = {}
        assert(beacon not in data_grid[point].keys())
        data_grid[point][beacon] = hist

    return data_grid, params_grid

def parse_grids_dir_multi(grid_dir_name, pattern):
    data_grid = {}
    params_grid = {}
    files = os.listdir(grid_dir_name)
    for file in files:
        if re.match(pattern,file):
            data_grid, params_grid = parse_grids_multi(
                os.path.join(grid_dir_name, file), data_grid)

    return data_grid, params_grid

def parse_grids_multi(grid_file_name, data_grid):
    """
    * File name format
    <place_identifier>_<dongleMac>_<sizeGrid>.grd

    <place_identifier>: a definition for the place of collected data
    <doncleMac>: hexadecimal MAC address without semicolons
    <sizeGrid>: size of the grids (float)

    * Header:
    <dongleMac>::<limits>::<sizeGrid>::<bins>

    <doncleMac>: hexadecimal MAC address without semicolons
    <limits>: float rectangle corners with format [ [ <x_begin>, <y_begin> ], [<x_end>, <y_end>] ]
    <sizeGrid>: size of the grids (float)
    <bins>: ordered list of integers or floats

    * Each line:
    <position>::<gridIndex_x>::<gridIndex_y>::<beaconMac>::<histogram>

    <position>: 3D or 2D position of the grid center
    <gridIndex_x>: corresponding grid index in x axis
    <gridIndex_y>: corresponding grid index in y axis
    <beaconMac>: hexadecimal MAC address without semicolons
    <histogram>: list of floats with the same number of bins
    """

    # get the place identifier
    searchObj = re.search(
        default_pattern_multi_data_grid,
        os.path.basename(grid_file_name))
    base_name = searchObj.group(1)
    # read header
    f = open(grid_file_name, 'r')
    line = f.readline().strip().split('::')

    dongle = line[0]
    print(grid_file_name)
    print(line)
    params_grid = {'limits': json.loads(line[1]), 'size_grid': float(line[2]),
                  'bins': json.loads(line[3]), 'name': base_name}

    # read others
    for line in f:
        splitLine = line.strip().split('::')
        point = tuple(json.loads(splitLine[0]))
        beacon = str(splitLine[1])
        hist = json.loads(splitLine[2])

        if point not in data_grid.keys():
            data_grid[point] = {}
        if dongle not in data_grid[point].keys():
            data_grid[point][dongle] = {}
        # assert(beacon not in data_grid[point][dongle].keys())
        data_grid[point][dongle][beacon] = hist

    return data_grid, params_grid

def write_grid_file(grid_file_name_base, data_grid, params_grid, dongle):

    fName = grid_file_name_base + "_" + str(params_grid['size_grid']) + ".grd"
    fid = open(fName, 'w+')

    # write header
    header = dongle + "::" + \
             json.dumps(params_grid['limits']) + '::' + \
             json.dumps(params_grid['size_grid']) + '::' + \
             json.dumps(params_grid['bins'])

    fid.write(header + '\n')

    for pos in data_grid.keys():
        linePOS = json.dumps(pos)
        for beacon in data_grid[pos][dongle].keys():
            lineBEA = beacon
            lineDAT = json.dumps(data_grid[pos][dongle][beacon])
            line = linePOS + '::' + lineBEA + '::' + \
                   lineDAT + '\n'
            fid.write(line)

    fid.close()

def write_occupancy_file(occ_file_name, data_occ, params_grid):
    fid = open(occ_file_name, 'w+')

    # write header
    header = json.dumps(params_grid['limits']) + '::' + \
            json.dumps(params_grid['size_grid'])

    fid.write(header + '\n')

    # data_occ should be a dictionary with keys for positions and values for
    # listWidgetItems

    for pos in data_occ.keys():
        linePOS = json.dumps(pos)
        lineDAT = json.dumps(data_occ[pos])
        line = linePOS + '::' + lineDAT + '\n'
        fid.write(line)

def parse_occupancy(occupancy_file_name, data_occ):

    # read header
    f = open(occupancy_file_name, 'r')
    line = f.readline().strip().split('::')

    params_occ = {'limits': json.loads(line[0]), 'size_grid': float(line[1])}

    # read others
    for line in f:
        splitLine = line.strip().split('::')
        point = tuple(json.loads(splitLine[0]))
        occupancy = int(splitLine[1])

        data_occ[point] = occupancy

    return data_occ, params_occ

def parse_track_file(track_file_name, data_trk):
    f = open(track_file_name, 'r')
    for line in f:
        splitLine = line.strip().split(',')
        timeStamp = json.loads(splitLine[0].strip())
        dongle = splitLine[1].strip()
        beacon = splitLine[2].strip()
        rssi = json.loads(splitLine[3].strip())
        point_x = json.loads(splitLine[4].strip())
        point_y = json.loads(splitLine[5].strip())
        # theta = json.loads(splitLine[6].strip())

        data_trk.append([timeStamp, [point_x, point_y], dongle,
                     beacon, rssi])

    return data_trk

def write_track_file(track_file_name, data_track):
    fid = open(track_file_name, 'w+')
    for i in range(len(data_track)):
        line = str(data_track[i][0]) + ',' + \
               str(data_track[i][2]) + ',' + \
               str(data_track[i][3]) + ',' + \
               str(data_track[i][4]) + ',' + \
               str(data_track[i][1][0]) + ',' + \
               str(data_track[i][1][1]) + '\n'
        fid.write(line)
    fid.close()
