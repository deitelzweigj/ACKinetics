import cv2
import serial
from serial import tools
from serial.tools import list_ports
import numpy as np
import imutils
import subprocess
import time

ard=True
#ard=False

debugt = False
test = time.clock()
times = [0] * 5

points = []

sendPrev=0

frames = 0
tracking = False
cam = 2#0 for native webcam, 2 for other webcam
cap = cv2.VideoCapture(cam)

#https://stackoverflow.com/questions/11420748/setting-camera-parameters-in-opencv-python
cap.set(12, 1.0)#Saturation0.5
print("FPS: "+str(cap.get(5)))#FPS30
print("Brightness: "+str(cap.get(10)))#Brightness0.5
print("Contrast: "+str(cap.get(11)))#Contrast0.0
if cam == 0:
    cap.set(10, 0.5)
    cap.set(11, 0.5)

#print(serial.tools.list_ports)
#python -m serial.tools.list_ports
if ard:
    ser = serial.Serial()
    ser.port = "/dev/ttyACM0"#check this for the right port
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

#distance = -17
distance = -40

def close_points(p1, p2, x):
    if abs(p1[0]-p2[0]) < x and abs(p1[1]-p2[1]) < x:
        return True
    else:
        return False

while k != 27 and k != ord('q'):
    test=time.clock()
    ret, frame = cap.read()

    if cam > 5:
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    else:
        frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
    blurred = cv2.GaussianBlur(frame, (5, 5), 5)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    #Green BGR 35 50 50
    #65 255 255
    lower = np.array([27, 100, 100])
    upper = np.array([47, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]

    if debugt:
        times[0] += time.clock() - test
        print "a" + str(time.clock()-test)
        test=time.clock()
    if np.count_nonzero(mask) and len(cnts) > 0:
        c = cnts[0]
        M = cv2.moments(c)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

        # draw the contour and center of the shape on the image
        cv2.drawContours(frame, [c], -1, (255, 0, 0), 2)
        cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)

    if debugt:
        times[1] += time.clock() - test
        print "b" + str(time.clock()-test)
        test=time.clock()

    #cv2.imshow('blur', blurred)

    if frames % 5 == 0:
        points.append((cX, cY))

    if debugt:
        times[2] += time.clock() - test
        print "c" + str(time.clock()-test)
        test=time.clock()
    if len(points) > 4 and close_points(points[-4], points[-1], 5) and not close_points(initial, (cX, cY), 5):
        initial = (cX, cY)
        #initial = (640,240)
        if not initial == (0, 0) and not initial == (640, 240):
            subprocess.Popen(["aplay", "/home/freder/Music/misc/beep.wav"])
    if debugt:
        times[3] += time.clock() - test
        print "d" + str(time.clock()-test)
        test=time.clock()
    if len(points) > 2:
        slope = 1000
        if initial[0] != cX:
            slope = float ((initial[1] - cY)) / (initial[0] - cX)
            intercept = cY - int (slope * (cX + distance))
            #cv2.circle(frame, (-distance, intercept), 7, (255, 0, 0), -1)
            cv2.line(frame, initial, (-distance, intercept), (0, 255, 0), thickness=2)
        cv2.circle(frame, initial, 7, (0, 0, 0), -1)

    if debugt:
        times[4] += time.clock() - test
        print "e" + str(time.clock()-test)
        test=time.clock()
    send=intercept
    send = 32000 - int(float(intercept) / (277 - 107) * 23000 - 23000 / 480 * 107)
    if ard:
        if frames % 1 == 0:
            ser.reset_output_buffer()
        #send=-(intercept-240)#*100
        #send=raw_input("Send intercept: ")
        if abs(send-sendPrev) >= 500 and frames % 20 == 0 and send >= 0 and send <= 23000:
            ser.write(str(send)+"\n")
            sendPrev=send
        #ser.write('E')

        #line = ser.readline()
        #print line
    #print intercept
    #print send


    #cv2.imshow('line', frame)
    #cv2.moveWindow('line', 0, 0)
    k = cv2.waitKey(1) & 0xFF
    frames += 1

if debugt:
    print "\nAverages\na "+str(times[0]/frames)+"\nb "+str(times[1]/frames)+"\nc "+str(times[2]/frames)+"\nd "+str(times[3]/frames)+"\ne "+str(times[4]/frames)
cap.set(12, 0.5)
cap.release()
cv2.destroyAllWindows()
if ard:
    ser.close()
