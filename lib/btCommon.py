import dbus
import sys
import signal
from ast import literal_eval
import socket
import time

threadWaitInterval = 0.000001

def getAdapters():

    BUS_NAME = 'org.bluez'
    ADAPTER_STRING = dbus.String('org.bluez.Adapter1')

    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object(BUS_NAME, '/'),
                             'org.freedesktop.DBus.ObjectManager')

    objects = manager.GetManagedObjects()
    adapters = {}

    for key in objects.keys():
        if ADAPTER_STRING in objects[key].keys():
            adapter = objects[key][ADAPTER_STRING]
        else:
            continue
        adapters[mac_to_str(adapter['Address'])] = str(adapter['Alias'])
    return adapters

def send_quit_to_log_thread(logQueue):
    logQueue.put("QUIT")

def send_quit_to_server_threads(writeQueue, scanQueues):
    writeQueue.put("QUIT")
    for adapter in scanQueues.keys():
        scanQueues[adapter].put([ "QUIT", None ])

def send_quit_to_client_threads(saveQueue, readQueues):
    saveQueue.put("QUIT")
    for thread in readQueues.values():
        thread.put("QUIT")

def flushQueue(threadQueue):
    while threadQueue.qsize() > 0:
        threadQueue.get()

def mac_to_str(bdaddr):
    return str(bdaddr).lower().replace(':','')

def str_to_mac(macStr):
    mac = macStr[0:2] + ':' + \
          macStr[2:4] + ':' + \
          macStr[4:6] + ':' + \
          macStr[6:8] + ':' + \
          macStr[8:10] + ':' + \
          macStr[10:12]
    return macStr.upper(mac)
