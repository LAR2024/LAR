import cv2
import numpy as np
from robolab_turtlebot import Turtlebot, detector

# this function takes in img, and returns key-value pair of r,g,b masks
def makeMasks(img):
  hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32) / 255.
  h=hsv_img[:,:,0]
  s=hsv_img[:,:,1]
  v=hsv_img[:,:,2]
  hsv=[h,s,v]
  fil={}

  def f(x,r,d,c):
      return cond[c](np.fabs(x-r),d).astype(np.uint8)

  for key in ['r','g','b']:
      ref ={'r':[.5,1,.6],'g':[.22,.6,.3],'b':[.38,.8,.8]}[key]
      diff={'r':[.47,.3,.3],'g':[.1,.3,.4],'b':[.1,.3,.6]}[key]
      rc  ={'r':[ 1, 0, 0],'g':[ 0, 0, 0],'b':[ 0, 0, 0]}[key]
      cond=[np.matrix.__lt__,np.matrix.__gt__]
      buf =list(map(lambda x,r,d,c:f(x,r,d,c),hsv,ref,diff,rc))
      fil[key]=cv2.bitwise_and(cv2.bitwise_and(buf[0],buf[1]),buf[2])
  return fil

# countours=[r:,g:,b:]

# this function takes in key-value pair of countours for r,g,b values
# draws them on img, and returns pillar rectangles
def drawBoxes(rgb_contours,img=None):
  pill={}
  for key in ['r','g','b']:
    contours=rgb_contours[key]
    border_color={'r':(0,0,255),'g':(0,255,0),'b':(255,0,0)}[key]
    pill[key]=[]
    for contour in contours:
      x,y,w,h = cv2.boundingRect(contour)
      if w*h>5000 and w*3<h and w*9>h:
          pill[key].append((x,y,w,h))
          if type(img)!=None:
            r_img = cv2.drawContours(img,[contour],0,(255,255,255),2)
            r_img = cv2.rectangle(img,(x,y),(x+w,y+h),border_color,2)
          else:
            r_img = None
  return pill,r_img
     
