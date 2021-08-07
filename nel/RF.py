# -*- coding: cp437 -*-

import sys
import mysql.connector
import math
import locale
import datetime
import struct
import io
import os
import time
import RPi.GPIO as GPIO
from datetime import datetime
import serial
import thread
# from Barrier import Barrier
# import numpy as np

class RF:
    def __init__(self, LEDPin, Barriers, Gates, Readers):
        GPIO.setmode(GPIO.BCM)
        self.LEDPin = LEDPin
        self.Barriers = Barriers
        self.Gates = Gates
        self.Readers = Readers
        self.Guard = None
        self.Devices = None
        GPIO.setup(self.LEDPin, GPIO.OUT)

        self.SerialPort = serial.Serial(port='/dev/serial0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=.005)
        thread.start_new_thread( self.ServiceReceive, ( ) )

    def ProcessData(self, Origin, Data):
        GPIO.output(self.LEDPin, GPIO.HIGH)
        print('RF Data - Origin: ' + Origin + '\t Data: '+  Data.encode('utf-8'))

        

        DeviceIsReader = False
        Device = None

        for Reader in self.Readers:
            if Reader.Address == Origin:
                Device = {
                    "ID": Reader.ID,
                    "Name": Reader.Caption,
                    "Type": 'Reader',
                    "Address": Reader.Address
                }
                DeviceIsReader = True
                break

        if DeviceIsReader == False:

            conn = mysql.connector.connect(user='admin', password='InDo2011', host='localhost', database='ControladorFraccionamientos')
            cur = conn.cursor()
            query = ("SELECT `ID`, `Name`, `Type`, `Address` FROM `devices`;")
            cur.execute(query)
            self.RFDevices = cur.fetchall()

            for CurrentDevice in self.RFDevices:
                if CurrentDevice[3] == Origin:
                    Device = {
                        "ID": CurrentDevice[0],
                        "Name": CurrentDevice[1],
                        "Type": CurrentDevice[2],
                        "Address": CurrentDevice[3]
                    }
                    break

        if Device == None:
            print('Device not registered')
        else:
            
            if Device['Type'] == 'Reader':
                if len(self.Readers) > 0:
                    for Reader in self.Readers:
                        if Reader.Address == Device['Address']:
                            Reader.ProcessCard(Data)
            else:
                print('General device')
        GPIO.output(self.LEDPin, GPIO.LOW)
    
    def ProcessFrame(self, byteFrame):
        for x in range(len(byteFrame)):
            if byteFrame[x] == 126:
                strOriginAddress = ''
                strReceivedData = ''
                intFrameLen = int('0x' + str(hex(byteFrame[x+1]))[2:].zfill(2) + str(hex(byteFrame[x+2]))[2:].zfill(2),0)
                intDataLen = intFrameLen-12

                for i in range(8):
                    strOriginAddress += str(hex(byteFrame[x+4+i]))[2:].zfill(2).upper()

                for j in range(intDataLen):
                    strReceivedData += chr(byteFrame[x+15+j])
                
                self.ProcessData( strOriginAddress, strReceivedData)
                

                x = intFrameLen + 4


    def ServiceReceive(self):
        while True:
            state=self.SerialPort.readline()
            if state != '':
                arreglo = bytearray(state)
                # print(arreglo)
                thread.start_new_thread( self.ProcessFrame, ( arreglo, ) )