# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 16:39:29 2022

@author: lauraherrera

Python code to receive input from MQTT to start recording and send over the 
calculated data.

"""
from paho.mqtt import client as mqtt_client
import sounddevice as sd
import threading
import time
import numpy as np
import json
import librosa 

status=''

broker='mqtt.eclipseprojects.io'
#broker="test.mosquitto.org"
port = 1883
topicStatus = "aherr/status"
topicData="aherr/data"
client_id = 'aherr'  


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
    print('Status received:', status) 
    
def recording():
    fs=2400 #Sample rate
    seconds = 5  # Duration of recording
    
    #Recording Data
    print('Recording...')
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
   
    #Calulations for Power Spectrum and Zero Crossing Rate
    t=np.arange(0,5,5/(fs*5))
    y=myrecording[:,0]
    ps=np.abs(np.fft.fft(y))**2
    time_step=5/(fs*5)
    freqs=np.fft.fftfreq(len(y),time_step)
    idx=np.argsort(freqs)
    lib=librosa.feature.zero_crossing_rate(y)

    #Encoding Data to send over MQTT 
    data=[y.tolist(),t.tolist(),lib.tolist(),freqs.tolist(),ps.tolist(),idx.tolist()]
    data_send=json.dumps(data)

    return data_send
    
  
def subscribing(): # subscribing since the beggining, waiting to receive status from mqtt
    
    client.subscribe(topicStatus)
    client.on_message = on_message
    client.loop_forever()
    

def publishing(): # publishing when 'start' is received from mqtt
     while (True):   
        time.sleep(1)
        if status=='start':
            data_send=recording()
            client.publish(topicData,data_send)
            client.publish(topicStatus,'stop')
            print('Publishing...')


    
client = connect_mqtt()

sub=threading.Thread(target=subscribing)
pub=threading.Thread(target=publishing)

sub.start()
pub.start()


if status=='stop': #stopping when 'stop' is received from mqtt
    sub.stop()
    pub.stop()
    
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  