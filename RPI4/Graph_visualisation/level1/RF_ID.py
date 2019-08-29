import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import paho.mqtt.publish as pub
import time
import threading

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(3)


on_bed = False
timer = 0
fig=plt.figure()
plt.ylim('Not on Bed','On Bed')
#this bed stores RF_ID card number, if adding or changing RFID card used, change the value
bed="73,65,173,135"

#standard mqtt setup definition
def setup_mqtt():
	client=mqtt.Client("RFIDProcessor")
	client.on_connect=OnConnect
	client.on_message=onMessage
	#192.168.4.1 is the ip for the network that RPI0 is hosting
	client.connect("192.168.4.1",1883,120)
	return client

#standard mqtt onConnect definition
def OnConnect(client,userdata,flags,rc):
    client.subscribe('sensors/RFID/raw')

#standard mqtt onMessage definition
def onMessage(client,userdata,msg):
    global timer
    global on_bed
    global bed
    if msg.topic =='sensors/RFID/raw':
		#if message matches given bed ID
        if msg.payload.decode() == bed:
			#on_bed is true and we have received a mqtt message, so timer is reset
            on_bed = True
            timer=0
        else:
			#otherwise its not on bed and timer is reset
            on_bed = False
            timer=0

def animate(i):
	#clear graph, and plot "not on bed" and "on bed" on y-axis, if on bed we plot 1, otherwise 0
    global on_bed
    plt.clf()
    plt.ylim('Not on Bed','On Bed')
    if on_bed:
        print("on bed")
        plt.bar('is it on bed',1)
    else:
        plt.bar('is it on bed',0)

#this runs in another thread constantly. and it checks if we are receiving mqtt messages in the last 3 second
#if no message is received in the last three second , we assume its not on bed anymore
def msg_checking():
    global on_bed
    global timer
    while True:
        timer +=1
        if timer >=3:
            on_bed=False
            timer =0
        time.sleep(1)

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

#if mqtt is connected then we start the mqtt message check thread
check = threading.Thread(target=msg_checking,daemon=True)
check.start()

#start the animation graph with interval of 500ms
ani= animation.FuncAnimation(fig, animate,interval=500)
plt.show()
