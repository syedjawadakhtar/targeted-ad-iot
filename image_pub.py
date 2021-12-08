import paho.mqtt.client as mqtt
import cv2
import advertisment
from time import sleep

def getImage():
    cap = cv2.VideoCapture(0)
    hasFrame, frame = cap.read()
    if frame.shape[0] < 100:
        return
    image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
    message = client.publish("face/cam", image_bytes)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("face/val")

    

def on_message(client, userdata, message,):
    
    print(str(message.payload))
    temp = str(message.payload)
    if "no" not in temp:
        string = temp.split(" ")
        age = string[1]
        age = age.replace("'","")
        gender = string[0]
        gender = gender.replace("b'", "")
        advertisment.show_add(age, gender)

    
    

def on_publish(client,userdata,result):
    print("sending image")

mqttBroker = "test.mosquitto.org"
client = mqtt.Client("test_camera_device")
client.connect(mqttBroker,1883,60)
client.on_publish = on_publish
client.on_message = on_message
client.on_connect = on_connect
client.subscribe("face/val")

while True:
    client.loop()
    getImage()
