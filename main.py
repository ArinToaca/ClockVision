import numpy as np
import cv2
import time
import requests
import base64
import traceback
import json

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FONT = cv2.FONT_HERSHEY_DUPLEX
FILENAME = 'face.png'
EXTENSION = 'png'
CASCADE_PATH = './haarcascade_frontalface_alt.xml'

STOP = 0

def clamp(minimum, x, maximum):
    #print("Clamping " + str(x) + "; " + str(int(max(minimum, min(x, maximum)))))
    return int(max(minimum, min(x, maximum)))

def save_face(face_mat):
  cv2.imwrite(FILENAME,face_mat)
  
def send_face():
  print("Sending data to server!")

  with open(FILENAME, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
    
  response = requests.send_image_to_server(encoded_string, EXTENSION)
  print("response %s" % response)
  json_data = json.loads(response)
  print("json data %s" % json_data)
  
  return json_data
  
def send_face_to_server(base64):
  return True
  
def display_message(message, sleepTime, fontScale):
  print("Displaying message: " + message)
  text_image = np.zeros((SCREEN_HEIGHT,SCREEN_WIDTH,3), np.uint8)
  text_image[:] = (255, 255, 255)
  
  # get boundary of this text
  textsize = cv2.getTextSize(message, FONT, fontScale, 2)[0]
  
  # get coords based on boundary
  textX = int((text_image.shape[1] - textsize[0]) / 2)
  textY = int((text_image.shape[0] + textsize[1]) / 2)
  
  # add text centered on image
  cv2.putText(text_image, message, (textX, textY ), FONT, fontScale, (255, 0, 0), 2)
  
  cv2.imshow('window',text_image)
  
  cv2.waitKey(sleepTime)

def draw_text_on_image(mat, text, fontScale=1):
  # get boundary of this text
  textsize = cv2.getTextSize(text, FONT, fontScale, 2)[0]
  
  # get coords based on boundary
  textX = int((mat.shape[1] - textsize[0]) / 2)
  textY = int((mat.shape[0] + textsize[1]) / 2)
  
  # add text centered on image
  cv2.putText(mat, text, (textX, textY ), FONT, fontScale, (255, 0, 0), 2)

def exhaust_all_frames(vidcap):
  vidcap.release()
  
  return cv2.VideoCapture(0)

def close_app(event,x,y,flags,param):
    global STOP 
    if event == cv2.EVENT_LBUTTONDOWN:
      STOP = 1

def run():
  global STOP
  #cv2.namedWindow("window")
  cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
  cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
  
  cv2.setMouseCallback('window',close_app)
  
  face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
  
  cap = cv2.VideoCapture(0)
  
  rectangle_scale_increase = 30
  
  consecutive_face_frames = 0
  last_x = 0
  last_y = 0
  
  while(not STOP):
      # Capture frame-by-frame
      ret, frame = cap.read()
      height, width, channels = frame.shape
  
      # Our operations on the frame come here
      gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  
      faces = face_cascade.detectMultiScale(gray, 1.3, 5)
      
      if len(faces) > 1:
        display_message('Too many faces detected in image: ' + str(len(faces)), 750, 1)
        cap = exhaust_all_frames(cap)
        continue
      
      if len(faces) == 0:
        consecutive_face_frames = 0
      
      for (x,y,w,h) in faces:
          if consecutive_face_frames < 10:
            center_x = x + w / 2
            center_y = y + h / 2
            if abs(center_x - last_x) < 50 and abs(center_y - last_y) < 25:
              consecutive_face_frames += 1
            else:
              draw_text_on_image(frame, 'Hold still!', 1.3)
              consecutive_face_frames = 0
              
            last_x = center_x
            last_y = center_y
            
            #display blue rectangle on output
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)     
            cv2.rectangle(frame,(x,y+h+10),(int(x+w*consecutive_face_frames/10),y+h+12),(255,0,0),2) 
            
            continue
              
          consecutive_face_frames = 0
              
          #save face to file
          start_y = clamp(0, y - y*rectangle_scale_increase/100, height)
          end_y = clamp(0, y + h + (y + h)*rectangle_scale_increase/100, height)
          
          start_x = clamp(0, x - x*rectangle_scale_increase/100, width)
          end_x = clamp(0, x + w + (x + w)*rectangle_scale_increase/100, width)
          
          #generate face subimage
          roi_face = frame[start_y:end_y, start_x:end_x]
          save_face(roi_face)
          
          display_message('Sending data to server', 2000, 2)
          
          try:
            rsp = send_face()
            print("LOGARIN rsp" % rsp)
            
            if rsp['status'] == 'Intruder':
              message = 'Persoana neautorizata!'
              display_message(message, 2000, 2)
            else:
              message = 'Bine ai venit ' + rsp['name'] + '!'
              if rsp['status'] == 'Entered':
                message2 = 'Poti intra in cladire!'
              else:
                message2 = 'Poti iesi din cladire!'
            
              display_message(message, 1000, 2)
              display_message(message2, 2000, 2)
          except:
            display_message('Error while transmitting image to server', 2000, 1)
            raise
          cap = exhaust_all_frames(cap)

          #show image
          #cv2.imshow('window',roi_face)  
          #cv2.waitKey(2000)

          #show status
          #display_message('Saved face', 2000)
          #cap = exhaust_all_frames(cap)   
  
      # Display the resulting frame
      cv2.imshow('window',frame)
      if (cv2.waitKey(1) & 0xFF == ord('q')):
          break

  # When everything done, release the capture
  cap.release()
  cv2.destroyAllWindows()
  
if __name__ == '__main__':
  run()
  
  
