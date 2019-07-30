import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import numpy as np
import time
from datetime import datetime
import threading

import socket
socket.setdefaulttimeout(3)


fig=plt.figure()
plt.ylim('NO','YES')
temp_value=0
value=0
previous=0
differences=0


def setup_mqtt():
    client=mqtt.Client("graph")
    client.on_connect=OnConnect
    client.on_message=OnMessage
    client.connect("192.168.4.1",1883,120)
    return client

def OnConnect(client,userdata,flags,rc):
    client.subscribe("sensors/proximity/count")
    
        
    
def OnMessage(client,userdata,msg):
    global temp_value
    if msg.topic =="sensors/proximity/count":
        temp_value=(int(msg.payload.decode()))
    
def animate(i):
    global value
    plt.clf()
    plt.ylim('NO','YES')
    plt.bar("are you moving around the bear",value)
        

def assign_value():
    global temp_value
    global previous
    global value

    while True:
        if temp_value != previous:
            print(1)
            value=1
        else:
            print(0)
            value=0
        previous=temp_value
        time.sleep(2)

while True:
    try:
        client = setup_mqtt()
        client.loop_start()
        print("mqtt connected")
        break
    except:
        print("Still waiting for mqtt connection")
        time.sleep(1)
        
assign_ = threading.Thread(target=assign_value,daemon=True)
assign_.start()


ani= animation.FuncAnimation(fig, animate,interval=500)
plt.show()


