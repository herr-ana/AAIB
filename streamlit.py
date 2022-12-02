# -*- coding: utf-8 -*-

import numpy as np
import streamlit as st
from paho.mqtt import client as mqtt
import time
import threading
import json
import csv
import pandas as pd
import os
from streamlit.runtime.scriptrunner import add_script_run_ctx

som=''
status=''
res=[]

#broker="test.mosquitto.org"
broker='mqtt.eclipseprojects.io'
port = 1883
topicStatus = "aherr/status"
topicData = "aherr/data"
client_id ='aherr'


def MQTT_TH(client):
    def on_connect(client,userdata,flags, rc):
        print('Connected')
        client.subscribe(topicData)
    
    def on_message(client,userdata,msg):
        print('on_message')
        res = json.loads(msg.payload.decode()) #Retornar à lista
    
        if 'data' not in st.session_state:
            st.session_state.data=res
            print('Received data')

        if 'data' in st.session_state:
            st.session_state.data=res
            print('Updated data')

        if 'signal' not in st.session_state:
            st.session_state.signal=res[0:2]
            print('Received signal')
        
        if 'signal' in st.session_state:
            st.session_state.signal=res[0:2]
            print('Updated signal')

        if 'lib' not in st.session_state:
            st.session_state.lib=res[2]
            print('Received lib')
        
        if 'lib' in st.session_state:
            st.session_state.lib=res[2]
            print('Updated lib')

        if 'ps' not in st.session_state:
            st.session_state.ps=res[3:6]
            print('Received ps')

        if 'ps' in st.session_state:
            st.session_state.ps=res[3:6]
            print('Updated ps')


    print('Initializing MQTT')
    client.on_connect=on_connect
    client.on_message=on_message

    client.connect(broker,port)
    client.loop_forever()

if 'mqttThread' not in st.session_state:
    st.session_state.mqttClient=mqtt.Client()
    st.session_state.mqttThread=threading.Thread(target=MQTT_TH,args=[st.session_state.mqttClient])
    add_script_run_ctx(st.session_state.mqttThread)
    st.session_state.mqttThread.start()

def publishing(status):
    st.session_state.mqttClient.publish(topicStatus,status)
    print('publ', status)
    
def get_data(filename)-> pd.DataFrame:
    return pd.read_csv(os.path.join(os.getcwd(),filename))

def list2df(list):
    df=pd.DataFrame(list)
    df=pd.DataFrame.transpose(df)
    return df

#configuration of the page
st.set_page_config(layout="wide")
st.title('Laura\'s Sound & Cloud Project')
c=st.empty()
c.caption('Please press start to start recording.')

col1, col2, col3, col4 = st.columns([0.5,2,0.5,0.5])
placeholder = st.empty()
l=st.empty()

with col1:
    nested_start=st.button('Start')
    l=st.empty()
    if nested_start:
        c.caption('Please wait for the recording.')
        l.caption('Listening...')

        if 'status' not in st.session_state:
            st.session_state.status='start'
            print('start')

        st.session_state.mqttClient.publish(topicStatus,'start')
        print('Started')

        with col2: 
            if st.button('Stop'):
                st.session_state.mqttClient.publish(topicStatus,'stop')
                

with col3: 
    if(nested_start):
        t = st.empty()
        times=[7,6,5,4,3,2,1]
        for seconds in times:
            c.caption(str('Please wait '+ str(seconds)+' seconds'))
            time.sleep(1)
        c.caption('Save File or press Start again.')
        l.caption('')
        with t:
            nested_show=st.button('Show Plots')
    
with col4:
    if st.button('Save File'):
        fs=st.empty()
        with open("teste.csv", "w") as f:
            write = csv.writer(f)
            write.writerows(st.session_state.data)
        fs.caption('File Saved!')
        

col12, col22, col32 = st.columns([1,1,1])

with col12:
    if 'signal' in st.session_state:
        df_signal=list2df(st.session_state.signal)
        st.subheader('Sonogram')
        st.line_chart(df_signal.rename(columns={1:'index',0:'Signal'}).set_index('index'))
        

with col22:
    if 'ps' in st.session_state:
        df_ps=list2df(st.session_state.ps[0:2])
    
        freq=np.array(st.session_state.ps[0])
        ps=np.array(st.session_state.ps[1])
        idx=np.array(st.session_state.ps[2])

        freqq=freq[idx][6000:12000]
        pss=ps[idx][6000:12000]

        ps_df = pd.DataFrame(freqq, columns = ['freq'])
        ps_df['Power Spectrum']=pss.tolist()

        st.subheader('Power Spectrum')
        st.line_chart(ps_df.rename(columns={'freq':'index'}).set_index('index'))
        

with col32:
    if 'lib' in st.session_state:
        df_lib=list2df(st.session_state.lib)
        
        st.subheader('Crossing Zeros Rate')
        st.line_chart(df_lib.rename(columns={0:'Crossing Zeros Rate'})) 




