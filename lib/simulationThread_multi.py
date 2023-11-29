__author__ = 'serhan'
import threading
import time
import json
from .parsers import *

SEC_SLEEP = 0.00001

class SimulationFileThread (threading.Thread):
    def __init__(self,
                 threadName,
                 inQueue,
                 outQueue,
                 logQueue = None,
                 realTime = True,
                 dataBuffer = 10):

        threading.Thread.__init__(self)
        self.name = threadName
        self.inQueue = inQueue
        self.outQueue = outQueue # the queue to put sample data
        self.dataFile = None
        self.data_track = None
        self.running = False
        self.lQueue = logQueue
        self.rtp = realTime
        self.timeStart = None
        self.timeDiff = None
        self.dataBuffer = dataBuffer
        self.init_wait_sec = 0

    def log(self, log_string):
        if self.lQueue:
            self.lQueue.put(self.name + ": "+ log_string)
        else:
            print(self.name + ": " + log_string)

    def readTrackFile(self):
        self.data_track = []
        self.data_track = parse_track_file(self.dataFile, self.data_track)

    def run(self):
        self.log("Starting.")
        counter = None
        time_stamp = None

        while(True):
            # receive message
            if self.inQueue.qsize() > 0:
                message = self.inQueue.get()
                self.log("Message Recieved: " + str(message))
                # Quit, End, File, Start
                if message[0] == "Q":
                    self.log("Quitting")
                    self.running = False
                    break
                if message[0] == "W":
                    self.init_wait_sec = message[1]
                    self.log("Waiting duration %s received" % self.init_wait_sec)
                if message[0] == "E":
                    self.log("Stopping")
                    self.running = False
                if message[0] == "F":
                    self.dataFile = message[1]
                    self.log("Loading file " + self.dataFile)
                    self.readTrackFile()
                    self.running = False
                if message[0] == "S":
                    if self.data_track == None:
                        self.log("Data not loaded")
                        continue
                    self.log("Waiting for %s seconds." % self.init_wait_sec)
                    time.sleep(self.init_wait_sec)
                    self.timeStart = time.time()
                    self.log("Starting simulation")
                    self.running = True
                    counter = 0

            # if not started pass all
            if not self.running:
                time.sleep(SEC_SLEEP)
                continue

            # if trying to work in real time
            if self.rtp:
                # get a time_stamp
                time_stamp = self.data_track[counter][0]

                # get the current time
                curTime = time.time()

                if not self.timeStart == None:
                    # set time difference
                    self.timeDiff = curTime - self.timeStart

                if curTime > self.timeDiff + time_stamp:
                    self.outQueue.put(self.data_track[counter])
                    if not counter+1 == len(self.data_track):
                        counter += 1
                    else:
                        break
                time.sleep(SEC_SLEEP)
            else:
                if not self.dataBuffer == None:
                    if self.outQueue.qsize() < self.dataBuffer:
                        self.outQueue.put(self.data_track[counter])
                        if counter < len(self.data_track):
                            counter += 1
                        else:
                            break
                else:
                    self.outQueue.put(self.data_track[counter])

            if counter >= len(self.data_track):
                self.outQueue.put("EoF")
                self.log("End of track file")
                self.running = False
                counter = 0
                # continue

        self.log("Ending")
