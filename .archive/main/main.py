#!/usr/bin/env python

import cv2
import signal
import os

import numpy as np
import math
import time
import detection
import wnavs


from robolab_turtlebot import Turtlebot, detector

main_pid=os.getpid()
WINDOW = 'markers'
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]

    # Print the event
    print('{} bumper {}'.format(bumper, state))
    os.kill(main_pid,signal.SIGKILL)



def get_delta(bod,pc):
    x,y,w,h=bod
    r_mid = (round(x+w/2),round(y+h/2))

    dx = 0
    dy = 0
    dz = 0
    index = 0

    for i in range(-5,5):
        for j in range(-5,5):
            point = pc[r_mid[1]+i][r_mid[0]+j]
            if not np.isnan(point[0]) and not np.isnan(point[1]) and not np.isnan(point[2]):
                dx += point[0]
                dy += point[1]
                dz += point[2]

                index+=1

    if index>0:
        dx /=index
        dy /=index
        dz /=index

        return dx,dy,dz ,(round(x+w/2),round(y+h/2))
    else:
        return None, None, None, (None,None)




def main():

    turtle = Turtlebot(rgb=True, pc =True)
    cv2.namedWindow(WINDOW)
    turtle.register_bumper_event_cb(bumper_cb)

    while not turtle.is_shutting_down():
        # get point cloud
        rgb_img = turtle.get_rgb_image()
        pc = turtle.get_point_cloud()

        # wait for  to be ready
        if rgb_img is None or pc is None:
            continue

        #hsv = cv2.cvtColor(, cv2.COLOR_BGR2HSV)


        #print('update')
        rgb_masks=detection.makeMasks(rgb_img)
        contours=detection.getContours(rgb_masks)
        full_mask=cv2.bitwise_or(cv2.bitwise_or(rgb_masks['r'],rgb_masks['g']),rgb_masks['b'])
        masked_img = cv2.bitwise_and(rgb_img, rgb_img, mask = full_mask)
        pillars=detection.getContourBoxes(contours)
        detection.drawContours(masked_img,contours)
        detection.drawPillars(masked_img,pillars)

        #cv2.imshow(WINDOW,cv2.bitwise_and(,rgb_img,mask=rgb_masks['r']))
        #cv2.waitKey(1)


        #if masked_img is not None:
        #    cv2.drawMarker(img, (round(len([0])/2), round(len(rgb_img)/2)), color=[255, 255, 255], thickness=1, 
        #        markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
        #        markerSize=10)

        pillar_array=detection.getPillarArray(pillars,pc)
        #print(pillar_array)
        wnavs.process(pillar_array)

        if len(pillars['r'])>0 and len(pillars['b'])>0:
            dx_r,dy_r,dz_r , r = get_delta(pillars['r'][0],pc)
            dx_b,dy_b,dz_b, b = get_delta(pillars['b'][0],pc)

            if dx_r is None or dx_b is None:
                continue

            dx = (dx_r-dx_b)**2
            dy = (dy_r-dy_b)**2
            dz = (dz_r-dz_b)**2
            
            dff = dx+dy+dz

            #print(dx_r,dz_r)
            mid_x = dx_r+(dx_b-dx_r)/2
            mid_y = dy_r+(dy_b-dy_r)/2
            mid_z = dz_r+(dz_b-dz_r)/2
            
            p_x=mid_x+(dz_b-dz_r)
            p_y=mid_y
            p_z=mid_z-(dx_b-dx_r)



            #print(mid_x,mid_z)
            alfa = math.atan(mid_x/mid_z)
            

            if masked_img is not None:
                cv2.drawMarker(masked_img, (r[0],r[1]), color=[0, 0, 255], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

                cv2.drawMarker(masked_img, (b[0],b[1]), color=[255, 0, 0], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

            m = [round(r[0]+(b[0]-r[0])/2),round(r[1]+(b[1]-r[1])/2)]

            if masked_img is not None:
                cv2.drawMarker(masked_img, (m[0],m[1]), color=[0, 255, 255], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

            #print(alfa,mid_z)

            direction = -1 if m[0]-r[0]>0 else 1

            #if abs(alfa)<0.1 and mid_z>0.5:
            #    #print('moving')
            #    #turtle.cmd_velocity(linear=0.1)
            #    pass
            #elif abs(alfa)<0.1 and mid_z<=0.5:
            #    #print('turn')
            #    turtle.reset_odometry()
            #    #while abs(turtle.get_odometry()[2]-direction*math.pi/2)>0.1:
            #    #    turtle.cmd_velocity(angular=direction*0.3)
            #else:
            #    #print('rotating',-alfa*2)
            #    alfa=1
            #    turtle.cmd_velocity(angular=-alfa*2)
                #map(,hsv)

              # show 
        turtle.cmd_velocity(angular=0.1)
        if masked_img is not None:
            cv2.imshow(WINDOW, masked_img)
            cv2.waitKey(1)


if __name__ == '__main__':
    main()
