import os
import cv2
import mediapipe as mp
import numpy as np

width, height = 1280, 720

cap = cv2.VideoCapture(0)

folderPath = "presentation_assets"
pathImages = sorted(os.listdir(folderPath), key=len)
imgNbr = 0
hs, h, ws, w = 2*120, 800, 2*213, 1550

initHand = mp.solutions.hands
mainHand = initHand.Hands(min_detection_confidence=0.5)
draw = mp.solutions.drawing_utils

def handLandmarks(colorImg):
    landmarkList = []
    landmarkPositions = mainHand.process(colorImg)
    landmarkChek = landmarkPositions.multi_hand_landmarks
    if landmarkChek:
        for hand in landmarkChek:
            for index, landmark in enumerate(hand.landmark):  # Change here
                draw.draw_landmarks(img, hand, initHand.HAND_CONNECTIONS)
                landmarkList.append([index, int(landmark.x*1280), int(landmark.y*720)])
    return landmarkList

face_line = 200

def action_recognation(lmlist):
    nbr = 0
    # if all fingers are up and thumb finger is to left
    if lmlist[8][2] < lmlist[7][2] and lmlist[12][2] < lmlist[11][2] and lmlist[16][2] < lmlist[15][2] and lmlist[20][2] < lmlist[19][2] and lmlist[4][1] < lmlist[2][1] and lmlist[4][1] < lmlist[3][1]:
        nbr = 1
    # if all fingers are up and thumb finger is to right
    elif lmlist[8][2] < lmlist[7][2] and lmlist[12][2] < lmlist[11][2] and lmlist[16][2] < lmlist[15][2] and lmlist[20][2] < lmlist[19][2] and lmlist[4][1] > lmlist[2][1] and lmlist[4][1] > lmlist[3][1]:
        nbr = 2
    # if index and middle fingers are up
    elif lmlist[8][2] < lmlist[7][2] and lmlist[12][2] < lmlist[11][2] and lmlist[16][2] > lmlist[15][2] and lmlist[20][2] > lmlist[19][2]:
        nbr = 3
    # if index finger is up and all the others are down
    elif lmlist[8][2] < lmlist[7][2] and lmlist[12][2] > lmlist[11][2] and lmlist[16][2] > lmlist[15][2] and \
            lmlist[20][2] > lmlist[19][2]:
        nbr = 4
    # if all the fingers are down
    elif lmlist[8][2] > lmlist[7][2] and lmlist[12][2] > lmlist[11][2] and lmlist[16][2] > lmlist[15][2] and lmlist[20][2] > lmlist[19][2]:
        nbr = 5
    return nbr

button_pressed = False
annotations = [[]]
annotationNumber = 0
annotationStart = False
eraser_pressed = False

while True:
    sucess, img = cap.read()
    img = cv2.flip(img, 1)
    lmlist = handLandmarks(img)
    cv2.line(img, (0, face_line), (width, face_line), (255, 255, 255), 10)
    pathFullImage = os.path.join(folderPath, pathImages[imgNbr])
    imgCurrent = cv2.imread(pathFullImage)

    imgSmall = cv2.resize(img, (ws, hs))
    imgCurrent = cv2.resize(imgCurrent, (w, h))
    imgCurrent[0:hs, w-ws:w] = imgSmall
    if lmlist and button_pressed == False:
        if action_recognation(lmlist) == 1 and lmlist[5][2] < face_line and imgNbr > 0 and imgNbr <= len(pathImages)-1:
            imgNbr -= 1
            button_pressed = True
            annotations = [[]]
            annotationNumber = 0
            annotationStart = False
        if action_recognation(lmlist) == 2 and lmlist[5][2] < face_line and imgNbr >= 0 and imgNbr < len(pathImages)-1:
            imgNbr += 1
            button_pressed = True
            annotations = [[]]
            annotationNumber = 0
            annotationStart = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 255), 12)

    if lmlist:
        if action_recognation(lmlist) == 3:
            indexFinger = int(np.interp(lmlist[8][1], [150, w//2], [2, w])), int(np.interp(lmlist[8][2], [250, h-250], [0, h]))
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
            annotationStart = False
        if action_recognation(lmlist) == 4:
            indexFinger = int(np.interp(lmlist[8][1], [150, w//2], [2, w])), int(np.interp(lmlist[8][2], [250, h-250], [0, h]))
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        if action_recognation(lmlist) == 5:
            if annotations and eraser_pressed == False:
                annotations.pop(-1)
                annotationNumber -= 1
                eraser_pressed = True
                annotationStart = False
        else:
            eraser_pressed = False

    if lmlist and lmlist[5][2] > face_line:
        button_pressed = False


    cv2.imshow("Presentation Controller", imgCurrent)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

###################""""
#40:21
##########################

cv2.destroyAllWindows()
cap.release()