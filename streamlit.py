# -*- coding: utf-8 -*-

import numpy as np
import streamlit as st
from paho.mqtt import client as mqtt_client
import time
import threading
from queue import Queue
import json
import csv
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import plotly.express as px 
from streamlit.runtime.scriptrunner import add_script_run_ctx


som=''
status=''
res=[]


broker="test.mosquitto.org"
port = 1883
topic = "laulau/status"
topic2 = "laulau/data"
client_id ='laulau'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            pass
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client




########################  

def on_message(client, userdata, msg):     
    print('on_message', status)
    res = json.loads(msg.payload.decode()) #Retornar à lista
    st.experimental_set_query_params(my_saved_result=res)
    
    if 'data' not in st.session_state:
       st.session_state.data=res
       print('received')
    
    
def subscribing():
    client.subscribe(topic2)
    client.on_message = on_message
    print('subs')
    client.loop_forever()

def publishing(status):
    client.publish(topic,status)
    print('publ', status)

def main(status):
    print('main')
    sub=threading.Thread(target=subscribing)
    add_script_run_ctx(sub)
    pub=threading.Thread(target=publishing(status))
    add_script_run_ctx(pub)
   
    sub.start()
    pub.start()
    

def get_data(filename)-> pd.DataFrame:
    return pd.read_csv(os.path.join(os.getcwd(),filename))


  

#configuration of the page
st.set_page_config(layout="wide")
st.title('Lauras Sound Shananigans')
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
            st.session_state.status='1'
            print('status=1')

        client=connect_mqtt()
        print('Conected')
        main(st.session_state.status)

        with col2: 
            if st.button('Stop'):
                client=connect_mqtt()
                pub=threading.Thread(target=publishing('3'))

    

with col3: 
    if(nested_start):
        t = st.empty()
        times=[7,6,5,4,3,2,1]
        for seconds in times:
            t.markdown(str('Please wait '+ str(seconds)+' seconds'))
            time.sleep(1)
        c.caption('Save the File or start again.')
        l.caption('')
        with t:
            nested_show=st.button('Show Plot')
    
with col4:
    if st.button('Save File'):
        with open("teste.csv", "w") as f:
            write = csv.writer(f)
            write.writerows(st.session_state.data)
        st.caption('File Saved!')



if 'data' in st.session_state:
    st.line_chart(st.session_state.data)
   
