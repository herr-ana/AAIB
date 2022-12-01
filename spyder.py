# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 16:39:29 2022

@author: lauraherrera

One Tap 
"""
from paho.mqtt import client as mqtt_client
import sounddevice as sd
from scipy.io.wavfile import write
import threading
import time
import matplotlib.pyplot as plt
import scipy as sc
from scipy.fft import *
import numpy as np

status=''

broker="test.mosquitto.org"
port = 1883
topicStatus = "laulau/status"
topicData="laulau/data"
client_id = 'laulau_status'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def on_message(client, userdata, msg):
    global status
    status=msg.payload.decode()
    print(status)
    
def recording():
    #fs = 44100  # Sample rate
    fs=2400
    seconds = 5  # Duration of recording
    
    print('Recording...')
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    
    yf=rfft(myrecording)
    freq=np.mean(abs(yf))
    Mfreq=10**3*freq
    sty=np.array2string(myrecording)
    
    global sound
    #sound=np.trunc(Mfreq)
    #sound=np.arange(0,10,0.1)
    
    sound=str(myrecording.tolist())
    
  
def subscribing(): # subscribing since the beggining, wait to receive the 1
    
    client.subscribe(topicStatus)
    client.on_message = on_message
    client.loop_forever()
    

def publishing(): # publishing when 1 is received from mqtt
     while (True):   
        time.sleep(1)
        if status=='1':
            recording()
            client.publish(topicData,sound)
            client.publish(topicStatus,'3')
            print('Publishing...')
            print(sound)
        #time.sleep(1)
    #client.loop_start()

    
client = connect_mqtt()

sub=threading.Thread(target=subscribing)
pub=threading.Thread(target=publishing)

### Start MAIN ###

sub.start()
pub.start()

#status=publishing()

if status=='3':
    sub.stop()
    pub.stop()
    
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  