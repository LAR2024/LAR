
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


class Masks:
    def __init__(self, r_mask,g_mask,b_mask, c_mask, masked_img):
        self.r_mask = r_mask
        self.g_mask = g_mask
        self.b_mask = b_mask
        self.c_mask = c_mask
        self.masked_img = masked_img

class Contours:
    def __init__(self, contours_r,contours_g,contours_b):
        self.contours_r = contours_r
        self.contours_g = contours_g
        self.contours_b = contours_b

class Pole:
    def __init__(self,w,h,x,y,color=None):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.color = color

class Poles:
    def __init__(self):
        self.r_poles = []
        self.g_poles = []
        self.b_poles = []
    
    def append(self,pole):
        if pole.color == 'r':
            self.r_poles.append(pole)
        elif pole.color == 'g':
            self.g_poles.append(pole)
        elif pole.color == 'b':
            self.b_poles.append(pole)



class Control:
    def __init__(self):
        self.turtle = Turtlebot(rgb=True, pc=True)
        cv2.namedWindow(WINDOW)
        self.turtle.register_bumper_event_cb(self.bumper_cb)

        

    def main(self):
        while not self.turtle.is_shutting_down():
            image = self.turtle.get_rgb_image()
            pc = self.turtle.get_point_cloud()

            if image is None or pc is None:
                continue

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            masks = self.get_masks(hsv, image)

            contours = self.get_contours(masks)

            poles, img = self.get_poles(masks,contours)

            self.show(img)






            if len(poles.r_poles)>0 and len(poles.b_poles)>0:
                pass


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


    def get_masks(self, hsv_img, image):
        r_low = np.array([0,130,80])
        r_up = np.array([10,255,255])

        b_low = np.array([90,130,30])
        b_up = np.array([150,255,255])

        g_low = np.array([50,130,80])
        g_up = np.array([70,255,255])

        r_mask = cv2.inRange(hsv_img, r_low, r_up)
        b_mask = cv2.inRange(hsv_img, b_low, b_up)
        g_mask = cv2.inRange(hsv_img, g_low, g_up)

        a_mask = cv2.bitwise_or(r_mask,b_mask)
        c_mask = cv2.bitwise_or(a_mask,g_mask)

        masked_img = cv2.bitwise_and(image, image, mask = c_mask)

        masks = Masks(r_mask,g_mask,b_mask,c_mask,masked_img)

        return masks

    def get_contours(self, masks: Masks):
        contours_r, _ = cv2.findContours(masks.r_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours_g, _ = cv2.findContours(masks.g_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours_b, _ = cv2.findContours(masks.b_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        contours = Contours(contours_r,contours_g,contours_b)
        return contours

    def get_poles(self, masks, contours):
        img = None
        poles = Poles()
        for cnt in contours.contours_r:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>3000 and w*3<h and w*9>h:
                new_pole = Pole(w,h,x,y,'r')
                poles.append(new_pole)
                img = cv2.drawContours(masks.masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masks.masked_img,(x,y),(x+w,y+h),(0,0,255),2)

        for cnt in contours.contours_g:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>3000 and w*3<h and w*9>h:
                new_pole = Pole(w,h,x,y,'g')
                poles.append(new_pole)
                img = cv2.drawContours(masks.masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masks.masked_img,(x,y),(x+w,y+h),(0,255,0),2)

        for cnt in contours.contours_b:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>2000 and w*2<h and w*10>h:
                new_pole = Pole(w,h,x,y,'b')
                poles.append(new_pole)
                img = cv2.drawContours(masks.masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masks.masked_img,(x,y),(x+w,y+h),(255,0,0),2)
        
        return poles, img

    def show(self, img):
        if img is not None:
            cv2.drawMarker(img, (round(len(img[0])/2), round(len(img)/2)), color=[255, 255, 255], thickness=1,
                markerType= cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                markerSize=10)

    def turn_angle(self,angle):
        direction = angle/abs(angle)
        self.turtle.reset_odometry()
        while abs(self.turtle.get_odometry()[2]-angle)>0.01:
            print(self.turtle.get_odometry()[2]-angle)
            self.turtle.cmd_velocity(angular=direction*0.3)

    def move_dist(self,dist):
        self.turtle.reset_odometry()
        while self.turtle.get_odometry()[0]-
            self.turtle.cmd_velocity(linear=0.1)
        

    def bumper_cb(self, msg):
        """Bumber callback."""
        # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
        bumper = bumper_names[msg.bumper]

        # msg.state stores the event 0:RELEASED, 1:PRESSED
        state = state_names[msg.state]

        # Print the event
        print('{} bumper {}'.format(bumper, state))
        os.kill(main_pid,signal.SIGKILL)









#----------------------------------------------------------------------------------------------

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

        
       
        r_low = np.array([0,130,80])
        r_up = np.array([10,255,255])

        b_low = np.array([90,130,30])
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
                img = cv2.drawContours(masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masked_img,(x,y),(x+w,y+h),(0,0,255),2)

        for cnt in contours_g:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>3000 and w*3<h and w*9>h:
                g_slp.append((x,y,w,h))
                img = cv2.drawContours(masked_img,[cnt],0,(255,255,255),2)
                img = cv2.rectangle(masked_img,(x,y),(x+w,y+h),(0,255,0),2)

        for cnt in contours_b:
            x,y,w,h = cv2.boundingRect(cnt)
            if w*h>2000 and w*2<h and w*10>h:
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
