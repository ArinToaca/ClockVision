import numpy as np
import cv2

def clamp(minimum, x, maximum):
    print("Clamping " + str(x) + "; " + str(int(max(minimum, min(x, maximum)))))
    return int(max(minimum, min(x, maximum)))

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

cap = cv2.VideoCapture(0)

rectangle_scale_increase = 30

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    height, width, channels = frame.shape

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 2, 5)
    for (x,y,w,h) in faces:
        #save face to file
        start_y = clamp(0, y - y*rectangle_scale_increase/100, height)
        end_y = clamp(0, y + h + (y + h)*rectangle_scale_increase/100, height)
        
        start_x = clamp(0, x - x*rectangle_scale_increase/100, width)
        end_x = clamp(0, x + w + (x + w)*rectangle_scale_increase/100, width)
        
        roi_face = frame[start_y:end_y, start_x:end_x]
        cv2.imwrite('face.png',roi_face)
    
        #display blue rectangle on output
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        
    if len(faces) > 0:
      break
        

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()