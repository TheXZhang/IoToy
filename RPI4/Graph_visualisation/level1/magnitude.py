import numpy as np
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time

import socket
socket.setdefaulttimeout(3)

temp="0"
temp_value=0
fig=plt.figure()
plt.ylim(0,1)



def setup_mqtt():
	client=mqtt.Client("movement_level1")
	client.on_connect=OnConnect
	client.on_message=OnMessage
	client.connect("192.168.4.1",1883,10)
	return client

def OnConnect(client,userdata,flags,rc):
	client.subscribe("sensors/accelerometer/magnitude")
	
		
	
def OnMessage(client,userdata,msg):
    global temp
    
    if msg.topic =="sensors/accelerometer/magnitude":
        temp=msg.payload.decode()
        
def assign_value():
    global temp_value
    global temp
    while True:
        if float(temp)>0.43:
            temp_value=1
        else:
            temp_value=0
        time.sleep(1)        
        
        
def animate(i):
    global value
    global label
    global temp_value
    plt.clf()
    plt.ylim('No','Yes')
    print(temp_value)
    plt.bar(['is there a movement'],temp_value)
    
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

