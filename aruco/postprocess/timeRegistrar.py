import numpy as np
import sys
import os
import json

POSPATTERN = "b15_k0.501_s15_a10_o5"
POSDIR = "/home/serhan/workspace/btlocalization/python3/aruco/data/test02" \
         "/trajectory/"
MBDDIR = "/home/serhan/workspace/btlocalization/python3/aruco/data/test02/mbd" \
         "/clipped/"
OUTDIR = "/home/serhan/workspace/btlocalization/python3/aruco/data/test02" \
         "/registered/"

# get the experiment name

def parse_pose_file(filePath):
    # print(filePath)
    pose_data = []
    with open(filePath, 'r') as fid:
        for line in fid:
            lineList = json.loads(line.strip())
            pose_data.append([lineList[0]] + lineList[1][0:12])
    return pose_data

def parse_mbd_file(filePath):
    rssi_data = []
    with open(filePath, 'r') as fid:
        for line in fid:
            lineList = line.strip().split(',')
            rssi_data.append([
                float(lineList[0]),
                lineList[1],
                lineList[2],
                int(lineList[3])
                ]
            )
    return rssi_data

def write_mbd_file(filePath, rssi_pose_data):
    with open(filePath, 'w+') as fid:
        for line in rssi_pose_data:
            for i in range(len(line)):
                if i == len(line) - 1:
                    end = "\n"
                else:
                    end = ','
                fid.write(str(line[i])+ end)

def main():
    if len(sys.argv) < 2:
        print("Usage:\n\
    %s <experiment>" % (sys.argv[0]))

    name_exp = sys.argv[1]

    # Check if pose file exist
    file_pose = name_exp + "_" + POSPATTERN + ".csv"
    if not file_pose in os.listdir(POSDIR):
        print("File not found: %s " % POSDIR + file_pose)
        return

    # Check if mbd directory is correct.
    if not name_exp in os.listdir(MBDDIR):
        print("Directory not found: %s" % MBDDIR + name_exp)
        return

    # Create a new directory if not existing
    if name_exp not in os.listdir(OUTDIR):
        os.mkdir(OUTDIR + name_exp)

    pose_data = parse_pose_file(POSDIR + file_pose)

    for file_MBD in os.listdir(MBDDIR + name_exp):
        # print(name_exp, file_MBD)
        rssi_pose_data = []
        # create a new file for each mbd
        # fid_out = open(OUTDIR + name_exp + "/" + file_MBD, "w+")
        rssi_data = parse_mbd_file(MBDDIR + name_exp + "/" + file_MBD)

        count_rssi = 0
        # count_pose = 0

        if rssi_data[0][0] < pose_data[0][0]:
            # this is the default behavior: if the rssi data comes first,
            # we map the first rssi data to the
            # first pose data
            rssi_pose_data.append(
                rssi_data[0] + pose_data[0][1:]
            )
            # count_pose += 1
            count_rssi += 1

        for count_pose in range(1, len(pose_data)):
            if pose_data[count_pose][0] - pose_data[count_pose-1][0] < 0:
                print("Houston, we have a problem!")
                break
            while rssi_data[count_rssi][0] < pose_data[count_pose][0]:
                if rssi_data[count_rssi][0] >= pose_data[count_pose-1][0] \
                        and \
                   pose_data[count_pose][0] >= rssi_data[count_rssi][0]:
                    # linear interpolation on the timestamp of rssi
                    dist_bck = rssi_data[count_rssi][0] - pose_data[
                        count_pose-1][0]
                    dist_fwd = pose_data[count_pose][0] - rssi_data[
                        count_rssi][0]
                    # inverse proportion
                    rssi_pose_data.append(rssi_data[count_rssi])
                    rssi_pose_data[-1] += \
                        np.round((np.array(pose_data[count_pose]) * dist_bck +
                         np.array(pose_data[count_pose-1]) * dist_fwd
                         )/(dist_fwd + dist_bck),9).tolist()[1:]
                else:
                    print("There is some big problem!")
                    return
                count_rssi += 1
                if count_rssi == len(rssi_data):
                    print("Passed the windmill!")
                    break


        write_mbd_file(OUTDIR + name_exp + "/" + file_MBD, rssi_pose_data)

if __name__ == '__main__':
    main()
