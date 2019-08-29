import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import threading

#this is to check wifi reconncetion
#if machine is not connceted to any wifi, it will show timeout after 3 second
import socket
socket.setdefaulttimeout(3)



fig=plt.figure()
plt.ylim(0,6)
plt.xlim([0,19])
y=[]
x=[]
#this count will act as a timer, and it will count up to 180
#so we can plot a graph that is over 3 minutes period
count=-10
temp_value=0
previous=0
differences=0

#standard mqtt setup definition
def setup_mqtt():
    client=mqtt.Client("proximity_over_time")
    client.on_connect=OnConnect
    client.on_message=OnMessage
    client.connect("192.168.4.1",1883,120)
    return client

#standard mqtt onConnect definition
def OnConnect(client,userdata,flags,rc):
    client.subscribe("sensors/proximity/count")


#standard mqtt onMessage definition
def OnMessage(client,userdata,msg):
    global temp_value
    if msg.topic =="sensors/proximity/count":
        temp_value=(int(msg.payload.decode()))


def animate(i):
    global y
    global x
    global differences
    #clear the graph
    plt.clf()
    #y limit is 0 to 6 this time since we cant really get more than 7 reading from proximity sensor over 10 second period
    #x limis is still 0 to 19 to represent 3 minutes(180s)
    plt.ylim(0,6)
    plt.xlim([0,19])
    #the title this time is also live. it will update total sensor reading over the last 3 minutes
    s="total motion detected in last 3 minutes :" + str(differences)
    plt.title(s, fontsize=15)
    plt.bar(x,y)


def assign_value():
    global temp_value
    global count
    global previous
    global differences
    global y
    global x

    #again, a timer to run this def every 10s
    threading.Timer(10.0,assign_value).start()
    local_temp=abs(temp_value-previous)
    #this if condition is to fix the problem with sensors on RPI0
    #Sean's code does not reset sensor readings every 10 second, it will keep increasing until you manually reboot the device(not sure about this reboot thing)
    #so problem we had was the reading I received can be 10k+. to work around, I have to calculate a difference between current and last reading
    #This local_temp<20 is to avoid when first starting this program, previous is still 0, temp_value can already be 10k+
    #then the difference for the first number is huge, didnt have enough time to find another fix
    #so If the difference for the first number is bigger than 20 we just give y list an 1
    if local_temp<20:
        #append the difference to y list
        y.append(temp_value-previous)
        #add this difference to our total differences
        differences += (temp_value-previous)
        #just same purposes as in magnitude_over_time, displaying 0 to 180 on x_axis
        count +=10
        x.append(str(count))
        #update previous with lastest value
        previous=temp_value
    else:
        #explained above
        y.append(1)
        differences +=1
        print(y)
        count +=10
        x.append(str(count))
        print(x)
        previous=temp_value

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
        print("Still waiting for mqtt connection")
        #sleep for a second to allow reconncetion, should be fine without it but while loop runs too fast, it may cause error
    time.sleep(1)

assign_value()

#this is to check if we have reached 3 minutes,
#we reset the graph every 3 minutes, all variable associated to plotting is reset
def aniChecking():
    global count
    global ani
    global differences
    global y
    global x
    while True:
        if count>=190:
            count=0
            differences=0
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
