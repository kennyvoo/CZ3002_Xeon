#https://github.com/DhrumilParikh-github/ObjectDetection-without-GPU
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import cv2
import numpy as np
import time
import os
import urllib.request
import threading, time
ticker = threading.Event()
from PIL import Image 
import imutils
import urllib



### Camera Parameter ###
# CAMERA_ID= ["LWN_L4_C1","LWN_L5_C1"]
# CAMERA_IP=['http://10.27.137.242:8080/video','http://10.27.220.116:8080/video']
CAMERA_ID= ["LWN_L5_C1"]
CAMERA_IP=['http://192.168.1.245:8080/video']
multicamera=False  #initialize as False
if(len(CAMERA_ID)>1):
     multicamera=True
FIRESTORE_COLLECTION='Seats'
font = cv2.FONT_HERSHEY_PLAIN

    
def main():
      ### Set Up FireStore ###
     cred = credentials.Certificate('FireStore.json')
     firebase_admin.initialize_app(cred)
     db = firestore.client()

     ### Load Yolo ###
     net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
     classes = []
     with open("coco.names", "r") as f:
          classes = [line.strip() for line in f.readlines()]
     layer_names = net.getLayerNames()
     output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
     colors = np.random.uniform(0, 255, size=(len(classes), 3))


     #Keep track of the timestamp of item detected
     seatItemDetectedTime={}

     ### Inference every 5s if replace while True
     #WAIT_TIME_SECONDS = 5
     #while not ticker.wait(WAIT_TIME_SECONDS):
     while True:
          class_ids = []
          confidences = []
          boxes = []
          seatImageToDetect=[]
          seatImageToDetectSize=[]
          SeatsArray=[]
          #Loop through each camera and append the cropped images into SeatArray[]
          for i in range(len(CAMERA_IP)):
               
               cap = cv2.VideoCapture(CAMERA_IP[i])
               _, frame = cap.read()

               seatTemp=[]
               # Retrieve all thet Seats related to this camera from the database
               SeatsList= db.collection(FIRESTORE_COLLECTION).where(u"cameraId",u"==",CAMERA_ID[i]).stream()
               for seat in SeatsList:
                    SeatsArray.append(seat.to_dict()) 
                    seatTemp.append(seat.to_dict())


               ##Crop out seats images from the full picture
               for i in seatTemp:

                    im1=frame[int(i["y1Img"]):int(i["y2Img"]),int(i["x1Img"]):int(i["x2Img"])]
                    im = imutils.resize(im1, width=416)

                    #append the frame and the size of the frame for drawing bounding box in the postprocessing part
                    seatImageToDetect.append(im) 
                    seatImageToDetectSize.append([int(i["x2Img"])-int(i["x1Img"]),int(i["y2Img"])-int(i["y1Img"])])

                    #draw out a bounding box for each seats in blue colour
                    cv2.rectangle(frame, (int(i["x1Img"]), int(i["y1Img"])), (int(i["x2Img"]), int(i["y2Img"])), (255,0,0), 2)
                    cv2.putText(frame,i["seatName"], (int(i["x1Img"]),int(i["y1Img"]) + 30), font, 3, (255,0,0), 3)
               
               if(multicamera):
                    cap.release()


          ### fit into the network
          blob = cv2.dnn.blobFromImages(seatImageToDetect, 1/255, (416, 416), (0, 0, 0), True, crop=False)
          net.setInput(blob)
          outs = net.forward(output_layers)

          #post-processing the output of the network
          for i in range(len(seatImageToDetect)):
               humanDetected=False
               itemDetected=False

               for out in outs:
                    out_tensor = out[i]
                    for detection in out_tensor:
                         scores = detection[5:]
                         class_id = np.argmax(scores)
                         confidence = scores[class_id]
                         if confidence > 0.6:
                              # Object detected
                              center_x = int(detection[0] *seatImageToDetectSize[i][0])+int(SeatsArray[i]["x1Img"])
                              center_y = int(detection[1] *seatImageToDetectSize[i][1])+int(SeatsArray[i]["y1Img"])
                              w = int(detection[2] *seatImageToDetectSize[i][0])
                              h = int(detection[3] *seatImageToDetectSize[i][1])

                              # Rectangle coordinates
                              x = int(center_x - w / 2)
                              y = int(center_y - h / 2)

                              boxes.append([x, y, w, h])
                              confidences.append(float(confidence))
                              class_ids.append(class_id)



                              if(classes[class_id]=="bottle"):  # check if bottle is detected
                                   itemDetected=True
     
                              if(classes[class_id]=="person"): # if a person is detected 
                                   humanDetected=True
                                   itemDetected=False 
                                   print("human detected")
                                   # record the starting time when the bottle is first detected. change the status to detected.
                              elif (classes[class_id]=="bottle" and not humanDetected and SeatsArray[i]["status"]!="Detected" and SeatsArray[i]["status"]!="Hogged"):
                                   SeatsArray[i]["status"]="Detected"
                                   db.collection(FIRESTORE_COLLECTION).document(SeatsArray[i]["id"]).update({u'status':'Detected'})
                                   seatItemDetectedTime[SeatsArray[i]["id"]]=round(time.time(),0)  
                                   itemDetected=True
                                   print("Object Detected")
                              
               # print(len(SeatsArray))
               # If the Seat is reserved or unavailable, skip the updating of the status. Can be improved by skipping the detection in the first placee
               if(SeatsArray[i]["status"]=="Reserved" or SeatsArray[i]["unavailable"]==True):
                    continue
               
               #  if human is detected and the seat status is not occupied 
               if(humanDetected and SeatsArray[i]["status"]!="Occupied"):
                    SeatsArray[i]["status"]="Occupied"
                    db.collection(FIRESTORE_COLLECTION).document(SeatsArray[i]["id"]).update({u'status':'Occupied'})
                    print( SeatsArray[i]["id"]+" Updated to occupied")
               #  if item is detected and seat status is not Hogged
               elif(itemDetected and SeatsArray[i]["status"]!="Hogged" and not humanDetected):
                    #minus the difference in time
                    diff=round(time.time(),0) -seatItemDetectedTime[SeatsArray[i]["id"]]
                    # if it's more than 5s, changed the seat status to hogged
                    print(diff)
                    if(diff>=5):
                         SeatsArray[i]["status"]="Hogged"
                         db.collection(FIRESTORE_COLLECTION).document(SeatsArray[i]["id"]).update({u'status':'Hogged'})
                         print(SeatsArray[i]["id"]+" Updated to Hogged")
               # if no human and item is detected, change the status to available if it's not available.
               elif (SeatsArray[i]["status"]!="Available" and not humanDetected and not itemDetected):
                    SeatsArray[i]["status"]="Available"
                    db.collection(FIRESTORE_COLLECTION).document(SeatsArray[i]["id"]).update({u'status':'Available'})
                    print(SeatsArray[i]["id"]+" Updated to Available")

          if(multicamera): # if multicamera, we wont show the result 
               continue

          # perform nms to eliminate the overlap boxes.
          indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.7, 0.3)
          

          # draw out bouding box for detected bounding boxes
          for i in range(len(boxes)):
               if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    confidence = confidences[i]
                    color = colors[class_ids[i]]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, color, 3)

          # resize the frame to smaller size.
          imS = cv2.resize(frame, (960, 540))
          cap.release()
          cv2.imshow("Image", imS)
          key = cv2.waitKey(5)
          if key == 27:
               break
     cap.release()
     cv2.destroyAllWindows()

def testCamera():
     ### CHECK if the number of camera_id is the same as the number of camera_IP
     if(len(CAMERA_ID)!=len(CAMERA_IP)):
          print("error")
          exit()
     for i in CAMERA_IP:
          cap = cv2.VideoCapture(i) 
          if cap is None or not cap.isOpened():
               print('Warning: unable to open video source: ', i)
               return False
     return True
     
if __name__ == "__main__":
     init=testCamera()   # check if any camera is not connected properly
     if init==False:
          exit()
     main()
     