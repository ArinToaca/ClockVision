import numpy as np
import cv2
import time
import requests
import base64
import traceback

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FONT = cv2.FONT_HERSHEY_SIMPLEX
FILENAME = 'face.png'
EXTENSION = 'png'

def clamp(minimum, x, maximum):
    #print("Clamping " + str(x) + "; " + str(int(max(minimum, min(x, maximum)))))
    return int(max(minimum, min(x, maximum)))

def save_face(face_mat):
  cv2.imwrite(FILENAME,face_mat)
  
def send_face():
  try:
    with open(FILENAME, "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read())
      
    response = requests.send_image_to_server(encoded_string, EXTENSION)
    print(response)
  except:
    traceback.print_exc()
    return "error"
  
  return response
  
def send_face_to_server(base64):
  return True
  
def display_message(message, sleepTime):
  print("Displaying message: " + message)
  text_image = np.zeros((SCREEN_HEIGHT,SCREEN_WIDTH,3), np.uint8)
  
  cv2.putText(text_image,message,(0,130), FONT, 1, (200,255,155))
  
  cv2.imshow('window',text_image)
  
  cv2.waitKey(sleepTime)

def exhaust_all_frames(vidcap):
  vidcap.release()
  
  return cv2.VideoCapture(0)

def run():
  cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
  cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
  
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
      
      if len(faces) > 1:
        display_message('Too many faces detected in image: ' + str(len(faces)), 2000)
        cap = exhaust_all_frames(cap)
        continue
      
      for (x,y,w,h) in faces:
          #save face to file
          start_y = clamp(0, y - y*rectangle_scale_increase/100, height)
          end_y = clamp(0, y + h + (y + h)*rectangle_scale_increase/100, height)
          
          start_x = clamp(0, x - x*rectangle_scale_increase/100, width)
          end_x = clamp(0, x + w + (x + w)*rectangle_scale_increase/100, width)
          
          #generate face subimage
          roi_face = frame[start_y:end_y, start_x:end_x]
          save_face(roi_face)
          send_face()

          #show image
          cv2.imshow('window',roi_face)  
          cv2.waitKey(2000)

          #show status
          display_message('Saved face', 2000)
          cap = exhaust_all_frames(cap)
          
          #display blue rectangle on output
          cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)       
  
      # Display the resulting frame
      cv2.imshow('window',frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

  # When everything done, release the capture
  cap.release()
  cv2.destroyAllWindows()
  
if __name__ == '__main__':
  run()
  
  