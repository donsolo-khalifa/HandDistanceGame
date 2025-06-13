import random
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
import cvzone
import time

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

DISPLAY_WIDTH, DISPLAY_HEIGHT = 800, 600

# Hand Detector
detector = HandDetector(detectionCon=0.5, maxHands=2)

# Find Function
# x is the raw distance y is the value in cm
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C

# Grid setup
rows, cols = 3, 3
x_spaces = np.linspace(200, 1080, cols, dtype=int)
y_spaces = np.linspace(200, 520, rows, dtype=int)
grid_targets = [(x, y) for y in y_spaces for x in x_spaces]

# Game Variables
current_target_idx = 0
cx, cy = grid_targets[current_target_idx]
color = (255, 0, 0)
counter = 0
score = 0
timeStart = time.time()
totalTime = 30
cyan = (255, 255, 0)

cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", DISPLAY_WIDTH, DISPLAY_HEIGHT)


def get_next_target():
    """Get next target position from grid"""
    global current_target_idx, cx, cy
    current_target_idx = random.randint(0, len(grid_targets) - 1)
    cx, cy = grid_targets[current_target_idx]


def reset_game():
    """Reset game state"""
    global score, timeStart, counter, current_target_idx, cx, cy, color
    score = 0
    timeStart = time.time()
    counter = 0
    current_target_idx = 0
    cx, cy = grid_targets[current_target_idx]
    color = (255, 0, 0)


# Loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if time.time() - timeStart < totalTime:
        hands, img = detector.findHands(img, draw=False)

        if hands:
            for hand in hands:
                lmList = hand['lmList']
                x, y, w, h = hand['bbox']
                x1, y1 = lmList[5][:2]
                x2, y2 = lmList[17][:2]

                distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
                A, B, C = coff
                distanceCM = A * distance ** 2 + B * distance + C
                # print(distanceCM, distance)

                if distanceCM < 100:
                    if x < cx < x + w and y < cy < y + h:
                        counter = 1

                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)
                cvzone.putTextRect(img, f'{int(distanceCM)} cm', (x + 5, y - 10), colorR=(255, 0, 0))

        if counter:
            counter += 1
            color = (0, 255, 0)
            if counter == 3:
                get_next_target()
                color = (255, 0, 255)
                score += 1
                counter = 0

        # Draw all grid positions
        for i, (gx, gy) in enumerate(grid_targets):
            if i == current_target_idx:
                # Draw active target
                cv2.circle(img, (gx, gy), 30, color, cv2.FILLED)
                cv2.circle(img, (gx, gy), 10, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, (gx, gy), 20, (255, 255, 255), 2)
                cv2.circle(img, (gx, gy), 30, (50, 50, 50), 2)
            else:
                # Draw inactive grid positions (dimmed)
                cv2.circle(img, (gx, gy), 25, (100, 100, 100), cv2.FILLED)
                cv2.circle(img, (gx, gy), 25, (50, 50, 50), 2)

        # Game HUD
        cvzone.putTextRect(img, f'Time: {int(totalTime - (time.time() - timeStart))}',
                           (1000, 75), scale=3, offset=20, colorR=cyan)
        cvzone.putTextRect(img, f'Score: {str(score).zfill(2)}', (60, 75), scale=3, offset=20, colorR=cyan)
    else:
        cvzone.putTextRect(img, 'Game Over', (400, 400), scale=5, offset=30, thickness=7, colorR=cyan)
        cvzone.putTextRect(img, f'Your Score: {score}', (450, 500), scale=3, offset=20, colorR=cyan)
        cvzone.putTextRect(img, 'Press R to restart', (460, 575), scale=2, offset=10, colorR=cyan)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    if key == ord('r'):
        reset_game()

cap.release()
cv2.destroyAllWindows()
