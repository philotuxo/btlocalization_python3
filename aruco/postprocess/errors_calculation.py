import json
import os
import numpy as np
import matplotlib.pyplot as plt

FONTSIZE_TICKS = 16
FONTSIZE_LABELS = 24

boxprops = dict(linewidth=3)
medianprops = dict(linewidth=3)
meanlineprops = dict(linestyle='--', linewidth=3)
whiskerprops = dict(linewidth=2)
capprops = dict(linewidth=2)

def parseSegmentsFile(fileName_segment):

    segment = {}
    with open(fileName_segment, "r+") as fid:
        for line in fid:
            lineSeg = json.loads(line.strip())
            segment[(lineSeg[0][0], lineSeg[1][0])] = [ lineSeg[0][1:], lineSeg[1][1:] ]

    return segment

def readSegmentsDir(dirName_segment):
    segments = {}
    files = os.listdir(dirName_segment)
    for file in files:
        expName = file.replace("_segment.txt","")
        segments[expName] = parseSegmentsFile(dirName_segment + file)
    return segments

def distanceNormal(segments, timeStamp, coords2D, segment_end = None):
    dist = None
    # check if the point is in the segment
    for terminals in segments.keys():
        if timeStamp < terminals[0] or timeStamp > terminals[1]:
            # do nothing
            continue
        p_measure = np.array(coords2D)
        p_start = np.array(segments[terminals][0])
        p_end = np.array(segments[terminals][1])


        dist = np.linalg.norm(
            np.cross(p_end - p_start, p_start - p_measure)) / \
            np.linalg.norm(p_end - p_start)
        if segment_end:
            segment_length = np.linalg.norm(p_end - p_start)
            vector_length = np.linalg.norm(p_measure - p_end)
            error_coeff = vector_length / segment_length
            dist += segment_end[terminals] * error_coeff/5

    return dist

def compute_errors_segment(allSegments, filePath, expName):
    segment_end_points = {}
    latest_timeStamp = None
    batch = []
    endPoint = {}
    with open(filePath, 'r') as fid:
        for line in fid:
            lineData = json.loads(line.strip())
            timeStamp = lineData[0]
            coords2D = lineData[1][0:2]

            if timeStamp == latest_timeStamp:
                batch.append(coords2D)
                continue
            else:
                latest_timeStamp = timeStamp
                if len(batch) > 0:
                    M = np.mean(batch, axis=0).tolist()
                    batch.clear()

                    for terminals in allSegments[expName].keys():
                        if timeStamp > terminals[0] and \
                                timeStamp < terminals[1]:
                            seg_x = allSegments[expName][terminals][1][0]
                            seg_y = allSegments[expName][terminals][1][1]
                            segment_end_points[terminals] = \
                                np.sqrt(
                                    (seg_x - M[0]) ** 2 + (seg_y - M[1]) ** 2
                                )
                            endPoint[terminals] = M
                batch.append(coords2D)
    # print(endPoint)
    return segment_end_points

def compute_errors_trajectory(allSegments, filePath, expName, seg_ends = None):
    distList = []
    latest_timeStamp = None
    batch = []

    with open(filePath, 'r') as fid:
        for line in fid:
            lineData = json.loads(line.strip())
            timeStamp = lineData[0]
            coords2D = lineData[1][0:2]
            if timeStamp == latest_timeStamp:
                batch.append(coords2D)
                continue
            else:
                latest_timeStamp = timeStamp
                if len(batch) > 0:
                    M = np.mean(batch, axis=0)
                    batch.clear()

                    dist = distanceNormal(allSegments[expName], timeStamp,
                                          M.tolist(), seg_ends)
                    if not dist == None:
                        distList.append(dist)
                batch.append(coords2D)

    # print(len(distList))
    return distList

def generateExperimentLabels(params):
    bLabel = ""
    fLabel = ""
    if params[0] == None:
        fLabel += "_kN"
    else:
        fLabel += "_k" + str(params[0])
        bLabel += "q: " + str(params[0]) + ""

    if params[1] == None:
        fLabel += "_sN"
    else:
        fLabel += "_s" + str(params[1])
        # bLabel += "C= " + str(params[1]) + ", "

    if params[2] == None:
        fLabel += "_oN"
    else:
        fLabel += "_o" + str(params[2])
        # bLabel += "U= " + str(params[2]) + ""

    if len(bLabel) == 0:
        bLabel = "Raw"
    bLabel = "$"+ bLabel +"$"

    return fLabel, bLabel

def main():
    trajDir = "/mnt/yedek/aruco_data/test02/trajectory/newExp/"
    exps = [  "duz_01", "duz_02","duz_03","duz_04","duz_05","kare_rotsuz",
              "kare_rotlu","zigzag_rotsuz","zigzag_rotlu" ]

    allSegments = readSegmentsDir("/mnt/yedek/aruco_data/test02/segments/"
    )

    paramss = [
        # [None, None, None],
        # [None, 20, None],
        # [None, 15, None],
        # [None, 5, None],
        # [None, 1, None],
        # [None, None, 20],
        # [None, None, 15],
        # [None, None, 5],
        # [None, None, 1],

        # [None, 15, 10],
        # [None, 15, 5],
        # [None, 15, 1],
        # [None, 20, 15],
        # [None, 20, 10],
        # [None, 20, 5],
        # [None, 20, 1],
        # [None, None, 5],

        [0.2, None, None],
        [0.01, 20, 10],
        [0.05, 20, 10],
        [0.1, 20, 10],
        [0.2, 20, 10],
        [0.5, 20, 10],
        [1.0, 20, 10],
        [2.0, 20, 10],
        [5.0, 20, 10],

        # remove penalty application

    ]
    errorss = []
    labels = []
    medians = []
    means = []
    for params in paramss:
        errors = []
        fLabel, bLabel = generateExperimentLabels(params)
        print(bLabel)
        for exp in exps:
            expFile = exp + fLabel + ".csv"
            if not os.path.isfile(trajDir + expFile):
                print(expFile, 'does not exist.')
                continue
            print(expFile)
            seg_end_err = None

            # penalty application
            seg_end_err = compute_errors_segment(
                allSegments, trajDir + expFile, exp)

            errors += compute_errors_trajectory(allSegments, trajDir +
                                                expFile, exp, seg_end_err)
        labels.append(bLabel)
        errorss.append(errors)
        medians.append(np.median(errors))
        means.append(np.mean(errors))

    for i in range(len(labels)):
        labels[i] = labels[i] + \
                    "\n" + str(round(means[i],3)) + \
                    "\n" + str(round(medians[i],3))

    fig = plt.figure(figsize=(15, 5))
    plt.boxplot(errorss,
                notch=True,
                showfliers=False,
                flierprops=dict(markerfacecolor='k', marker='o', alpha=.1),
                showmeans=True,
                meanline=True,
                labels=labels,
                whis=2.0,
                boxprops=boxprops,
                meanprops=meanlineprops,
                medianprops=medianprops,
                whiskerprops=boxprops,
                capprops=capprops
                )
    # plt.plot(medians)
    plt.xticks(weight='bold', fontsize = FONTSIZE_TICKS)
    #plt.text(0.45,-0.252,"Mean:\nMedian:",weight='bold',
             #horizontalalignment='right' )
    #plt.text(0.50,-0.135,"$q: $\nMedian:\nMean:",weight='bold',
             #horizontalalignment='right')
    plt.text(0.50,-0.24,"Mean:\nMedian:",weight='bold',
             horizontalalignment='right', fontsize = FONTSIZE_TICKS)
    plt.yticks(fontsize= FONTSIZE_TICKS)

    plt.ylabel("Error (m)", weight='bold', fontsize=FONTSIZE_LABELS)
    plt.ylim([-.05, 0.75])
    plt.grid(True)
    plt.xlabel("$C= " + str(20) + "$, $" + "U= " + str(10) + "$",
               fontsize = FONTSIZE_LABELS)
    plt.tight_layout()
    # plt.tick_params(width=2)
    # plt.xticks(range(len(labels)), labels)
    plt.show()

if __name__ == '__main__':
    main()
