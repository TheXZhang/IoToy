import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time
import paho.mqtt.client as mqtt

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(3)


temp=[]
fig=plt.figure()
plt.ylim(0,5)
plt.xlim([0,19])
#list of value for y_axis
y=[]
#list of value for x_axis
x=[]
#this count will act as a timer, and it will count up to 180
#so we can plot a graph that is over 3 minutes period
count=-10
last_10s_value=[]


#standard mqtt setup definition
def setup_mqtt():
	client=mqtt.Client("movement_level3")
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
		#unlike previous levels, in this level, we store values in a list
		#it will store up to 10 values, and we will calculate an average in other def
        temp.append(msg.payload.decode())
        time.sleep(1)

def assign_value():
    global count
    global y
    global x
    global temp
    global last_10s_value
	#transfer our list of values into a local temporary list
    local_temp=temp
	#starting a new thread with a timer of 10 second, so def assign_value is executed every 10s
    threading.Timer(10.0,assign_value).start()
	#for all item in the list ,we check if they are above the base value
	#if above we store the value in a new list, if not we store 0 in the a list
    for item in local_temp:
        if float(item)<0.43:
            last_10s_value.append(0)
        else:
            last_10s_value.append(float(item))

    #calculate a average using our filtered list
    average=np.average(last_10s_value)
    print(average)

	#append average for ploting
    y.append(average)
	#clear all list for next round of values
    temp.clear()
    local_temp.clear()
    last_10s_value.clear()
	#add 10 to count everytime this def is run
    count +=10
	#append the count timer for ploting
    x.append(str(count))



def animate(i):
    global y
    global x
    plt.clf()
	#y axis is from 0 to 5, the average is probably lower but i didnt have enough time to test
    plt.ylim(0,5)
	#x axis is from 0 to 19, represent 0 to 180 in 10 second interval
    plt.xlim([0,19])
    plt.title("10 seconds Average magnitude over 3 minutes period", fontsize=15)
    plt.bar(x,y)

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

#if mqtt is connected then we start the animation check thread
aniCheck = threading.Thread(target=aniChecking,daemon=True)
aniCheck.start()

time.sleep(5)

#start the animation graph with interval of 10 second
ani= animation.FuncAnimation(fig, animate, interval=10000)
plt.show()
