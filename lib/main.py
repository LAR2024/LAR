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


random.main_pid = os.getpid()




class NewControl:
    def __init__(self):
        self.DRAW = True

        self.turtle = Turtlebot(rgb=True, pc=True)
        self.turtle.register_bumper_event_cb(random.bumper_cb)

    def main_loop(self):
        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()
            if image is not None and pc is not None:
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image,pc)

                if self.DRAW:
                    process_imgs.draw_poles(vision_image, poles)
                    process_imgs.draw_mid(vision_image)
                    blank_img = process_imgs.draw_topdown(poles, pc)
                    topdown = process_imgs.draw_pairs(pairs, blank_img)

                    random.draw_image('CAM-Image', image, (0,0))
                    random.draw_image('CAM-Point_Cloud', pc, (0,550))
                    random.draw_image('MASKS', vision_image, (650,0))
                    random.draw_image('TOPDOWN', topdown, (650,550))


    def get_turtle_images(self):
        image = self.turtle.get_rgb_image()
        pc = self.turtle.get_point_cloud()

        if image is not None and pc is not None:
            return image, pc
        else:
            return None, None









