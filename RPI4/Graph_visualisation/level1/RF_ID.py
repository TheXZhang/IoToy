import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import paho.mqtt.publish as pub
import time
import threading

import socket
socket.setdefaulttimeout(3)


on_bed = False
timer = 0
fig=plt.figure()
plt.ylim('Not on Bed','On Bed')
bed="73,65,173,135"

def setup_mqtt():
	client=mqtt.Client("RFIDProcessor")
	client.on_connect=OnConnect
	client.on_message=onMessage
	client.connect("192.168.4.1",1883,120)
	return client

def OnConnect(client,userdata,flags,rc):
    client.subscribe('sensors/RFID/raw')

def onMessage(client,userdata,msg):
    global timer
    global on_bed
    global bed
    if msg.topic =='sensors/RFID/raw':
        if msg.payload.decode() == bed:
            on_bed = True
            timer=0
        else:
            on_bed = False
            timer=0
        
def animate(i):
    global on_bed
    plt.clf()
    plt.ylim('Not on Bed','On Bed')
    if on_bed:
        print("on bed")
        plt.bar('is it on bed',1)
    else:
        plt.bar('is it on bed',0)

def msg_checking():
    global on_bed
    global timer
    while True:
        timer +=1
        if timer >=3:
            on_bed=False
            timer =0
        time.sleep(1)


while True:
    try:
        client = setup_mqtt()
        client.loop_start()
        print("mqtt connected")
        break
    except:
        print("Still waiting for mqtt connection")
        time.sleep(1)
        
check = threading.Thread(target=msg_checking,daemon=True)
check.start()


ani= animation.FuncAnimation(fig, animate,interval=500)
plt.show()



