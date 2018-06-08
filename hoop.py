import cv2
import serial
import numpy as np
import subprocess
import imutils

ard=False
points = []
sendPrev=0
frames = 0
tracking = False
cam = 0
cap = cv2.VideoCapture(cam)

cap.set(12, 1.0) #Saturation
print("FPS: "+str(cap.get(5))) #FPS
print("Brightness: "+str(cap.get(10))) #Brightness
print("Contrast: "+str(cap.get(11))) #Contrast
if cam == 0:
    cap.set(10, 0.5)
    cap.set(11, 0.5)

if ard:
    ser = serial.Serial()
    ser.port = "/dev/ttyACM1"#check this for the right port
    ser.baudrate = 115200
    ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    ser.parity = serial.PARITY_NONE #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    #ser.timeout = None          #block read
    #ser.timeout = 1            #non-block read
    #ser.timeout = 2              #timeout block read
    #ser.xonxoff = False     #software flow control
    #ser.rtscts = False     #hardware (RTS/CTS) flow control
    #ser.dsrdtr = False       #hardware (DSR/DTR) flow control
    #ser.writeTimeout = 0.5     #timeout for write
    ser.open()

cX = 0
cY = 0
k = 0

intercept = 0
initial = (0, 0)
distance = 0

def close_points(p1, p2, x):
    if abs(p1[0]-p2[0]) < x and abs(p1[1]-p2[1]) < x:
        return True
    else:
        return False

while k != 27 and k != ord('q'):
    ret, frame = cap.read()

    if cam > 5:
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    else:
        frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
    blurred = cv2.GaussianBlur(frame, (5, 5), 5)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Green BGR 35 50 50
    # 65 255 255
    lower = np.array([35, 50, 50])
    upper = np.array([65, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    if np.count_nonzero(mask) and len(cnts) > 0:
        c = cnts[0]
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

    if frames % 5 == 0:
        points.append((cX, cY))

    if len(points) > 4 and close_points(points[-4], points[-1], 5) and not close_points(initial, (cX, cY), 5):
        #initial = (cX, cY)
        initial = (640,240)
        if not initial == (0, 0) and not initial == (640, 240):
            subprocess.Popen(["aplay", "/home/freder/Music/misc/beep.wav"])

    if len(points) > 2:
        slope = 1000
        if initial[0] != cX:
            slope = float ((initial[1] - cY)) / (initial[0] - cX)
            intercept = cY - int (slope * (cX + distance))

    send = intercept
    if ard:
        send = 23900 - int(float(intercept) / 480 * 23900)
        # send=raw_input("Send intercept: ")
        if abs(send - sendPrev) >= 500 and frames % 5 == 0:
            ser.write(str(send) + "E")
            sendPrev = send

    print intercept
    k = cv2.waitKey(1) & 0xFF
    frames += 1

cap.set(12, 0.5)
cap.release()
if ard:
    ser.close()