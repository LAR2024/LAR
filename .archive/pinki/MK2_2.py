import cv2
import signal
import os

import numpy as np
import math
import time

from robolab_turtlebot import Turtlebot, detector

from me import makeMasks

main_pid = os.getpid()
bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']


class Masks:
    def __init__(self, r_mask, g_mask, b_mask, c_mask, masked_img):
        self.r_mask = r_mask
        self.g_mask = g_mask
        self.b_mask = b_mask
        self.c_mask = c_mask
        self.masked_img = masked_img


class Contours:
    def __init__(self, contours_r, contours_g, contours_b):
        self.contours_r = contours_r
        self.contours_g = contours_g
        self.contours_b = contours_b


class Pole:
    def __init__(self, w, h, x, y, color=None, contours = None, alfa = None):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.alfa = alfa
        self.color = color
        self.contours = contours
        self.pos = ()
        self.ID = None



class Poles:
    def __init__(self):
        self.poles = []
        self.r_poles = []
        self.g_poles = []
        self.b_poles = []

    def append(self, pole):
        self.poles.append(pole)
        if pole.color == 'r':
            self.r_poles.append(pole)
        elif pole.color == 'g':
            self.g_poles.append(pole)
        elif pole.color == 'b':
            self.b_poles.append(pole)


class Control:
    def __init__(self):
        self.turtle = Turtlebot(rgb=True, pc=True)
        self.turtle.register_bumper_event_cb(self.bumper_cb)

    def get_r_alfa(self):
        while not self.turtle.is_shutting_down():
            image = self.turtle.get_rgb_image()
            pc = self.turtle.get_point_cloud()

            if image is None or pc is None:
                continue

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            masks = self.get_masks(hsv, image)

            contours = self.get_contours(masks)

            poles, img = self.get_poles(masks, contours)

            self.draw_mid(img)

            for r_pole in poles.r_poles:
                dx_r, dy_r, dz_r, r = self.get_delta(r_pole, pc)
                alfa = round(math.degrees(math.atan(dx_r / dz_r)),2)
                cv2.putText(img,str(alfa),(r_pole.x,r_pole.y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255), 1)

            for b_pole in poles.b_poles:
                dx_r, dy_r, dz_r, r = self.get_delta(b_pole, pc)
                alfa = round(math.degrees(math.atan(dx_r / dz_r)),2)
                cv2.putText(img,str(alfa),(b_pole.x,b_pole.y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0), 1)

            for g_pole in poles.g_poles:
                dx_r, dy_r, dz_r, r = self.get_delta(g_pole, pc)
                alfa = round(math.degrees(math.atan(dx_r / dz_r)),2)
                cv2.putText(img,str(alfa),(g_pole.x,g_pole.y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0), 1)

            if img is not None:
                cv2.imshow(WINDOW, img)
                cv2.waitKey(1)

    def new_main(self):
        while not self.turtle.is_shutting_down():
            image = self.turtle.get_rgb_image()
            pc = self.turtle.get_point_cloud()

            if image is None or pc is None:
                continue

            self.draw_rgb_cam(image)
            self.draw_pc_cam(pc)

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            masks, vision_image = self.get_masks(hsv, image)

            contours = self.get_contours(masks)

            poles = self.get_poles(contours,pc)

            self.draw_poles(vision_image,poles)

            self.draw_mid(vision_image)

            self.draw_masks(vision_image)

            blank_img = self.draw_topdown(poles,pc)

            Pairs = self.find_doubles(poles)

            self.draw_pairs(Pairs,blank_img)

            #self.draw_walls(pc)

            if len(Pairs)>0:
                best = []
                lowest = None
                for pair in Pairs:
                    pole1 = pair[0]
                    pole2 = pair[1]

                    x1, y1, z1 = pole1.pos
                    x2, y2, z2 = pole2.pos

                    mid_x = x1 + (x2 - x1) / 2
                    mid_y = y1 + (y2 - y1) / 2
                    mid_z = z1 + (z2 - z1) / 2

                    rng = (mid_x**2+mid_z**2)**0.5

                    if lowest is None:
                        lowest = rng
                        best = pair
                    else:
                        if lowest>rng:
                            lowest = rng
                            best = pair

                pole1 = best[0]
                pole2 = best[1]

                x1, y1, z1 = pole1.pos
                x2, y2, z2 = pole2.pos

                mid_x = x1 + (x2 - x1) / 2
                mid_y = y1 + (y2 - y1) / 2
                mid_z = z1 + (z2 - z1) / 2

                rng = (mid_x ** 2 + mid_z ** 2) ** 0.5

                """p_x = mid_x + (dz_b - dz_r)
                p_y = mid_y
                p_z = mid_z - (dx_b - dx_r)"""

                # print(mid_x,mid_z)
                alfa = math.atan(mid_x / mid_z)

                """m = [round(r[0] + (b[0] - r[0]) / 2), round(r[1] + (b[1] - r[1]) / 2)]
    
                if img is not None:
                    cv2.drawMarker(img, (m[0], m[1]), color=[0, 255, 255], thickness=1,
                                   markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                                   markerSize=10)
    
                # print(alfa,mid_z)"""

                print('alfa:',alfa,'mid_z:', mid_z)

                if pole1.color=='r' and pole1.pos[0]<pole2.pos[0]:
                    direction = 1
                else:
                    direction = -1

                if abs(alfa) < 0.1 and mid_z > 0.3:
                    print('moving')
                    self.turtle.cmd_velocity(linear=0.1)
                elif abs(alfa) < 0.1 and mid_z <= 0.3:
                    print('turn')
                    time.sleep(1)
                    self.turn_angle(direction*math.pi/3)
                elif abs(alfa)>0.1:
                    print('rotating', alfa)
                    direction2=-alfa/abs(alfa)
                    self.turtle.cmd_velocity(angular=direction2*0.1,linear=0.01)

                    # map(,hsv)

                    # show image




    def main(self):
        while not self.turtle.is_shutting_down():
            image = self.turtle.get_rgb_image()
            pc = self.turtle.get_point_cloud()

            if image is None or pc is None:
                continue

            self.draw_rgb_cam(image)
            self.draw_pc_cam(pc)

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            masks = self.get_masks(hsv, image)

            contours = self.get_contours(masks)

            poles, img = self.get_poles(masks, contours)



            self.draw_mid(img)

            if len(poles.r_poles) > 0 and len(poles.b_poles) > 0:
                dx_r, dy_r, dz_r, r = self.get_delta(poles.r_poles[0], pc)
                dx_b, dy_b, dz_b, b = self.get_delta(poles.b_poles[0], pc)

                if dx_r is None or dx_b is None:
                    continue

                dx = (dx_r - dx_b) ** 2
                dy = (dy_r - dy_b) ** 2
                dz = (dz_r - dz_b) ** 2

                dff = dx + dy + dz

                # print(dx_r,dz_r)
                mid_x = dx_r + (dx_b - dx_r) / 2
                mid_y = dy_r + (dy_b - dy_r) / 2
                mid_z = dz_r + (dz_b - dz_r) / 2

                p_x = mid_x + (dz_b - dz_r)
                p_y = mid_y
                p_z = mid_z - (dx_b - dx_r)

                # print(mid_x,mid_z)
                alfa = math.atan(mid_x / mid_z)

                if img is not None:
                    cv2.drawMarker(img, (r[0], r[1]), color=[0, 0, 255], thickness=1,
                                   markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                                   markerSize=10)

                    cv2.drawMarker(img, (b[0], b[1]), color=[255, 0, 0], thickness=1,
                                   markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                                   markerSize=10)

                m = [round(r[0] + (b[0] - r[0]) / 2), round(r[1] + (b[1] - r[1]) / 2)]

                if img is not None:
                    cv2.drawMarker(img, (m[0], m[1]), color=[0, 255, 255], thickness=1,
                                   markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                                   markerSize=10)

                # print(alfa,mid_z)

                direction = -1 if m[0] - r[0] > 0 else 1

                if abs(alfa) < 0.1 and mid_z > 0.5:
                    print('moving')
                    self.turtle.cmd_velocity(linear=0.1)
                elif abs(alfa) < 0.1 and mid_z <= 0.5:
                    print('in odometry')
                    alfa2 = math.atan(p_x / p_z)
                    self.turtle.reset_odometry()
                    while abs(self.turtle.get_odometry()[2] - alfa2) > 0.1:
                        print(self.turtle.get_odometry()[2] - alfa2)
                        self.turtle.cmd_velocity(angular=direction * 0.3)

                    while abs((self.turtle.get_odometry()[0] - p_x) ** 2 + (self.turtle.get_odometry()[1] - p_z) ** 2):
                        self.turtle.cmd_velocity(linear=0.1)

                    print('turn')
                    self.turtle.reset_odometry()
                    while abs(self.turtle.get_odometry()[2] - direction * math.pi / 2) > 0.1:
                        self.turtle.cmd_velocity(angular=direction * 0.3)
                else:
                    print('rotating', -alfa * 2)
                    self.turtle.cmd_velocity(angular=-alfa * 2)

                    # map(,hsv)

                    # show image
            if img is not None:
                cv2.imshow(WINDOW, img)
                cv2.waitKey(1)

    def draw_topdown(self,poles,pc):
        r_color = (0, 0, 255)
        g_color = (0, 255, 0)
        b_color = (255, 0, 0)

        w = 640
        h = 480
        f = 70

        blank_img = np.zeros((h, w, 3), dtype = np.uint8)
        cv2.drawMarker(blank_img, (int(w/2), int(h-10)), color=(255, 255, 255), thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.line(blank_img, (f, 0), (int(w/2), int(h-10)), (255,255,255), 1)
        cv2.line(blank_img, (w-f, 0), (int(w / 2), int(h-10)), (255, 255, 255), 1)
        cv2.line(blank_img, (int(w / 2), 0), (int(w / 2), int(h - 10)), (255, 255, 255), 1)

        for pole in poles.poles:
            dx_r, dy_r, dz_r, r = self.get_delta(pole, pc)
            if dx_r is None:
                continue

            x = int(round(w/2+dx_r*200))
            y = int(round(h-10-dz_r*200))


            if pole.color == 'r':
                color = r_color
            elif pole.color == 'g':
                color = g_color
            elif pole.color == 'b':
                color = b_color
            else:
                color = (255,255,0)


            cv2.drawMarker(blank_img, (x, y), color=color, thickness=1,
                           markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                           markerSize=10)

        """for x in range(len(pc[0])):
            p_x,p_y,p_z = pc[int((70/100)*h)][x]
            if not np.isnan(p_x) and not np.isnan(p_y) and not np.isnan(p_z):
                rx = int(round(w / 2 + p_x * 200))
                ry = int(round(h - 10 - p_z * 200))
                blank_img[ry][rx]=[128,128,128]
                #print(rx,ry)
            else:
                pass
                #print('NaN')"""


        """cv2.imshow('TOP_DOWN', blank_img)
        cv2.moveWindow('TOP_DOWN', 650, 550)
        cv2.waitKey(1)"""
        return blank_img

    def draw_walls(self, pc):
        w = 640
        h = 480
        blank_img = np.zeros((h, w, 3), dtype=np.uint8)
        #for y in range(len(pc)):
        for x in range(len(pc[0])):
            p_x,p_y,p_z = pc[int(3*h/4)][x]
            if not np.isnan(p_x) and not np.isnan(p_y) and not np.isnan(p_z):
                rx = int(round(w / 2 + p_x * 200))
                ry = int(round(h - 10 - p_z * 200))
                blank_img[ry][rx]=[255,0,0]
                print(rx,ry)
            else:
                print('NaN')



        cv2.imshow('walls', blank_img)
        cv2.moveWindow('walls', 2*640, 480)
        cv2.waitKey(1)


    def get_masks(self, hsv_img, image):
        """r_low = np.array([0, 130, 80])
        r_up = np.array([10, 255, 255])

        b_low = np.array([90, 130, 30])
        b_up = np.array([150, 255, 255])

        g_low = np.array([50, 130, 80])
        g_up = np.array([70, 255, 255])

        r_mask = cv2.inRange(hsv_img, r_low, r_up)
        b_mask = cv2.inRange(hsv_img, b_low, b_up)
        g_mask = cv2.inRange(hsv_img, g_low, g_up)"""

        rgb_masks = makeMasks(image)

        r_mask = rgb_masks['r']
        b_mask = rgb_masks['b']
        g_mask = rgb_masks['g']

        a_mask = cv2.bitwise_or(r_mask, b_mask)
        c_mask = cv2.bitwise_or(a_mask, g_mask)

        masked_img = cv2.bitwise_and(image, image, mask=c_mask)
        vision_image = cv2.bitwise_and(image, image, mask=c_mask)

        masks = Masks(r_mask, g_mask, b_mask, c_mask, masked_img)

        return masks, vision_image

    def get_contours(self, masks: Masks):
        contours_r, _ = cv2.findContours(masks.r_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_g, _ = cv2.findContours(masks.g_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_b, _ = cv2.findContours(masks.b_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours = Contours(contours_r, contours_g, contours_b)
        return contours

    def get_poles(self, contours,pc):
        ID = 0
        poles = Poles()
        for cnt in contours.contours_r:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h > 2000 and w * 3 < h and w * 9 > h:
                new_pole = Pole(w, h, x, y, 'r', cnt)
                dx, dy, dz, r = self.get_delta(new_pole, pc)
                new_pole.pos = (dx,dy,dz)
                new_pole.ID = ID
                ID+=1
                poles.append(new_pole)

        for cnt in contours.contours_g:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h > 3000 and w * 3 < h and w * 9 > h:
                new_pole = Pole(w, h, x, y, 'g', cnt)
                dx, dy, dz, r = self.get_delta(new_pole, pc)
                new_pole.pos = (dx, dy, dz)
                new_pole.ID = ID
                ID += 1
                poles.append(new_pole)

        for cnt in contours.contours_b:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h > 2000 and w * 2 < h and w * 10 > h:
                new_pole = Pole(w, h, x, y, 'b', cnt)
                dx, dy, dz, r = self.get_delta(new_pole, pc)
                new_pole.pos = (dx, dy, dz)
                new_pole.ID = ID
                ID += 1
                poles.append(new_pole)

        return poles

    def draw_poles(self,img, poles):
        r_color = (0, 0, 255)
        g_color = (0,255,0)
        b_color = (255,0,0)
        for pole in poles.poles:
            cv2.drawContours(img, [pole.contours], 0, (255, 255, 255), 2)
            if pole.color == 'r':
                color = r_color
            elif pole.color == 'g':
                color = g_color
            elif pole.color == 'b':
                color = b_color
            else:
                color = (255,255,0)
            cv2.rectangle(img, (pole.x, pole.y), (pole.x + pole.w, pole.y + pole.h), color, 2)

            cv2.drawMarker(img, (pole.x + round(pole.w/2), pole.y + round(pole.h/2)), color=color, thickness=1,
                           markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                           markerSize=10)

    def draw_rgb_cam(self,rgb_cam_image):
        cv2.imshow('RGB_CAM', rgb_cam_image)
        cv2.moveWindow('RGB_CAM', 0, 0)
        cv2.waitKey(1)

    def draw_pc_cam(self,pc_cam_image):
        cv2.imshow('PC_CAM', pc_cam_image)
        cv2.moveWindow('PC_CAM', 0, 550)
        cv2.waitKey(1)

    def draw_masks(self,masks_image):
        cv2.imshow('MASKS_CAM', masks_image)
        cv2.moveWindow('MASKS_CAM', 650, 0)
        cv2.waitKey(1)

    def draw_mid(self, img):
        if img is not None:
            cv2.drawMarker(img, (round(len(img[0]) / 2), round(len(img) / 2)), color=[255, 255, 255], thickness=1,
                           markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                           markerSize=10)

    def find_doubles(self,poles):
        Pairs = []
        for index1,pole1 in enumerate(poles.poles):
            for index2,pole2 in enumerate(poles.poles):
                if pole1.pos[0] is not None and pole2.pos[0] is not None:
                    if index1!=index2:
                        diff = ((pole1.pos[0]-pole2.pos[0])**2+(pole1.pos[1]-pole2.pos[1])**2+(pole1.pos[2]-pole2.pos[2])**2)**0.5
                        if diff<0.2 and ((pole1.color == 'r' and pole2.color == 'b') or (pole1.color == 'b' and pole2.color == 'r') or (pole1.color == 'g' and pole2.color == 'g') ):
                            if [pole1, pole2] not in Pairs and [pole2,pole1] not in Pairs:
                                Pairs.append([pole1, pole2])
                else:
                    print("err None in pole.pos")
        return Pairs

    def draw_pairs(self, pairs,blank_img):
        for pair in pairs:
            pole1= pair[0]
            pole2 = pair[1]

            w = 640
            h = 480

            x1 = int(round(w / 2 + pole1.pos[0] * 200))
            y1 = int(round(h - 10 - pole1.pos[2] * 200))

            x2 = int(round(w / 2 + pole2.pos[0] * 200))
            y2 = int(round(h - 10 - pole2.pos[2] * 200))

            mid_x = round(x1+(x2-x1)/2)
            mid_y = round(y1+(y2-y1)/2)

            cv2.drawMarker(blank_img, (mid_x,mid_y), color=[0, 255, 255], thickness=1,
                           markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                           markerSize=10)

            #print(x1,y1,x2,y2)

            cv2.line(blank_img, (x1,y1), (x2,y2), (0, 255, 255), 1)

        cv2.imshow('TOP_DOWN', blank_img)
        cv2.moveWindow('TOP_DOWN', 650, 550)
        cv2.waitKey(1)

    def turn_angle(self, angle):
        direction = angle / abs(angle)
        self.turtle.reset_odometry()
        while abs(self.turtle.get_odometry()[2] - angle) >= 0.01:
            #print(self.turtle.get_odometry()[2] - angle)
            self.turtle.cmd_velocity(angular=direction * 0.3)

    def move_dist(self, dist):
        direction = dist/abs(dist)
        self.turtle.reset_odometry()
        while abs(self.turtle.get_odometry()[0] - dist) >= 0.01:
            #print(self.turtle.get_odometry()[0] - dist)
            self.turtle.cmd_velocity(linear=0.1*direction)

    def bumper_cb(self, msg):
        """Bumber callback."""
        # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
        bumper = bumper_names[msg.bumper]

        # msg.state stores the event 0:RELEASED, 1:PRESSED
        state = state_names[msg.state]

        # Print the event
        print('{} bumper {}'.format(bumper, state))
        os.kill(main_pid, signal.SIGKILL)

    def get_delta(self,bod, pc):
        #x, y, w, h = bod
        x = bod.x
        y = bod.y
        w = bod.w
        h = bod.h

        r_mid = (round(x + w / 2), round(y + h / 2))

        dx = 0
        dy = 0
        dz = 0
        index = 0

        for i in range(-5, 5):
            for j in range(-5, 5):
                point = pc[r_mid[1] + i][r_mid[0] + j]
                if not np.isnan(point[0]) and not np.isnan(point[1]) and not np.isnan(point[2]):
                    dx += point[0]
                    dy += point[1]
                    dz += point[2]

                    index += 1

        if index > 0:
            dx /= index
            dy /= index
            dz /= index

            return dx, dy, dz, (round(x + w / 2), round(y + h / 2))
        else:
            return None, None, None, (None, None)


ROBOT = Control()
#ROBOT.new_main()
#ROBOT.get_r_alfa()

#ROBOT.turn_angle(math.pi/8)
#ROBOT.move_dist(-0.5)

ROBOT.new_main()


