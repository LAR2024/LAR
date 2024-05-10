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

    def avrg_pairs(self):
        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()

            number_of_samples = 0
            sum_w1 = 0
            sum_h1 = 0
            sum_x1 = 0
            sum_y1 = 0

            sum_w2 = 0
            sum_h2 = 0
            sum_x2 = 0
            sum_y2 = 0

            if image is not None and pc is not None:
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image, pc)

                if pairs != []:
                    pair = pairs[0]

                    if number_of_samples != 0:
                        if abs(pair.pole_1.pos.x - sum_x1/number_of_samples) <= abs(pair.pole_1.pos.x - sum_x2/number_of_samples):
                            pole1 = pair.pole_1
                            pole2 = pair.pole_2
                        else:
                            pole1 = pair.pole_2
                            pole2 = pair.pole_1
                    else:
                        pole1 = pair.pole_1
                        pole2 = pair.pole_2



                    sum_w1 += pole1.mask_pos.w
                    sum_h1 += pole1.mask_pos.h
                    sum_x1 += pole1.mask_pos.x
                    sum_y1 += pole1.mask_pos.y

                    sum_w2 += pole2.mask_pos.w
                    sum_h2 += pole2.mask_pos.h
                    sum_x2 += pole2.mask_pos.x
                    sum_y2 += pole2.mask_pos.y

                    number_of_samples += 1

                    w1 = sum_w1 / number_of_samples
                    h1 = sum_h1 / number_of_samples
                    x1 = sum_x1 / number_of_samples
                    y1 = sum_y1 / number_of_samples

                    w2 = sum_w2 / number_of_samples
                    h2 = sum_h2 / number_of_samples
                    x2 = sum_x2 / number_of_samples
                    y2 = sum_y2 / number_of_samples

                    pole_1 = classes.Pole(w1, h1, x1, y1, pole1.color, None, pc)
                    pole_2 = classes.Pole(w2, h2, x2, y2, pole2.color, None, pc)

                    NewPair = classes.Pair(pole_1, pole_2)

                    target_pos_x = NewPair.help.local.x
                    target_pos_y = NewPair.help.local.y

                    return NewPair


    def main_loop(self):
        last_last_pairs = []
        last_pairs = []
        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()

            number_of_samples = 0
            sum_w1 = 0
            sum_h1 = 0
            sum_x1 = 0
            sum_y1 = 0

            sum_w2 = 0
            sum_h2 = 0
            sum_x2 = 0
            sum_y2 = 0

            if image is not None and pc is not None:
                print("15:37")
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image,pc)

                if pairs != []:
                    pair = pairs[0]

                    pole1 = pair.pole_1
                    pole2 = pair.pole_2

                    sum_w1 += pole1.mask_pos.w
                    sum_h1 += pole1.mask_pos.h
                    sum_x1 += pole1.mask_pos.x
                    sum_y1 += pole1.mask_pos.y

                    sum_w2 += pole2.mask_pos.w
                    sum_h2 += pole2.mask_pos.h
                    sum_x2 += pole2.mask_pos.x
                    sum_y2 += pole2.mask_pos.y

                    number_of_samples += 1



                    w1 = sum_w1 / number_of_samples
                    h1 = sum_h1 / number_of_samples
                    x1 = sum_x1 / number_of_samples
                    y1 = sum_y1 / number_of_samples

                    w2 = sum_w2 / number_of_samples
                    h2 = sum_h2 / number_of_samples
                    x2 = sum_x2 / number_of_samples
                    y2 = sum_y2 / number_of_samples



                    pole_1 = classes.Pole(w1, h1, x1, y1, pole1.color, None, pc)
                    pole_2 = classes.Pole(w2, h2, x2, y2, pole2.color, None, pc)

                    NewPair = classes.Pair(pole_1,pole_2)



                    target_pos_x = NewPair.help.local.x
                    target_pos_y = NewPair.help.local.y


                    print(target_pos_x,target_pos_y)
                    #self.move2xyf(target_pos_x,target_pos_y, 0)
                    pass

                if self.DRAW and pairs != [] :
                    draw_imgs.draw_poles(vision_image, poles)
                    draw_imgs.draw_mid(vision_image)
                    topdown_img = draw_imgs.draw_topdown(poles, pc)
                    if len(pairs) > 0:
                        topdown_img = draw_imgs.draw_pairs(pairs, topdown_img, NewPair.help.topdown.pos)

                    random.draw_image('CAM-Image', image, (0,0))
                    random.draw_image('CAM-Point_Cloud', pc, (0,550))
                    random.draw_image('MASKS', vision_image, (650,0))
                    random.draw_image('TOPDOWN', topdown_img, (650,550))

                last_last_pairs = last_pairs
                last_pairs = pairs

    def start(self):
        pairs_turns = []

        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()

            if image is not None and pc is not None:
                print("15:20")
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image,pc)

                if len(pairs)>0:
                    for pair in pairs:
                        print((pair.mid.local.x) ** 2 + (pair.mid.local.y) ** 2)


                pairs_turns.append(pairs)

                self.rotate(math.radians(45))

            if len(pairs_turns)>=8:
                break

        print("start turn")

        close_dist = None
        close_pair = None
        close_index = 0

        for index, pairs in enumerate(pairs_turns):
            for pair in pairs:
                new_dist = (pair.mid.local.x) ** 2 + (pair.mid.local.y) ** 2

                if close_dist is None:
                    close_dist = new_dist
                    close_pair = pair
                    close_index = index

                elif new_dist<close_dist:
                    close_dist = new_dist
                    close_pair = pair
                    close_index = index

        print(close_index)
        self.rotate(math.radians(45)*close_index)


    def get_nearest_pair(self):
        image, pc = self.get_turtle_images()

        pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image, pc)


        if len(pairs) > 0:
            close_dist = None
            close_pair = None

            for pair in pairs:
                new_dist = pair.mid.local.x ** 2 + pair.mid.local.y ** 2

                if close_dist is None:
                    close_dist = new_dist
                    close_pair = pair

                elif new_dist < close_dist:
                    close_dist = new_dist
                    close_pair = pair

            self.draw(pairs, poles, vision_image, image, pc, close_pair.mid.topdown.pos)
            return close_pair
        else:
            self.draw(pairs, poles, vision_image, image, pc, (0, 0))
            return None


    def find_nearest_pair(self):
        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()

            if image is not None and pc is not None:
                close_pair = self.get_nearest_pair(image, pc)

                print(close_pair.mid.local.y, close_pair.mid.local.x)
                fi = math.atan2(close_pair.mid.local.y, close_pair.mid.local.x) - math.pi/2

                print(fi)
                self.rotate(fi)

    def move_to_nearest_pair(self):

        Help = False
        Park = False
        Turn = 0
        while not self.turtle.is_shutting_down():
            close_pair = self.get_nearest_pair()
            print('RUN')

            if Help and Park:
                print('End')
                time.sleep(1)

                if Turn == 0:
                    print('Turn = 0')
                    break
                else:
                    Turn = 0

                self.move(-0.1)
                self.rotate(Turn*math.pi/2)
                self.move(0.1)

                Help = False
                Park = False



            if close_pair is None:
                continue

            if close_pair.pole_1.pos.x < close_pair.pole_2.pos.x:
                if close_pair.pole_1.color == 'r':
                    Turn = 1
                elif close_pair.pole_1.color == 'b':
                    Turn = -1
                else:
                    Turn = 0
            else:
                if close_pair.pole_2.color == 'r':
                    Turn = 1
                elif close_pair.pole_2.color == 'b':
                    Turn = -1
                else:
                    Turn = 0


            if not Help and not Park:
                x = close_pair.help.local.x
                y = close_pair.help.local.y

                fi = math.atan2(close_pair.park.local.y-y, close_pair.park.local.x-x) - math.pi/2

                print('move to help and rotate to park')
                print(x,y,fi)

                self.move2xyf(x, y, fi)
                print('end of move to help')
                Help = True

            elif Help and not Park:
                x = close_pair.park.local.x
                y = close_pair.park.local.y

                fi = math.atan2(close_pair.mid.local.y - y, close_pair.mid.local.x - x) - math.pi / 2

                print('move to park and rotate to mid')
                print(x, y, fi)

                self.move2xyf(x, y, fi)
                print('end of move to park')
                Park = True





    def draw(self, pairs, poles, vision_image, image, pc, pos):
        if self.DRAW:
            draw_imgs.draw_poles(vision_image, poles)
            draw_imgs.draw_mid(vision_image)
            topdown_img = draw_imgs.draw_topdown(poles, pc)
            if len(pairs) > 0:
                topdown_img = draw_imgs.draw_pairs(pairs, topdown_img, pos)

            random.draw_image('CAM-Image', image, (0, 0))
            random.draw_image('CAM-Point_Cloud', pc, (0, 550))
            random.draw_image('MASKS', vision_image, (650, 0))
            random.draw_image('TOPDOWN', topdown_img, (650, 550))

    def update_imgs(self):
        image, pc = self.get_turtle_images()
        if image is not None and pc is not None:
            pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image,pc)

            if self.DRAW:
                draw_imgs.draw_poles(vision_image, poles)
                draw_imgs.draw_mid(vision_image)
                topdown_img = draw_imgs.draw_topdown(poles, pc)

                topdown_img = draw_imgs.draw_pairs(pairs, topdown_img, (0,0))

                random.draw_image('CAM-Image', image, (0,0))
                random.draw_image('CAM-Point_Cloud', pc, (0,550))
                random.draw_image('MASKS', vision_image, (650,0))
                random.draw_image('TOPDOWN', topdown_img, (650,550))

    def get_turtle_images(self):
        image = self.turtle.get_rgb_image()
        pc = self.turtle.get_point_cloud()

        # TODO: add check that pc is not NoneType: "np.isnan(var)"
        if image is not None and not np.isnan(pc[0][0][0]):
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
            #print(fi)
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

            if pl_dist>0:
                dist = pl_dist - od_dist
            else:
                dist = pl_dist + od_dist
            direction = dist / abs(dist)

            #print(dist,direction)
            self.turtle.cmd_velocity(linear=direction * 0.1)
        self.turtle.cmd_velocity(linear=0)
        time.sleep(1)