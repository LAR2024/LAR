import cv2
import signal
import os
import numpy as np
import math
import time

from robolab_turtlebot import Turtlebot, detector


from lib import classes
from lib import process_imgs
from lib import random
from lib import draw_imgs


random.main_pid = os.getpid()

"""
    x: left to right from turtle    [m]
    y: back to front from turtle    [m]
    z: down to up from turtle       [m]

    fi: counter-clockwise           [rad]
"""


class NewControl:
    def __init__(self):
        self.DRAW = True

        self.turtle = Turtlebot(rgb=True, pc=True)
        self.turtle.register_bumper_event_cb(random.bumper_cb)
        self.turtle.wait_for_point_cloud()

    def main_loop(self):
        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()
            if image is not None and pc is not None:
                print("16:53")
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image,pc)


                if len(pairs) > 0:
                    target_pos = pairs[0].t_pos
                else:
                    target_pos = (0,0)

                if self.DRAW:
                    draw_imgs.draw_poles(vision_image, poles)
                    draw_imgs.draw_mid(vision_image)
                    topdown_img = draw_imgs.draw_topdown(poles, pc)
                    topdown_img = draw_imgs.draw_pairs(pairs, topdown_img, target_pos)

                    random.draw_image('CAM-Image', image, (0,0))
                    random.draw_image('CAM-Point_Cloud', pc, (0,550))
                    random.draw_image('MASKS', vision_image, (650,0))
                    random.draw_image('TOPDOWN', topdown_img, (650,550))




    def get_turtle_images(self):
        image = self.turtle.get_rgb_image()
        pc = self.turtle.get_point_cloud()

        # TODO: add check that pc is not NoneType: "np.isnan(var)"
        if image is not None and pc is not None:
            return image, pc
        else:
            return None, None

    def move2xyf(self, x,y,gamma):
        fi = math.atan2(y,x) - math.pi/2
        dist = math.sqrt(pow(x,2)+pow(y,2))

        self.rotate(fi)
        self.move(dist)
        self.rotate(-fi+gamma)


    def get_odometry(self):
        a,b,gamma = self.turtle.get_odometry()

        x = -b
        y = a
        fi = gamma
        return x,y,fi



    def rotate(self, pl_fi):
        self.turtle.reset_odometry()
        fi = pl_fi
        while abs(fi)>0.01:
            od_x, od_y, od_fi = self.get_odometry()

            fi = pl_fi-od_fi
            print(fi)
            direction = fi / abs(fi)
            self.turtle.cmd_velocity(angular=direction * 0.3)
        self.turtle.cmd_velocity(angular=0)
        time.sleep(1)


    def move(self, pl_dist):
        self.turtle.reset_odometry()
        dist = pl_dist
        while abs(dist)>0.01:
            od_x, od_y, od_fi = self.get_odometry()

            od_dist = math.sqrt(pow(od_x,2)+pow(od_y,2))

            dist = pl_dist - od_dist
            print(dist)
            direction = dist / abs(dist)
            self.turtle.cmd_velocity(linear=direction * 0.1)
        self.turtle.cmd_velocity(linear=0)
        time.sleep(1)