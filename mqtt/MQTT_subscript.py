
import paho.mqtt.client as mqtt
import json
import thread
import time
import datetime


import MySQLdb

from pymongo import MongoClient
import pprint
import datetime
import numpy
#below commented out code is for setting up a mysql data connection
'''
import mysql.connector

cnx = mysql.connector.connect(user='calplug', password ='energy345', host='cpmqtt1.calit2.uci.edu', database ='energychannel')
cursor = cnx.cursor()
'''

#below is how you set up the database connection for mongo
client1 = MongoClient("mongodb://localhost:27017/west")
db = client1.pulses
collection = db.pulse


#these are connection credentials for mqtt
user = "calplug"
password = "Calplug2016"
host = "cpmqtt1.calit2.uci.edu"
port = 1883


#these two lists are iterated through below in the on_connect function
mac_list = ['5ccf7fd854a2'] #need to put all macid's that you are using into here
topicList = ['InstantaneousDem0and','PowerFactor'] # put all desired topics into here


samples = dict()
for mac in mac_list:
    for topic in topicList:
        samples[mac+topic] = None

#make a for loop for all of the plugs
list1 = []
keepalive = 60
sTopicSub = 'out/devices/'
sTopicPub = 'in/devices/'

PAYLOAD_POST = '{"method": "post","params":{}}'
PAYLOAD_GET = '{"method": "get","params":{}}'


#this kills the connection after 2 seconds
# this kills the process after 3 secconds
def disconnect_countdown(client):
    #print("WAITING TO COUNT DOWN")
    time.sleep(2)
    client.disconnect()
    #print("------DISCONNECTING---------")
    time.sleep(1)
    exit()



def on_connect(client, userdata, flags, rc):
    thread.start_new_thread( disconnect_countdown, (client,))
    client.subscribe(sTopicSub+"#")
    for mac_id in mac_list:
        #print(mac_id)
        #print("Connected with result code "+str(rc))
        # reconnect then subscriptions will be renewed.
        #client.publish(sTopicPub + mac_id + '/0/cdo/FirmwareVersion', payload = PAYLOAD_GET)
        client.publish(sTopicPub + mac_id + '/1/OnOff/OnOff', payload = PAYLOAD_GET)
        client.publish(sTopicPub + mac_id + '/1/SimpleMeteringServer/CurrentSummationDelivered', payload = PAYLOAD_GET)
        client.publish(sTopicPub + mac_id + '/1/SimpleMeteringServer/InstantaneousDemand', payload = PAYLOAD_GET)
        client.publish(sTopicPub + mac_id + '/1/SimpleMeteringServer/RMSCurrent', payload = PAYLOAD_GET)
        client.publish(sTopicPub + mac_id + '/1/SimpleMeteringServer/Voltage', payload = PAYLOAD_GET)
        client.publish(sTopicPub + mac_id + '/1/SimpleMeteringServer/PowerFactor', payload = PAYLOAD_GET)
        #dont change anythin

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #the following lines are there to parse the topic, macid, and value from the mqtt message
    my_topic = msg.topic[msg.topic.rfind('/')+1:]
    my_mac_id = msg.topic.replace("out/devices/", "")
    my_mac_id = my_mac_id.replace("/1/SimpleMeteringServer/"+my_topic, "")
    my_mac_id = my_mac_id.replace("/0/SimpleMeteringServer/"+my_topic, "")
    my_mac_id = my_mac_id.replace("/1/OnOff/OnOff", "")
    my_value = str(msg.payload.decode("utf8"))
    my_value = my_value.replace('{"response": {"value":',"")
    my_value = my_value.replace("}","")

    #uncomment these lines whenever you are debugging the script. its good to be able to see the values
    print("MY MAC: " +  my_mac_id)
    print("MY TOPIC: " + my_topic)
    print("MY VALUE: " + my_value)



    #Replace this to add custom communication/data storage ****starting here***
    #where you have access to the value, topic, and macId from the incomming mqtt message

    #this is an example of code used to insert into a mongodb. Notice the json formating of the insert
    #look at pymongo for further info about python/mongo connections
    if my_topic == "CurrentSummationDelivered":
        collection = db.CurrentSummationDelivered
        collection.insert_one({'value': my_value, 'when': datetime.datetime.now() })
    elif my_topic == "InstantaneousDemand":
        collection = db.InstantaneousDemand
        collection.insert_one({'value': my_value, 'when': datetime.datetime.now() })
    elif my_topic == "Voltage":
        collection = db.Voltage
        collection.insert_one({'value': my_value, 'when': datetime.datetime.now() })
    elif my_topic == "PowerFactor":
        collection = db.PowerFactor
        collection.insert_one({'value': my_value, 'when': datetime.datetime.now() })
    elif my_topic == "RmsCurrent":
        collection = db.RmsCurrent
        collection.insert_one({'value': my_value, 'when': datetime.datetime.now() })


    #*****ending here**** because this is where you are receiveing each piece of data


    #note that the way that this is set up the topic will only be the last part of the OG topics(much shorter)
    # for example /in/devices/<mac_address>/1/SimpleMeteringServer/InstantaneousDemand --> InstantaneousDemand
    #client.publish("mac_id", payload = my_mac_id)

client = mqtt.Client()
client.on_connect = on_connect
timeStart = time.time()

client.on_message = on_message #this makes it so on_message happens every time the client recieves a message
client.username_pw_set(user, password)
client.connect(host, port, keepalive)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
     # manual interface.
client.loop_forever()

#below shows an example of inserting data into a mysql database. The below code would fit be located inside
#the onMessage function to properly store data
'''
while time.time() - timeStart < 3:



print {"time":time.time(),"PFd1":samples['600194111e44PowerFactor'], "PFd2":samples['5ccf7fd852e1PowerFactor'], "PFd3":samples['6001941122a9PowerFactor'] ,"PFA": samples['5ccf7fd85885PowerFactor'], "Dem1": samples['600194111e44InstantaneousDemand'] ,"Dem2": samples['5ccf7fd852e1InstantaneousDemand'] ,"Dem3":samples['6001941122a9InstantaneousDemand'] ,"DemA":samples['5ccf7fd85885InstantaneousDemand'] }

try: # stores data into mysql database

      # 85 aggreagate
      # e1 blower #2
      # a9 fan #3
      # 44 lamp #1

  insert_point = ("INSERT INTO trainingData" "( PF1,Dem1, PF2,Dem2, PF3, Dem3, PFA, DemA, Timestamp) " "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
  insert_data = (samples['600194111e44PowerFactor'],samples['600194111e44InstantaneousDemand'],samples['5ccf7fd852e1PowerFactor'],samples['5ccf7fd852e1InstantaneousDemand'],samples['6001941122a9PowerFactor'],samples['6001941122a9InstantaneousDemand'],samples['5ccf7fd85885PowerFactor'],samples['5ccf7fd85885InstantaneousDemand'],time.time())
  cursor.execute(insert_point,insert_data)
  cnx.commit()


except TypeError as e:
  print(e)
  cnx.rollback()
'''
