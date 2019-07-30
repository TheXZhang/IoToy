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
plt.ylim(0,6)
plt.xlim([0,19])
value=[]
label=[]
count=-10
temp_value=0
previous=0
differences=0


def setup_mqtt():
    client=mqtt.Client("proximity_over_time")
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
    global label
    global differences
    plt.clf()
    plt.ylim(0,6)
    plt.xlim([0,19])
    s="total motion detected in last 3 minutes :" + str(differences)
    plt.title(s, fontsize=15)
    plt.bar(label,value)
        

def assign_value():
    global temp_value
    global count
    global previous
    global differences
    global value
    global label

    threading.Timer(10.0,assign_value).start()
    local_temp=abs(temp_value-previous)
    if local_temp<20:
        value.append(temp_value-previous)
        differences += (temp_value-previous)
        print(value)
        count +=10
        label.append(str(count))
        print(label)
        previous=temp_value
    else:
        value.append(1)
        differences +=1
        print(value)
        count +=10
        label.append(str(count))
        print(label)
        previous=temp_value

while True:
    try:
        client = setup_mqtt()
        client.loop_start()
        print("mqtt connected")
        break
    except:
        print("Still waiting for mqtt connection")
        time.sleep(1)
        
assign_value()

def aniChecking():
    global count
    global ani
    global differences
    global value
    global label
    while True:
        if count>=190:
            count=0
            differences=0
            value.clear()
            label.clear()
            value.append(0)
            label.append("0")
            ani= animation.FuncAnimation(fig, animate, frames=18, interval=10000,repeat=False)
            

aniCheck = threading.Thread(target=aniChecking,daemon=True)
aniCheck.start()

time.sleep(5)
ani= animation.FuncAnimation(fig, animate, frames=18, interval=10000,repeat=False)
plt.show()

