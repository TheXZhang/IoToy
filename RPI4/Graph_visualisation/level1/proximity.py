import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import time
import threading

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(3)

#initialise global variables
fig=plt.figure()
plt.ylim('NO','YES')
#temp_value is value we received with each mqtt message
temp_value=0
#previous_y is just last y we used to plot the graph
previous_y=0
y=0


#standard mqtt setup definition
def setup_mqtt():
    client=mqtt.Client("graph")
    client.on_connect=OnConnect
    client.on_message=OnMessage
    #192.168.4.1 is the ip for the network that RPI0 is hosting
    client.connect("192.168.4.1",1883,120)
    return client

#standard mqtt onConnect definition
def OnConnect(client,userdata,flags,rc):
    client.subscribe("sensors/proximity/count")


#standard mqtt onMessage definition
def OnMessage(client,userdata,msg):
    global temp_value
    if msg.topic =="sensors/proximity/count":
        #with every message we received we put the value into temp_value
        temp_value=(int(msg.payload.decode()))

def animate(i):
    global y
    #clear graph, set y axis with no and yes then plot using new y in every loop
    plt.clf()
    plt.ylim('NO','YES')
    plt.bar("are you moving around the bear",y)


def assign_value():
    global temp_value
    global previous_y
    global y

    while True:
        # if the lastest temp_value is not equal to the latest y value, there is a change in sensor data
        # hence sensor is capturing people around it, so we set y to 1 to represnt True
        if temp_value != previous_y:
            print(1)
            y=1
        else:
        # if two values are equal, sensor is not detecting any people around it, so 0
            print(0)
            y=0

        #update previous_y with lastest value
        previous_y=temp_value
        # 2 second sleep time, proximity sensor only refreshes its reading every 2 second
        time.sleep(2)

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
