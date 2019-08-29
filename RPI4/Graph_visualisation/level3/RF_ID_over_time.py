import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import numpy as np
import time
from datetime import datetime
import threading

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(5)

fig=plt.figure()
plt.ylim('No','Yes')
plt.xlim([0,19])
y=[]
x=[]
count=-10
on_bed= 0
timer=0
bed="73,65,173,135"

#standard mqtt setup definition
def setup_mqtt():
    client=mqtt.Client("RF_ID_over_time")
    client.on_connect=OnConnect
    client.on_message=OnMessage
    client.connect("192.168.4.1",1883,120)
    return client

#standard mqtt onConnect definition
def OnConnect(client,userdata,flags,rc):
    client.subscribe("sensors/RFID/raw")


#standard mqtt onMessage definition
def OnMessage(client,userdata,msg):
    global on_bed
    global timer
    if msg.topic =="sensors/RFID/raw":
        #same as in level one, if message matches bed id , it is on bed otherwise its not
        if msg.payload.decode() == bed:
            on_bed = 1
            timer=0
        else:
            on_bed = 0
            timer=0


def animate(i):
    global y
    global x
    #its pretty much the same as all the other ones
    plt.clf()
    plt.ylim('No','Yes')
    plt.xlim([0,19])
    plt.bar(x,y)


def assign_value():
    global on_bed
    global count
    global y
    global x
    #again, starting a timer in another thread that run this def every 10s
    threading.Timer(10.0,assign_value).start()
    y.append(on_bed)
    count +=10
    x.append(str(count))


#this while loop is to check network and mqtt connections
while True:
    #if anything fails, it indicates you are not connceted to the required wifi
    try:
        client = setup_mqtt()
        client.loop_start()
        print("mqtt connected")
        #loop is executed until both passes and break out the loop
        break
    except:
        #if not conncetion, print message to indicate
        print("Still waiting for mqtt connection")
        #sleep for a second to allow reconncetion, should be fine without it but while loop runs too fast, it may cause error
    time.sleep(1)

assign_value()

#this is to check if we have reached 3 minutes,
#we reset the graph every 3 minutes, all variable associated to plotting is reset
def aniChecking():
    global count
    global ani
    global y
    global x
    while True:
        if count>=190:
            count=0
            y.clear()
            x.clear()
            y.append(0)
            x.append("0")

def msg_checking():
    global on_bed
    global timer
    while True:
        timer +=1
        if timer >=3:
            on_bed=0
            timer =0
        time.sleep(1)

#if mqtt is connected then we start the animation check thread and message checking thread

aniCheck = threading.Thread(target=aniChecking,daemon=True)
aniCheck.start()

msgCheck = threading.Thread(target=msg_checking,daemon=True)
msgCheck.start()

#start the animation graph with interval of 10 second
ani= animation.FuncAnimation(fig, animate, frames=18, interval=10000,repeat=False)
plt.show()
