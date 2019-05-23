#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# SCRIPT NOT IS USE RIGHT NOW
#  logHumidity.py
#
#  Sam Erickson, March 2019
#  
#  Capture data from a DHT22 sensor and save it


import time
import random
import pandas as pd
import os.path


###import Adafruit_DHT
###import RPi.GPIO as GPIO

###GPIO.setmode(GPIO.BCM)
#There are two ways to number RPi input output pins. This command indicates that we are using
# Broadcom System on a Chip numbering system

###GPIO.setwarnings(False)
# This system requires more than one script to run simultaneously on the RPi. This command
# Turns off warnings on startup if other pins are already doing things.

global humSetPoint
humSetPoint = 80 #relative humidity
global relay
relay = 17 #our relay will be plugged into 17
global controlSignal
controlSignal = 13 #this is a pin whose HIGH or LOW state shows whether we are in
# auto or manual mode
global manSwitch
manSwitch = 27

manSwitchSts = int(0) 
# This variable is purely for storing whether the relay 
# should be on or off. In a future version I want to find a better way to do this
# probably using mySQL.

global relaySts
relaySts = int(0)
#GPIO.setup(relay, GPIO.OUT)
#GPIO.output(relay, GPIO.LOW)
#GPIO.setup(manSwitch, GPIO.OUT)
#GPIO.output(manSwitch, GPIO.LOW)

#GPIO.setup(controlSignal, GPIO.OUT)
#GPIO.output(controlSignal, GPIO.HIGH)


sampleFreq = 2.5 # time in seconds
maxRows = 3600/2.5 # one hour of data



def checkAutoCtrl():
    if GPIO.input(controlSignal) == 0:
        return False
    else:
        return True
    
def getFAKEdata():
    #Purely for testing code without sensor input	
    hum,temp = (round(10+random.random()*10,1), round(2+random.random()*3,1))
    return(temp,hum)

def getDHTdata():
    DHT22Sensor = Adafruit_DHT.DHT22
    DHTpin = 4
    (hum,temp)=Adafruit_DHT.read_retry(DHT22Sensor, DHTpin)
    if (hum is None or temp is None):
        hum = None
        temp = None
    elif(hum < 100 and temp < 50 and hum > 0 and temp  >0):
        hum = round(hum)
        temp = round(temp, 1)   
    else:
        hum = None
        temp = None
    #else:
     #   hum = -1
      #  temp = -1
    return(temp,hum)


def recordData(temp,hum,relaySts):
    global df
    global numRows
    global maxRows
    t = time.asctime()
    if (relaySts == 0): 
        HumSts = 1
    else:
        HumSts = 0
    vals = {"Time":t,"Humidity":hum,"Temperature":temp,"HumidifierPower":HumSts}
    #df = df.append({"Time":time.asctime(),"Humidity":hum,"Temperature":temp}, ignore_index=True)
    dataLine = "\n"+str(t)+","+str(temp)+","+str(hum)+","+str(HumSts)
    with open('HumTempData_LongTerm.csv', 'a') as s:
        s.write(dataLine)
    if(numRows<maxRows):
        df_s = pd.read_csv('HumTempData_ShortTerm.csv')
        df_s = df_s.append(vals,ignore_index=True)
        df_s.to_csv('HumTempData_ShortTerm.csv',index=False)
        #with open('HumTempData_ShortTerm.csv', 'a') as s:
        #    s.write(dataLine)
        numRows = numRows+1
    else:
        df_s = pd.read_csv('HumTempData_ShortTerm.csv')
        df_s = df_s.iloc[1:]
        df_s = df_s.append(vals,ignore_index=True)
        df_s.to_csv('HumTempData_ShortTerm.csv',index=False)

def CheckControl(hum,humSetPoint):
    global relaySts
    global manSwitch
    if checkAutoCtrl():
        #WHEN AUTO CONTROL ON
        
        #SAM! Need to add what happens with None vals
        if(relaySts == 0):
            if hum > 80:
                GPIO.output(relay, GPIO.HIGH)
                relaySts = 1
        elif (relaySts == 1 and hum <= 80 and hum != None):
             GPIO.output(relay, GPIO.LOW)
             relaySts = 0
        else:
            pass
    else:
        #Manual Control
        manSwitchSts = bool(GPIO.input(manSwitch))
        if(relaySts == 0 and not manSwitchSts):
                GPIO.output(relay, GPIO.HIGH)
                relaySts = 1
        elif (relaySts == 1 and manSwitchSts):
             GPIO.output(relay, GPIO.LOW)
             relaySts = 0
        else:
            pass

def initialize():
    global numRows
    global relaySts
    numRows = 0
    temp, hum = getDHTdata()
    if hum <= 80:
        relaySts = 0
    else:
        relaySts = 1
    #colString = "Time,Humidity,Temperature"
    colString = "Time,Humidity,Temperature,HumidifierPower"
    with open('HumTempData_ShortTerm.csv', 'w') as s:
        s.write(colString)
    if not os.path.isfile('HumTempData_LongTerm.csv'): 
        with open('HumTempData_LongTerm.csv', 'w') as s:
            s.write(colString)


# main function
def main():
    global relaySts
    global relay
    global humSetPoint
    while True:
        temp, hum = getFAKEdata() #getDHTdata()
        #print("Temp: ",temp,"hum: ",hum)
        recordData(temp,hum,relaySts)
		#logData (temp, hum)
        CheckControl(hum,humSetPoint)
    time.sleep(sampleFreq)
        


# ------------ Execute program 
initialize()
main()

