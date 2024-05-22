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

PRESSED = False

def button(data):
    global PRESSED
    PRESSED = True
    print("PRESSED")
    print(data)



class NewControl:
    def __init__(self):
        self.DRAW = True

        self.turtle = Turtlebot(rgb=True, pc=True)
        self.turtle.register_bumper_event_cb(random.bumper_cb)
        self.turtle.register_button_event_cb(button)
        self.turtle.wait_for_point_cloud()

    def start_turn(self):
        """ turns around and finds closest pair, than rotates to it

        :return:
        """

        while not PRESSED:
            print("wait for button")
            time.sleep(0.1)
            pass

        best_pair = None
        best_distance = None
        best_angle = None

        self.turtle.reset_odometry()
        angle = 2*math.pi

        fi = angle

        actual_angle = 0
        while abs(actual_angle-2*math.pi) > 0.3:
            image, pc = self.get_turtle_images(no_wait = True)

            if image is not None and pc is not None:
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image, pc)
                self.draw(pairs, poles, vision_image, image, pc, (0, 0))

                if len(pairs) > 0:
                    for pair in pairs:
                        distance = (pair.mid.local.x**2 + pair.mid.local.y**2)**(1/2)
                        if best_distance is None:
                            best_distance = distance
                            best_pair = pair
                            best_angle = actual_angle

                        if distance < best_distance:
                            best_distance = distance
                            best_pair = pair
                            best_angle = actual_angle

            od_x, od_y, od_fi = self.get_odometry()

            fi = angle - od_fi

            if od_fi > 0:
                if actual_angle > od_fi and od_fi<-2:
                    actual_angle = od_fi + 2*math.pi
                else:
                    actual_angle = od_fi
            elif od_fi < 0 and actual_angle != 0:
                actual_angle = math.pi + math.pi - abs(od_fi)
            print(actual_angle, od_fi, fi)
            direction = fi / abs(fi)
            print(direction)
            self.turtle.cmd_velocity(angular=direction * 0.3)

        self.turtle.cmd_velocity(angular=0)

        self.new_rotate(best_angle)

    def get_nearest_pair(self):
        """ finds closest pair in vision and returns Pair object of it

        :return:
        """
        image, pc = self.get_turtle_images()

        if image is not None and pc is not None:
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
        else:
            return None

    def rotate_to_nearest_pair(self):
        """ rotates to nearest pair in vision

        :return:
        """
        retry = 0
        while not self.turtle.is_shutting_down():
            image, pc = self.get_turtle_images()

            if image is not None and pc is not None:
                close_pair = self.get_nearest_pair()

                if close_pair is not None:

                    print(close_pair.mid.local.y, close_pair.mid.local.x)
                    fi = math.atan2(close_pair.mid.local.y, close_pair.mid.local.x) - math.pi/2

                    print(fi)
                    self.new_rotate(fi)
                    break
                else:
                    retry += 1

            if retry>5:
                break

    def move_to_nearest_pair(self):

        Found = False
        Help = False
        Park = False
        Turn = 0
        retries = 0
        retries_try = 0
        while not self.turtle.is_shutting_down():
            close_pair = self.get_nearest_pair()
            print('RUN')

            if Help and Park:
                print('End')
                time.sleep(1)

                if Turn == 0:
                    print('Turn = 0')
                    self.turtle.play_sound()
                    time.sleep(0.3)
                    self.turtle.play_sound(1)
                    time.sleep(0.3)
                    self.turtle.play_sound(2)
                    time.sleep(0.3)
                    self.turtle.play_sound(3)
                    time.sleep(0.3)
                    self.turtle.play_sound(4)
                    time.sleep(0.3)
                    self.turtle.play_sound(5)
                    time.sleep(0.3)
                    self.turtle.play_sound(6)
                    time.sleep(1)

                    break
                else:
                    print("rotate after move")
                    self.new_move(-0.1, True)
                    self.new_rotate(Turn * math.pi / 2, True)
                    self.new_move(0.2, True)

                    Turn = 0

                Found = False
                Help = False
                Park = False



            if close_pair is None:
                print("no close pair")
                if retries >= 10 and retries_try == 0 and Help is False and Park is False:
                    print("find right")
                    self.new_rotate(-math.pi/4)
                    retries = 0
                    retries_try = 1
                elif retries >= 10 and retries_try == 1 and Help is False and Park is False:
                    print("find left")
                    self.new_rotate(math.pi/2)
                    retries = 0
                    retries_try = 0
                elif Help is False and Park is False:
                    print("found nothing")
                    retries += 1

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

            print('Turn:',Turn)

            if not Found and not Help and not Park:
                self.rotate_to_nearest_pair()
                Found = True
            elif not Help and not Park:
                x = close_pair.help.local.x
                y = close_pair.help.local.y

                fi = math.atan2(close_pair.park.local.y-y, close_pair.park.local.x-x) - math.pi/2

                print('move to help and rotate to park')
                print(x,y,fi)

                self.move2xyf(x, y, fi, True)
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

    def eco_draw(self, image, pc):
        draw_imgs.draw_mid(image)
        random.draw_image('CAM-Image', image, (0, 0))
        random.draw_image('CAM-Point_Cloud', pc, (0, 550))

    def draw(self, pairs, poles, vision_image, image, pc, pos):
        if self.DRAW:
            draw_imgs.draw_mid(image)
            draw_imgs.draw_poles(vision_image, poles)
            draw_imgs.draw_mid(vision_image)
            topdown_img = draw_imgs.draw_topdown(poles, pc)
            if len(pairs) > 0:
                topdown_img = draw_imgs.draw_pairs(pairs, topdown_img, pos)

            random.draw_image('CAM-Image', image, (0, 0))
            random.draw_image('CAM-Point_Cloud', pc, (0, 550))
            random.draw_image('MASKS', vision_image, (650, 0))
            random.draw_image('TOPDOWN', topdown_img, (650, 550))

    def update_imgs(self, eco = False):
        image, pc = self.get_turtle_images()
        if image is not None and pc is not None:
            if not eco:
                pairs, poles, vision_image = process_imgs.get_pairs_from_cams(image, pc)
                self.draw(pairs, poles, vision_image, image, pc, (0, 0))
            else:
                self.eco_draw(image, pc)
        else:
            print("image is none and pc is none")

    def get_turtle_images(self, no_wait = False):
        print("imgs update")
        image = self.turtle.get_rgb_image()

        pc = self.turtle.get_point_cloud()

        if not no_wait:
            self.turtle.wait_for_rgb_image()
            self.turtle.wait_for_point_cloud()

        if image is not None and not np.isnan(pc).all() :
            return image, pc
        else:
            return None, None

    def move2xyf(self, x,y,gamma, speed_up=False):
        fi = math.atan2(y,x) - math.pi/2
        dist = math.sqrt(pow(x,2)+pow(y,2))

        self.new_rotate(fi)
        self.new_move(dist, speed_up)
        self.new_rotate(-fi+gamma)

    def get_odometry(self):
        a, b, gamma = self.turtle.get_odometry()

        x = -b
        y = a
        fi = gamma

        return x, y, fi

    def new_rotate(self, angle, speed_up=False):
        if angle > 2 * math.pi:
            raise ValueError('Angle bigger than 2pi')
        elif angle == math.pi:
            angle -= 0.01
            #raise ValueError('Angle is pi')

        # TODO: solve rotation for pi

        if speed_up:
            speed = 0.5
            tolerance = 0.03
        else:
            speed = 0.3
            tolerance = 0.01

        self.turtle.reset_odometry()

        if angle > math.pi:
            angle = -math.pi + (angle - math.pi)
        elif angle < -math.pi:
            angle = math.pi + (angle + math.pi)

        fi_err = angle

        while abs(fi_err) > tolerance:
            od_x, od_y, od_fi = self.get_odometry()
            od_angle = od_fi

            fi_err = angle - od_angle

            direction = fi_err / abs(fi_err)

            self.turtle.cmd_velocity(angular=direction * speed)

        if not speed_up:
            self.turtle.cmd_velocity(angular=0)
            time.sleep(1)

    def new_move(self, distance, speed_up=False):
        if abs(distance) < 0.5 and speed_up is True:
            speed_up = False

        if speed_up:
            tolerance = 0.03
        else:
            tolerance = 0.01

        self.turtle.reset_odometry()

        dist_err = distance

        while abs(dist_err) > tolerance:
            od_x, od_y, od_fi = self.get_odometry()
            od_distance = od_y

            dist_err = distance - od_distance

            direction = dist_err / abs(dist_err)

            speed_up_time = 0.3
            slow_down_time = 0.3
            fast_speed = 0.5
            slow_speed = 0.1

            actual_speed = slow_speed
            if speed_up:
                if dist_err > (1-speed_up_time) * distance:
                    actual_speed = ((1 - dist_err / distance) / speed_up_time) * (fast_speed - slow_speed) + slow_speed
                elif dist_err > slow_down_time * distance:
                    actual_speed = fast_speed
                elif dist_err > 0:
                    actual_speed = fast_speed - (fast_speed-slow_speed) * (1 - (dist_err / distance) / slow_down_time)
            else:
                actual_speed = slow_speed
            self.turtle.cmd_velocity(linear=direction * actual_speed)

        if not speed_up:
            self.turtle.cmd_velocity(linear=0)
            time.sleep(1)

