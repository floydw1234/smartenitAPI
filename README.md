# smartenitAPI
the communication for smartenit sensors. both mqtt and zigbee systems

2 files make up the "API":
One having to do with the MQTT zigbee sensors and One with the smartnit hub zigbee system.
I will be giving for of an overview in this READ.me but there will be comments in the code
explaining what each line/function does as well as how to change configurations to 
make the code work with your system




MQTT/Python:
To be able to use this, you must first change all the credentials for MQTT and pymongo based
on what your system is using. If you are using the cpmqtt1 server then you should keep the mqtt
stuff the same. 

The Mqtt sensors are constantly subscribing to a specific topic relating to a 
some attribute that they have, e.g. "powerFactor". Then when the sensor recieves a message on
that topic then, they publish to a topic relating the the attribute. The python code MQTT_sub.py
first has a list of MAC_IDS and TOPICS that it publishes to, to prompt the sensor to publish, and 
starts to subscribe to the related topic. Then has an on_message function that deals with
the incomming mqtt message and that is where you can put any code that you would like to 
store it, or relay it along, or do cool math with it(in the on_message function). The code dies
after a couple of seconds 



NodeJS/Hub approach:
This one is slightly more simple than the last. The smartinet zigbee system has a software and 
zigbee communication codebase that makes it easy to get the data from the sensors. The file
fetchPower.js does a couple of things. First

