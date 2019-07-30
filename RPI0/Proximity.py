
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
from datetime import datetime

#try connect to broker
def tryConnect():
    try:
        client.connect('192.168.4.1',1883,120)
        print 'Proximity Sensor Connected!'
        return True
    except:
        print 'Proximity Sensor Failed to connect'
        time.sleep(1)
        return False

def reset():
    with open('count.txt','w') as f:
        f.write('0')
    global count
    count = 0
    print 'Proximity Sensor Count Reset'

def on_message(client,userdata,msg):
    print msg.payload
    if msg.payload.decode() == 'reset':
        reset()

def trySub():
    try:
        client.subscribe('test/message/reset')
        print 'Proximity Sensor Subscribed!'
        return True
    except:
        print 'Proximity Sensor Failed to subscribe'
        return False

count = 0
subscribed = False
#Set pin 23 as input with resistor down
GPIO.setmode(GPIO.BCM)
GPIO.setup(23,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
client=mqtt.Client('ProxSensor')
client.on_message=on_message
isConnected = tryConnect()

while True:
        if not subscribed:
            subscribed = trySub()
        client.loop_start()
        #if not connected to broker try again
        if not isConnected:
            isConnected = tryConnect()
        #if input from radar and is connected to broker
        if GPIO.input(23) & isConnected & subscribed:
            count+=1
            log = 'Count: ' + str(count) + ', Time: ' + str(datetime.now()) + '\n'
            #publish count
            try:
                client.publish('test/message',str(count))
            except:
                print 'Detected movement but error in publishing'
                tryConnect()
                trySub()
            with open('ProxSensorLog.txt','a+') as f:
                f.write(log)
            time.sleep(2.1)
