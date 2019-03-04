#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  appDhtWebServer.py
#  
#  

'''
	RPi Web Server for DHT captured data  
'''


import RPi.GPIO as GPIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)
import os
import pandas as pd


#Set up front-end GPIO connectivity
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
led = 13
ledSts = 0
relayPin = 17
GPIO.setup(relayPin, GPIO.OUT) 

GPIO.setup(led, GPIO.OUT) 
#Turn on LED, indicate that humifier on auto control  
GPIO.output(led, GPIO.HIGH)
global autoControl
autoControl = True

global manSwitch
manSwitch = 27
manSwitchSts = int(0) 
GPIO.setup(manSwitch, GPIO.OUT) 




def getData():
    global filename
    global df
    df = pd.read_csv('HumTempData_ShortTerm.csv')
    time = df.iloc[df.shape[0]-1]["Time"]
    temp = df.iloc[df.shape[0]-1]["Temperature"]
    hum = df.iloc[df.shape[0]-1]["Humidity"]
    return time, temp, hum

def getDF():
    df = pd.read_csv('HumTempData_ShortTerm.csv')
    return(df)

def getLastData():
    global filename
    global df
    df = getDF()
    time = df.iloc[df.shape[0]-1]["Time"]
    temp = df.iloc[df.shape[0]-1]["Temperature"]
    hum = df.iloc[df.shape[0]-1]["Humidity"]
    return time, temp, hum

global numSamples
numSamples = getDF().shape[0]

#if (numSamples > 101):
#numSamples = 100


# main route 
@app.route("/")
def index():
    relayPin = 17
    relaySts = GPIO.input(relayPin)
    time, temp, hum = getLastData()
    ledSts = GPIO.input(led)
    if ledSts == 1:
        controlSts = "SET TO AUTOMATIC"
    else:
        controlSts = "SET TO MANUAL"
    if relaySts == 1:
        HumSts = "OFF"
    else:
        HumSts = "ON"
    templateData = {
	  'time'	: time,
      'temp'	: temp,
      'hum'		: hum,
      'numSamples'	: numSamples,
      'led'  : ledSts,
      'controlSts' : controlSts, 
      'HumSts' : HumSts, 

	}
    return render_template('index.html', **templateData)


@app.route("/info")
def info():
    return render_template('info.html')

@app.route('/return-files/')
def return_files_tut():
	try:
		return send_file('HumTempData_LongTerm.csv', attachment_filename='HumTempData_LongTerm.csv')
	except Exception as e:
		return str(e)

@app.route('/delete-files/')
def deleteFiles():
    try:
        os.remove("HumTempData_LongTerm.csv")
        colString = "Time,Humidity,Temperature,HumidifierPower"
        with open('HumTempData_LongTerm.csv', 'w') as s:
            s.write(colString)
        return ("All data deleted. Click back to return to webpage.")
    except Exception as e:
        return str(e)
###


@app.route('/plot/temp')
def plot_temp():
    #times, temps, hums = getHistData(numSamples)
    ys = getDF()['Temperature']
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperature [C]".encode('utf8'))
    axis.set_xlabel("Samples")
    axis.grid(True)
    axis.set_ylim(0,40)
    #xs = range(numSamples)
    axis.plot(ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/hum')
def plot_hum():
    ys = getDF()['Humidity']
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Humidity [%]".encode('utf8'))
    axis.set_xlabel("Samples")
    axis.grid(True)
    axis.axhline(y=80, color='r', linestyle='--', lw=2)
    axis.set_ylim(0,100)

    #try this:
    #xs = range(numSamples)
    axis.plot(ys)   #this appears to be the issue!
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
   
    
    
    if deviceName == 'led':
        actuator = led
    if deviceName == 'manSwitch':  
        actuator = manSwitch
    if action == "on":
        GPIO.output(actuator, GPIO.HIGH)
    if action == "off":
        GPIO.output(actuator, GPIO.LOW)
    ledSts = GPIO.input(led)
    if ledSts == 1:
        controlSts = "SET TO AUTOMATIC"
    else:
        controlSts = "SET TO MANUAL"
    ledSts = GPIO.input(manSwitch)
    manSwitchSts = GPIO.input(manSwitch)
        #if relaySts == 1:
    #    HumSts = "OFF"
    #else:
   #     HumSts = "ON"
    relayPin = 17
    relaySts = GPIO.input(relayPin)
    time, temp, hum = getLastData()
    if relaySts == 1:
        HumSts = "ON"
    else:
        HumSts = "OFF"
    
    
    templateData = {
            'led'  : ledSts,
            'controlSts' : controlSts,
             'manSwitchSts' : manSwitchSts,
          	  'time'	: time,
                'temp'	: temp,
                'hum'		: hum,
                'HumSts' : HumSts
    }
    return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

