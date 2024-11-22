import os
import cv2 
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://face-recognitionb2014580-default-rtdb.firebaseio.com/",
    'storageBucket':"face-recognitionb2014580.firebasestorage.app"
})
bucket = storage.bucket()
# Set up the camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load the background image
imgBackground = cv2.imread("Resources/background.png")

# Load the mode images
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Load the encoding file
print("Loading encode file...")
file= open('EncodeFile.p', 'rb') 
encodeListWithIds = pickle.load(file)
file.close()
encodeListKnown, userIds = encodeListWithIds
print("Encode file loaded")
modeType = 0
counter = 0
id = -1
imgUser = []
while True:
    success, img = cap.read()
    # Resize the image
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Find the faces in the current frame
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Overlay the image on the background
    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
    if faceCurFrame:
        # Loop through the faces in the current frame
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceIds = face_recognition.face_distance(encodeListKnown, encodeFace)

            # Find the index of the best match
            matchIndex = np.argmin(faceIds)

            # If a match is found, draw a bounding box around the face
            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = userIds[matchIndex]
                
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendance",imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1
                    
                        
            if counter != 0:
                if counter ==1:
                    #Get the data
                    userInfo = db.reference(f'Users/{id}').get()
                    print(userInfo)
                    #Get img from storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(),np.uint8)
                    imgUser = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                    #Update data of attendance
                    datetimeObject = datetime.strptime(userInfo['last_attendance'],"%Y-%m-%d %H:%M:%S")
                    secondElapse = (datetime.now()-datetimeObject).total_seconds()
                    print(secondElapse)
                    if secondElapse > 30:
                        ref=db.reference(f'Users/{id}')
                        userInfo['total_attendance']+=1
                        ref.child('total_attendance').set(userInfo['total_attendance'])
                        ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter =0
                        imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
                if modeType !=3:
                    if 10< counter <20:
                        modeType = 2
                    if counter <=10:
                        cv2.putText(imgBackground,str(userInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    
                        cv2.putText(imgBackground,str(userInfo['major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    
                        cv2.putText(imgBackground,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    
                        cv2.putText(imgBackground,str(userInfo['lever']),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    
                        cv2.putText(imgBackground,str(userInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    
                        cv2.putText(imgBackground,str(userInfo['starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    
                        (w,h), _ = cv2.getTextSize(userInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                        offset = (414 - w)// 2
                        cv2.putText(imgBackground,str(userInfo['name']),(808+ offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1) 
                    
                        imgBackground[175:175+216,909:909+216] = imgUser
                
                counter +=1
                if counter >=20:
                    counter = 0
                    modeType = 0
                    userInfo =[]
                    imgUser =[]
                    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # Display the output          
    cv2.imshow("Face Attendance",imgBackground)
    
    # Exit on key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break