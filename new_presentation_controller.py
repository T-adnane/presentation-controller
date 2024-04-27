import os
import cv2
import mediapipe as mp
import numpy as np
import pyautogui

screen_width, screen_height = pyautogui.size()
screen_width, screen_height = int(screen_width / 2), int(screen_height / 2)
cap = cv2.VideoCapture(0)
presentation_folder = "presentation_assets"
pathPresentation = sorted(os.listdir(presentation_folder), key=len)
slideNbr = 0

colorPath = "colors"
myList = os.listdir(colorPath)
colorList = []
for imPath in myList:
    image = cv2.imread(f'{colorPath}/{imPath}')
    colorList.append(image)
imgColor = colorList[0]

initHand = mp.solutions.hands
mainHand = initHand.Hands(min_detection_confidence=0.6)
draw = mp.solutions.drawing_utils

button_pressed = False
annotations = [[]]
annotationNumber = 0
annotationStart = False
eraser_pressed = False

color = (0, 0, 255)

def handLandmarks(colorImg):
    landmarkList = []
    landmarkPositions = mainHand.process(colorImg)
    landmarkChek = landmarkPositions.multi_hand_landmarks
    if landmarkChek is not None:
        for hand in landmarkChek:
            for landmark in hand.landmark:
                draw.draw_landmarks(frame, hand, initHand.HAND_CONNECTIONS)
                landmarkList.append([int(landmark.x * screen_width), int(landmark.y * screen_height)])
    return landmarkList


def fingersUp(lmList):
    fingers = [0, 0, 0, 0, 0, 0]
    # Pinky finger is up
    if (lmList[20][1] < lmList[19][1]) and (lmList[19][1] < lmList[18][1]):
        fingers[0] = 1
    # Ring finger is up
    if (lmList[16][1] < lmList[15][1]) and (lmList[16][1] < lmList[14][1]):
        fingers[1] = 1
    # Middle finger is up
    if (lmList[12][1] < lmList[11][1]) and (lmList[12][1] < lmList[10][1]):
        fingers[2] = 1
    # Index finger is up
    if (lmList[8][1] < lmList[7][1]) and (lmList[8][1] < lmList[6][1]):
        fingers[3] = 1
    # Thump finger is to right
    if (lmList[4][0] < lmList[3][0]) and (lmList[4][0] < lmList[2][0]) and (lmList[4][1] > lmList[5][1]):
        fingers[4] = 1
    # Thump finger is to left
    if (lmList[4][0] > lmList[3][0]) and (lmList[4][0] > lmList[2][0]) and (lmList[4][1] > lmList[5][1]):
        fingers[5] = 1
    return fingers


while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (screen_width, screen_height))

    lmList = handLandmarks(frame)
    cv2.line(frame, (0, 200), (screen_width, 200), (255, 255, 255), 1)
    pathFullPresentation = os.path.join(presentation_folder, pathPresentation[slideNbr])
    slideCurrent = cv2.imread(pathFullPresentation)

    slideCurrent = cv2.resize(slideCurrent, (screen_width, screen_height))
    if lmList:
        fingers = fingersUp(lmList)
        if lmList[5][1] < 200 and not button_pressed:
            # condition to go to the back slide
            if fingers == [1, 1, 1, 1, 0, 1] and slideNbr > 0:
                slideNbr -= 1
                button_pressed = True
                annotations = [[]]
                annotationNumber = 0
                annotationStart = False

            # condition to go to the next slide
            elif fingers == [1, 1, 1, 1, 1, 0] and slideNbr < len(pathPresentation)-1:
                slideNbr += 1
                button_pressed = True
                annotations = [[]]
                annotationNumber = 0
                annotationStart = False

        if lmList[5][1] > 200:
            button_pressed = False


        # The Condition to start pointer
        if fingers == [0, 0, 1, 1, 0, 0] or fingers == [0, 0, 1, 1, 1, 0] or fingers == [0, 0, 1, 1, 0, 1]:
            cv2.circle(slideCurrent, (lmList[8][0], lmList[8][1]), 12, (0, 0, 255), cv2.FILLED)
            annotationStart = False
            # Condition to change the color
            if lmList[8][1] < 50:
                slideCurrent[0:100, 0:screen_width] = cv2.resize(imgColor, (960, 100))
                cv2.circle(slideCurrent, (lmList[8][0], lmList[8][1]), 12, (0, 0, 255), cv2.FILLED)
                annotationStart = False
                if lmList[8][0] > 100 and lmList[8][0] < 200:
                    imgColor = colorList[1]
                    color = (255, 0, 0)
                elif lmList[8][0] > 400 and lmList[8][0] < 500:
                    imgColor = colorList[2]
                    color = (0, 0, 0)
                elif lmList[8][0] > 690 and lmList[8][0] < 790:
                    imgColor = colorList[3]
                    color = (0, 0, 255)

        # The condition to start painting
        if fingers == [0, 0, 0, 1, 0, 0] or fingers == [0, 0, 0, 1, 1, 0] or fingers == [0, 0, 0, 1, 0, 1]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            if color == (255, 0, 0):
                annotations[annotationNumber].append((lmList[8][0], lmList[8][1], 3))
            elif color == (0, 0, 0):
                annotations[annotationNumber].append((lmList[8][0], lmList[8][1], 2))
            elif color == (0, 0, 255):
                annotations[annotationNumber].append((lmList[8][0], lmList[8][1], 1))
        else:
            annotationStart = False

        # The condition to erase the last painting
        if fingers == [0, 0, 0, 0, 0, 0] or fingers == [0, 0, 0, 0, 1, 0] or fingers == [0, 0, 0, 0, 0, 1]:
            if annotations and eraser_pressed == False:
                annotations.pop(-1)
                annotationNumber -= 1
                eraser_pressed = True
                annotationStart = False
        else:
            eraser_pressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                if annotations[i][j][2] == 1:
                    cv2.line(slideCurrent, annotations[i][j-1][:2], annotations[i][j][:2], (0, 0, 255), 8)
                elif annotations[i][j][2] == 2:
                    cv2.line(slideCurrent, annotations[i][j-1][:2], annotations[i][j][:2], (0, 0, 0), 8)
                elif annotations[i][j][2] == 3:
                    cv2.line(slideCurrent, annotations[i][j-1][:2], annotations[i][j][:2], (255, 0, 0), 8)

    x_offset = (screen_width - frame.shape[1]) // 2
    y_offset = (screen_height - frame.shape[0]) // 2
    screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    screen[y_offset:y_offset + frame.shape[0], x_offset:x_offset + frame.shape[1]] = frame
    cv2.imshow('frame', screen)
    cv2.imshow('slides', slideCurrent)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
