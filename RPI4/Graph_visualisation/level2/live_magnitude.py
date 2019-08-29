import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(3)

temp="0"
y=0
fig=plt.figure()
plt.ylim(0,10)

#standard mqtt setup definition
def setup_mqtt():
	client=mqtt.Client("movement_level2")
	client.on_connect=OnConnect
	client.on_message=OnMessage
	client.connect("192.168.4.1",1883,120)
	return client

#standard mqtt onConnect definition
def OnConnect(client,userdata,flags,rc):
	client.subscribe("sensors/accelerometer/magnitude")


#standard mqtt onMessage definition
def OnMessage(client,userdata,msg):
    global temp
    if msg.topic =="sensors/accelerometer/magnitude":
		#for every new message we receive, we store the sensor reading in temp variable
        temp=msg.payload.decode()


def assign_value():
    global y
    global temp
    while True:
		#if sensor reading is less than 0.43, this is the sensor reading (most of the time) when bear is not moving
		#then we assume there is no movement, make y=0
        if float(temp)<0.43:
            y=0
        else:
		#else we assign this lastest sensor reading to y
            y=float(temp)
        time.sleep(1)



def animate(i):
    global value
    global label
    global y
	#clear the graph
    plt.clf()
	#y axies is 0 to 10, on average if u are moving a bear, we get a reading between 1-5
	#its mostly just 1.ish, unless you are throwing it across the room, u hardlt get it over 10
    plt.ylim(0,10)
    print(y)
    plt.bar(['Magnitude'],y)

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

#if mqtt is connected then we start the assigning value thread
assign_ = threading.Thread(target=assign_value,daemon=True)
assign_.start()

#start the animation graph with interval of 500ms
ani= animation.FuncAnimation(fig, animate,interval=500)
plt.show()
