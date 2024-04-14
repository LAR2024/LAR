#!/usr/bin/env python

import cv2
import signal
import os

import numpy as np
import math
import time


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

def cceck(hsv,image,x,y):
    h=hsv[0]
    s = hsv[1]
    v = hsv[2]

    r_trsh=10
    g_trsh=10
    b_trsh=30

    red_ref = [0,130,80]
    blue_ref = [120,80,80]
    green_ref = [60,80,80]
    
    if (abs(h-red_ref[0]) <r_trsh and s>red_ref[1] and v>red_ref[2]):
        image[y][x] = [0,0,255]
    elif (abs(h-green_ref[0]) <g_trsh and s>green_ref[1] and v>green_ref[2]):
        image[y][x] = [0,255,0]
    elif (abs(h-blue_ref[0]) <b_trsh and s>blue_ref[1] and v>blue_ref[2]):
        image[y][x] = [255,0,0]
    else:
        image[y][x] = [0,0,0]


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
        image = turtle.get_rgb_image()
        pc = turtle.get_point_cloud()

        # wait for image to be ready
        if image is None or pc is None:
            continue

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


        print('update')
        """for y in range(len(image)):
            for x in range(len(image[0])):
                cceck(hsv[y][x],image,x,y)"""

        r_low = np.array([0,130,80])
        r_up = np.array([10,255,255])

        b_low = np.array([90,130,80])
        b_up = np.array([150,255,255])

        g_low = np.array([50,130,80])
        g_up = np.array([70,255,255])

        r_mask = cv2.inRange(hsv, r_low, r_up)
        b_mask = cv2.inRange(hsv, b_low, b_up)
        g_mask = cv2.inRange(hsv, g_low, g_up)

        a_mask = cv2.bitwise_or(r_mask,b_mask)
        c_mask = cv2.bitwise_or(a_mask,g_mask)

        masked_img = cv2.bitwise_and(image, image, mask = c_mask)
       


        contours_r, _ = cv2.findContours(r_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours_g, _ = cv2.findContours(g_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours_b, _ = cv2.findContours(b_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        r_slp = []
        g_slp = []
        b_slp = []

        img = None


        for cnt in contours_r:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>3000 and w*3<h and w*9>h:
                r_slp.append((x,y,w,h))
                img = cv2.drawContours(masked_img,[cnt],0,(255,255,255),2)""for y in range(len(image)):
            for x in range(len(image[0])):
                cceck(hsv[y][x],image,x,y)

        """r_low = np.array([0,130,80])
        r_up = np.array([10,255,255])

        b_low = np.array([90,130,80])
        b_up = np.array([150,255,255])

        g_low = np.array([50,130,80])
        g_up = np.array([70,255,255])

        rgb_masks['r'] = cv2.inRange(hsv, r_low, r_up)
        rgb_masks['b'] = cv2.inRange(hsv, b_low, b_up)
    (rgb_masks['g'] = cv2.inRange(hsv, g_low, g_up)
        """
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>3000 and w*3<h and w*9>h:
                g_slp.append((x,y,w,h))
                img = cv2.drawContours(masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masked_img,(x,y),(x+w,y+h),(0,255,0),2)

        for cnt in contours_b:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>3000 and w*3<h and w*9>h:
                b_slp.append((x,y,w,h))
                img = cv2.drawContours(masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masked_img,(x,y),(x+w,y+h),(255,0,0),2)

        if img is not None:
            cv2.drawMarker(img, (round(len(image[0])/2), round(len(image)/2)), color=[255, 255, 255], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

        if len(r_slp)>0 and len(b_slp)>0:
            dx_r,dy_r,dz_r , r = get_delta(r_slp[0],pc)
            dx_b,dy_b,dz_b, b = get_delta(b_slp[0],pc)

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
            

            if img is not None:
                cv2.drawMarker(img, (r[0],r[1]), color=[0, 0, 255], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

                cv2.drawMarker(img, (b[0],b[1]), color=[255, 0, 0], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

            m = [round(r[0]+(b[0]-r[0])/2),round(r[1]+(b[1]-r[1])/2)]

            if img is not None:
                cv2.drawMarker(img, (m[0],m[1]), color=[0, 255, 255], thickness=1, 
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

            #print(alfa,mid_z)

            direction = -1 if m[0]-r[0]>0 else 1

            if abs(alfa)<0.1 and mid_z>0.5:
                print('moving')
                turtle.cmd_velocity(linear=0.1)
            elif abs(alfa)<0.1 and mid_z<=0.5:
                print('in odometry')
                alfa2 = math.atan(p_x/p_z)
                turtle.reset_odometry()
                while abs(turtle.get_odometry()[2]-alfa2)>0.1:
                    print(turtle.get_odometry()[2]-alfa2)
                    turtle.cmd_velocity(angular=direction*0.3)

                while abs((turtle.get_odometry()[0]-p_x)**2+(turtle.get_odometry()[1]-p_z)**2):
                    turtle.cmd_velocity(linear=0.1)

                print('turn')
                turtle.reset_odometry()
                while abs(turtle.get_odometry()[2]-direction*math.pi/2)>0.1:
                    turtle.cmd_velocity(angular=direction*0.3)
            else:
                print('rotating',-alfa*2)
                turtle.cmd_velocity(angular=-alfa*2)

                #map(,hsv)

                # show image
        if img is not None:
            cv2.imshow(WINDOW, img)
            cv2.waitKey(1)


if __name__ == '__main__':
    main()
