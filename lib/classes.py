import numpy as np






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


class PoleMaskSize:
    def __init__(self,w,h,x,y):
        self.w = w
        self.h = h
        self.x = x  # on img left to right
        self.y = y  # on img up to down

        self.middle_x = self.x + round(self.w/2)
        self.middle_y = self.y + round(self.h/2)

        self.pos = (self.x, self.y) # position of left up corner of pole
        self.pos2 = (self.x + self.w, self.y + self.h)  # position of right down corner of pole


class PoleTopdownPos:
    def __init__(self, pc_pos):
        WIDTH = 640
        HEIGHT = 480

        self.x = int(round(WIDTH/2+pc_pos.x*200))   # on img from left to right
        self.y = int(round(HEIGHT- pc_pos.y*200))   # on img from top to down
        self.pos = (self.x, self.y)


class PolePCPos:
    def __init__(self, masked_pos, pc):
        self.x = None   # left to right from turtle
        self.y = None   # back to front from turtle
        self.z = None   # down to up from turtle

        self.pos = (self.x, self.y, self.z)

        (a,b) =self.__get_delta(masked_pos, pc)

    def __get_delta(self, bod, pc):
        # x, y, w, h = bod
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


            self.__pc_xyz_to_xyz(dx,dy,dz)

            return (round(x + w / 2), round(y + h / 2))
        else:
            return (None, None)

    def __pc_xyz_to_xyz(self, x,y,z):
        self.x = x
        self.y = z
        self.z = -y

        self.pos = (self.x, self.y, self.z)


class PolePos:
    def __init__(self,x,y,z):
        self.x = x  # left to right from turtle
        self.y = y  # back to front from turtle
        self.z = z  # down to up from turtle

        self.pos= (self.x, self.y, self.z)

class Pole:
    def __init__(self, w, h, x, y, color=None, contours = None, pc= None):
        self.VALID = True

        self.mask_pos = PoleMaskSize(w,h,x,y)

        self.color = color
        self.RGB_color = None
        self.__set_rgb()

        self.pc_pos = PolePCPos(self.mask_pos, pc)

        self.contours = contours
        self.pos = PolePos(self.pc_pos.x,self.pc_pos.y,self.pc_pos.z)

        if self.pc_pos.pos != (None, None, None):
            self.topdown_pos = PoleTopdownPos(self.pc_pos)
        else:
            self.topdown_pos = None
            self.VALID = False

        self.ID = None

    def __set_rgb(self):
        if self.color == 'r':
            self.RGB_color = (0, 0, 255)
        elif self.color == 'g':
            self.RGB_color = (0,255,0)
        elif self.color == 'b':
            self.RGB_color = (255,0,0)
        else:
            self.RGB_color = (255,255,0)


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


class Pair:
    def __init__(self,pole_1,pole_2):
        self.pole_1 = pole_1
        self.pole_2 = pole_2

        self.mid_x = None
        self.mid_y = None
        self.mid_pos = (self.mid_x, self. mid_y)

        self.t_x = None
        self.t_y = None
        self.t_pos = (self.t_x, self.t_y)

        self.p_x = None
        self.p_y = None
        self.p_pos = (self.p_x, self.p_y)

        self.__set_mid()
        self.__set_t()
        self.__set_p()


    def __set_mid(self):
        self.mid_x = round(self.pole_1.topdown_pos.x + (self.pole_2.topdown_pos.x - self.pole_1.topdown_pos.x) / 2)
        self.mid_y = round(self.pole_1.topdown_pos.y + (self.pole_2.topdown_pos.y - self.pole_1.topdown_pos.y) / 2)

        self.mid_pos = (self.mid_x, self.mid_y)


    def __set_t(self):
        t_x1 = round(self.mid_x + 3 * (self.pole_2.topdown_pos.y-self.pole_1.topdown_pos.y) / 2)
        t_y1 = round(self.mid_y - 3 * (self.pole_2.topdown_pos.x-self.pole_1.topdown_pos.x) / 2)
        rng_t1 = round(pow(t_x1 ** 2 + t_y1 ** 2, 0.5))

        t_x2 = round(self.mid_x - 3 * (self.pole_2.topdown_pos.y-self.pole_1.topdown_pos.y) / 2)
        t_y2 = round(self.mid_y + 3 * (self.pole_2.topdown_pos.x-self.pole_1.topdown_pos.x) / 2)
        rng_t2 = round(pow(t_x2 ** 2 + t_y2 ** 2, 0.5))

        if rng_t1 > rng_t2:
            self.t_x = t_x1
            self.t_y = t_y1
        else:
            self.t_x = t_x2
            self.t_y = t_y2

        self.t_pos = (self.t_x, self.t_y)


    def __set_p(self):
        """-------------------------------------------------------"""
        p_x1 = round(self.mid_x + (self.pole_2.topdown_pos.y-self.pole_1.topdown_pos.y) * 4)
        p_y1 = round(self.mid_y - (self.pole_2.topdown_pos.x-self.pole_1.topdown_pos.x) * 4)
        rng_p1 = round(pow(p_x1 ** 2 + p_y1 ** 2, 0.5))

        p_x2 = round(self.mid_x - (self.pole_2.topdown_pos.y-self.pole_1.topdown_pos.y) * 4)
        p_y2 = round(self.mid_y + (self.pole_2.topdown_pos.x-self.pole_1.topdown_pos.x) * 4)
        rng_p2 = round(pow(p_x2 ** 2 + p_y2 ** 2, 0.5))

        if rng_p1 > rng_p2:
            self.p_x = p_x1
            self.p_y = p_y1
        else:
            self.p_x = p_x2
            self.p_y = p_y2

        self.p_pos = (self.p_x, self.p_y)



