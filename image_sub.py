import paho.mqtt.client as mqtt
import time
import cv2
import numpy as np
import base64
import os

faceProto="opencv_face_detector.pbtxt"
faceModel="opencv_face_detector_uint8.pb"
ageProto="age_deploy.prototxt"
ageModel="age_net.caffemodel"
genderProto="gender_deploy.prototxt"
genderModel="gender_net.caffemodel"


def on_connect(client, userdata, flags, rc):
    print("Connected to camera 1 with result code "+str(rc))
    client.subscribe("face/cam1")
    print("Connected to camera 2 with result code "+str(rc))
    client.subscribe("face/cam2")

for i in range (1,3):

    def highlightFace(net, frame, conf_threshold=0.7):
        if frame is None:
            return 0, []
        frameOpencvDnn=frame.copy()
        frameHeight=frameOpencvDnn.shape[0]
        frameWidth=frameOpencvDnn.shape[1]
        blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob)
        detections=net.forward()
        faceBoxes=[]
        for i in range(detections.shape[2]):
            confidence=detections[0,0,i,2]
            if confidence>conf_threshold:
                x1=int(detections[0,0,i,3]*frameWidth)
                y1=int(detections[0,0,i,4]*frameHeight)
                x2=int(detections[0,0,i,5]*frameWidth)
                y2=int(detections[0,0,i,6]*frameHeight)
                faceBoxes.append([x1,y1,x2,y2])
                cv2.rectangle(frameOpencvDnn, (x1,y1), (x2,y2), (0,255,0), int(round(frameHeight/150)), 8)
        return frameOpencvDnn,faceBoxes


    def on_message(client, userdata, message,):
    #    f = open('output.jpg', "wb")
    #    print(type(message.payload))
    #    f.write(message.payload)
    #    print("Image Received")
    #    f.close()


    #    jpg_as_np = np.frombuffer(message.payload, dtype=np.uint8)
    #    img = cv2.imdecode(jpg_as_np, flags=1)
        jpg_as_np = np.frombuffer(message.payload, dtype=np.uint8)
        img = cv2.imdecode(jpg_as_np, flags=1)
        
        cv2.imwrite('./0.jpg', img)
        frame = cv2.imread('./0.jpg')
        os.remove('./0.jpg')
        
        padding=20
        resultImg,faceBoxes=highlightFace(faceNet,frame)
        if not faceBoxes:
            print("No face detected on camera "+str(i))
            message = client.publish("face/val"+str(i), "no face")
            return

        for faceBox in faceBoxes:
            face=frame[max(0,faceBox[1]-padding):
                    min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
                    :min(faceBox[2]+padding, frame.shape[1]-1)]

            blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
            genderNet.setInput(blob)
            genderPreds=genderNet.forward()
            gender=genderList[genderPreds[0].argmax()]
            print(f'Gender: {gender}')

            ageNet.setInput(blob)
            agePreds=ageNet.forward()
            age=ageList[agePreds[0].argmax()]
            print(f'Age: {age[1:-1]} years')
            message = client.publish("face/val"+str(i), str(gender) + ", " + str(age))

    faceNet=cv2.dnn.readNet(faceModel,faceProto)
    ageNet=cv2.dnn.readNet(ageModel,ageProto)
    genderNet=cv2.dnn.readNet(genderModel,genderProto)
    MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
    ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    genderList=['Male','Female']

    mqttBroker="test.mosquitto.org"
    client = mqtt.Client("test_image_processor")
    client.connect(mqttBroker,1883,60)

    client.on_message=on_message
    client.on_connect = on_connect
    client.loop_forever()