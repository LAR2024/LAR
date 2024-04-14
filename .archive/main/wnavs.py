# ver: Tue Apr  2 12:07:00 CEST 2024

#p_d = 50+-2 mm
#p_dist = 50+-5 mm
#s_dist <= 50 mm

import uuid
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import random

def findNearestTarget(targets):
    if len(targets)==0:
        return None
    nearest=targets[0]
    distance=np.linalg.norm(nearest[0])
    for target in targets[1:]:
        new_distance=np.linalg.norm(target[0])
        if (new_distance<distance):
            nearest=target
            distance=new_distance
    return nearest

def dvals(x):
  return tuple((((np.array(x)*[w,-h])//[real_w,real_h])+origin).astype(np.int64))

def display(location,color,marker_type='column',pointer=None):
    if marker_type=='column' or marker_type=='target':
        cv2.drawMarker(img, dvals(location), color, cv2.MARKER_SQUARE, 10, 1)
    if marker_type=='robot' or marker_type=='target':
        cv2.drawMarker(img,dvals(location), color, cv2.MARKER_TILTED_CROSS, 10, 1)
    if marker_type=='highlight':
        cv2.drawMarker(img,dvals(location), color, cv2.MARKER_SQUARE, 15, 1)
    if pointer is not None:
        cv2.line(img,dvals(location),dvals(location+pointer), color,1)

def displayConnection(col1,col2,is_flag):
    if SHOW_ALL_CONNECTIONS or (SHOW_ACTIVE_CONNECTIONS and is_flag):
        connection_color={
                True:(255,255,255),
                False:(90,90,90)
                }[is_flag]
        cv2.line(img,dvals(col1['pos']),dvals(col2['pos']),connection_color,1)

def getTargetsFromFlag(col1,col2):
    targets=[]
    flag_center=col2['pos']+(col1['pos']-col2['pos'])/2
    connection_direction=np.array(((col1['pos']-col2['pos'])/np.linalg.norm(col1['pos']-col2['pos']))*TARGET_FROM_CENTER)

    relative_target=np.matmul([[0,1],[-1,0]],connection_direction)

    right_column=[]
    direction=[]
    if relative_target[0]>col1['pos'][0] or (relative_target[0]==col1['pos'][0] and relative_target[1]>col1['pos'][1]):
        right_column=col1
        if right_column['color']=='r':
            direction=-connection_direction
        else:
            direction=connection_direction
    else:
        right_column=col2
        if right_column['color']=='r':
            direction=-connection_direction
        else:
            direction=connection_direction
    
    rcol=[random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)]
    #display(right_column['pos'],rcol,'highlight')
    targets+=[[flag_center+relative_target,direction]]
    #display(flag_center+relative_target,rcol,'highlight')
    relative_target=np.matmul([[0,-1],[1,0]],connection_direction)
    #display(flag_center+relative_target,rcol,'highlight')
    targets+=[[flag_center+relative_target,direction]]
    return targets

def getTargets(columns):
    targets=[]
    #columns=list(map(lambda x:{'pos':np.array([x[0][0],-x[0][1]]),'color':x[1]},columns))
    unchecked=columns
    for col1 in columns:
        #random.seed(1)
        color={'b':(255,0,0),'g':(0,255,0),'r':(0,0,255)}[col1['color']]
        display(col1['pos'],color)
        if SHOW_TRACKERS:
            cv2.line(img,dvals(col1['pos']),dvals(np.array([0,0])),color,1)
            if SHOW_TRACKERS_DIST:
                cv2.putText(img, "%.2f"%(np.linalg.norm(col1['pos'])) , dvals((col1['pos'])//2+10) , FONT, 0.4,color, 1)
        unchecked=unchecked[1:]
        for col2 in unchecked:
            if (not (col1['color']=='r' and col2['color']=='b') and
                not (col1['color']=='b' and col2['color']=='r') and
                not (col1['color']=='g' and col2['color']=='g')):
                continue
            is_flag=MIN_DISTANCE<np.linalg.norm(col1['pos']-col2['pos'])<MAX_DISTANCE
            displayConnection(col1,col2,is_flag)
            if is_flag:
                targets+=getTargetsFromFlag(col1,col2)
    return targets



def getPositionRelativeToRobot(x):
    if x[0]<-IN_FRONT_MARGIN:
        return 'left'
    elif x[0]>IN_FRONT_MARGIN:
        return 'right'
    else:
        return 'front'

def displayInFrontArea():
    cv2.line(img,(origin[0]+IN_FRONT_MARGIN,0),(origin[0]+IN_FRONT_MARGIN,h), (200,90,90),1)
    cv2.line(img,(origin[0]-IN_FRONT_MARGIN,0),(origin[0]-IN_FRONT_MARGIN,h), (200,90,90),1)

def nameTargets(targets,old_names):
    names={}
    for target in targets:
        named=False
        for name in old_names.keys():
            if (np.isclose(target,old_names[name],0.05,0.05)).all():
                names[name]=target
                named=True
                break
        if not named:
            print("!!! name change !!!")
            names[str(uuid.uuid1())]=target
    return names

def displayTargetNames(names):
    for name in names.keys():
        cv2.putText(img, name , dvals(names[name][0]) , FONT, 1,(255,255,255), 1)

def handleMouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
       pos=([x,y]-origin)
       for name in targets_by_name.keys():
           if (np.isclose(pos,targets_by_name[name][0],0,5)).all():
               print(name)
               break






h=1000
w=1000
real_h=1
real_w=1
MAX_DISTANCE=1250
MIN_DISTANCE=0
TARGET_FROM_CENTER=0.05
SHOW_TRACKERS=True
SHOW_TRACKERS_DIST=True
SHOW_TARGETS=True
SHOW_ACTIVE_TARGET=True
SHOW_ALL_CONNECTIONS=True
SHOW_ACTIVE_CONNECTIONS=True
IN_FRONT_MARGIN=10
FONT=cv2.FONT_HERSHEY_PLAIN 
origin=np.array([w//2,h-h//20])

cols=[
        ([120,0],'r'),
        ([100,100],'r'),
        ([200,250],'r'),
        ([-200,200],'g'),
        ([180,80],'b'),
        ([0,80],'b'),
        ([200,100],'b')
      ]
x=0
#while True:
#    cols=[
#            ([120,0],'r'),
#            ([100,100],'r'),
#            ([200,250],'r'),
#            ([-200,200],'g'),
#            ([180,80],'b'),
#            ([0,80],'b'),
#            ([200,x],'b')
#          ]
targets_by_name={}
def process(cols):
    global targets_by_name
    global img
    global targets_by_name
    img = np.zeros((h,w,3), np.uint8)
    #cv2.namedWindow('test', flags=cv2.WINDOW_GUI_NORMAL)
    cv2.setMouseCallback('test', handleMouse)
    targets=getTargets(cols)
    old_targets_by_name=targets_by_name
    targets_by_name=nameTargets(targets,old_targets_by_name)
    if SHOW_TARGETS:
        for target in targets:
            display(target[0],(255,0,255),marker_type='target',pointer=target[1])
            cv2.line(img,dvals(target[0]),dvals([0,0]), (200,90,90),1)
    active_target=findNearestTarget(targets)
    if SHOW_ACTIVE_TARGET:
        if active_target is not None:
            display(active_target[0],(0,255,255),marker_type='target',pointer=active_target[1])
    displayTargetNames(targets_by_name)
    display([0,0],(255,255,255),'robot')
    displayInFrontArea()
    cv2.imshow("test",img)
    #x+=1
    cv2.waitKey(50)

