import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(3)

#initialise global variables
temp="0"
y=0
fig=plt.figure()
#Y axis limit is set to 1 sa its a yes/no graph
plt.ylim(0,1)


#standard mqtt setup definition
def setup_mqtt():
	client=mqtt.Client("movement_level1")
	client.on_connect=OnConnect
	client.on_message=OnMessage
	#192.168.4.1 is the ip for the network that RPI0 is hosting
	client.connect("192.168.4.1",1883,120)
	return client

#standard mqtt onConnect definition
def OnConnect(client,userdata,flags,rc):
	client.subscribe("sensors/accelerometer/magnitude")


#standard mqtt onMessage definition
def OnMessage(client,userdata,msg):
	#temp is a temporary varible for holding sensor values.
	#this variable is later accessed in another thread
	#temp value is updated with each new message
    global temp
    if msg.topic =="sensors/accelerometer/magnitude":
        temp=msg.payload.decode()

#this occurs in a different thread, its task is to assign value for y
def assign_value():
    global y
    global temp
	#while true loop, this assigning is done continuously so the graph is displaying the latest sensor reading
    while True:
		#I made up a base value 0.43, this is the sensor reading (most of the time) when bear is not moving
        if float(temp)>0.43:
			#if if over this base value, then there is a movement, we give y 1 to represent YES
            y=1
        else:
			#otherwise give y 0 to represent No
            y=0
		#make loop sleep for a second I believe it worked without this ,but I just had it to slow down the while loop
        time.sleep(1)

#animation definition for the animated graph
def animate(i):
    global y
	#this clears the graph
    plt.clf()
	#instead of showing 0 and 1 on y-axis, we are showing yes and no for movement
    plt.ylim('No','Yes')
	#for debugging purposes
    print(y)
	#graph is ploted with "is there a movement in x-axis." change to whatever
    plt.bar(['is there a movement'],y)

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
