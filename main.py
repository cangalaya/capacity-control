from collections import deque
from imutils.video import WebcamVideoStream
import imutils
import cv2
import time
import math


def dotproduct(v1, v2):
    '''
    Distance between 2 dots
    :param v1: dot1
    :param v2: dot2
    :return:
    '''
    return sum((a*b) for a, b in zip(v1, v2))


def run():
    # A list to put moving trajectory
    traceList = []
    vs = cv2.VideoCapture("example_01.mp4")     #http//alonso:manuel2007@192.168.1.3:8040/video -> ip camera
                                                #/home/djalonso/Downloads/example_01.mp4        -> using a video (path)
    # Background frame
    lastFrame = None
    time.sleep(1)

    # A distance to determine whether the two objects detected in two frames is the same object.
    frameDistance =  100    #100
    # Window size
    winWidth = 500      #500
    winHeight = 300     #300

    # Color filter (RED)
    redLower = (120, 4, 24)
    redUpper = (226, 58, 96)

    # Standard line
    outLine = int(winHeight/2 - 20)     #blue
    inLine = int(winHeight/2 + 0)      #red
    
    # Indoor direction
    inVector = (0,1) # y-axis

    inCount = 0
    outCount = 0

    timer = 0

    # tasa de refrescamiento (cambio de iluminación)
    tasa_refresh = 100

    while True:
        _,frame = vs.read()

        frame = imutils.resize(frame, width=winWidth, height=winHeight)
        # Tracing color
        #rbg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #gray = cv2.inRange(rbg, redLower, redUpper)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if lastFrame is None:
            lastFrame = gray
            continue

        frameDelta = cv2.absdiff(lastFrame, gray)
        dst = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        dst = cv2.dilate(dst, None, iterations=5)
        _, cnts, _ = cv2.findContours(dst.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Every detected rectangle
        for c in cnts:
            print(cv2.contourArea(c))
            c_check = False
            # Guess why ^v^  130000
            if (cv2.contourArea(c)) < 3000 or (cv2.contourArea(c) > 30000):
                continue

            if cv2.contourArea(c) > 130000:
                lastFrame = gray
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            cv2.circle(frame, center, 1, (0, 0, 255), 5)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


            # Record the trajectory of each object
            for k,v in enumerate(traceList):
                if math.hypot(center[0] - v[0][0], center[1] - v[0][1]) < frameDistance:
                    if (center[1] < inLine) and (center[1] > outLine):
                        v.appendleft(center)
                        cv2.putText(frame, str(k), center, cv2.FONT_ITALIC, 1.0, (255, 255, 255), 1)
                        c_check = True
                        break
                    elif len(v) >= 2:
                        firstPoint = v[len(v)-1]
                        dx = v[0][0] - firstPoint[0]
                        dy = v[0][1] - firstPoint[1]
                        vt = (dx, dy)
                        if dotproduct(vt, inVector) > 0:
                            inCount += 1
                        else:
                            outCount += 1
                        traceList.remove(v)
                        break

            if (c_check is False) and (center[1] < inLine) and (center[1] > outLine):
                # Treat one dot as a new center point of one object
                traceList.append(deque([center]))
        """
        timer = timer+1
        if timer > tasa_refresh:
            timer = 0
            #traceList = []
            lastFrame = gray
        """
        cv2.putText(frame, "Entraron: {}".format(str(inCount)), (10, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "Salieron: {}".format(str(outCount)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv2.line(frame, (0, outLine), (winWidth, outLine), (250, 0, 1), 2)  # blue line
        cv2.line(frame, (0, inLine), (winWidth, inLine), (0, 0, 255), 2)  # red line

        cv2.imshow("contours", dst)
        cv2.imshow("origin", frame)

        key = cv2.waitKey(1) & 0xFF

if __name__ == '__main__':
    run()
