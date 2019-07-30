import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import numpy as np
import time
from datetime import datetime
import threading

import socket
socket.setdefaulttimeout(5)

fig=plt.figure()
plt.ylim('No','Yes')
plt.xlim([0,19])
value=[]
label=[]
count=-10
on_bed= 0
timer=0
bed="73,65,173,135"


def setup_mqtt():
    client=mqtt.Client("RF_ID_over_time")
    client.on_connect=OnConnect
    client.on_message=OnMessage
    client.connect("192.168.4.1",1883,120)
    return client

def OnConnect(client,userdata,flags,rc):
    client.subscribe("sensors/RFID/raw")
    
        
    
def OnMessage(client,userdata,msg):
    global on_bed
    global timer
    if msg.topic =="sensors/RFID/raw":
        if msg.payload.decode() == bed:
            on_bed = 1
            timer=0
        else:
            on_bed = 0
            timer=0
            
            
def animate(i):
    global value
    global label
    plt.clf()
    plt.ylim('No','Yes')
    plt.xlim([0,19])
    plt.bar(label,value)
        

def assign_value():
    global on_bed
    global count
    global value
    global label
    
    threading.Timer(10.0,assign_value).start()
    value.append(on_bed)
    count +=10
    label.append(str(count))
    print(value)
    print(label)
    
    
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
    global value
    global label
    while True:
        if count>=190:
            count=0
            value.clear()
            label.clear()
            value.append(0)
            label.append("0")
            ani= animation.FuncAnimation(fig, animate, frames=18, interval=10000,repeat=False)

def msg_checking():
    global on_bed
    global timer
    while True:
        timer +=1
        if timer >=3:
            on_bed=0
            timer =0
        time.sleep(1)


aniCheck = threading.Thread(target=aniChecking,daemon=True)
aniCheck.start()

msgCheck = threading.Thread(target=msg_checking,daemon=True)
msgCheck.start()

ani= animation.FuncAnimation(fig, animate, frames=18, interval=10000,repeat=False)
plt.show()

