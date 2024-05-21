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
                if r_mid[1] + i >= len(pc) or r_mid[0] + j >= len(pc[0]):
                    continue

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

        self.pos = (self.x, self.y, self.z)


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


class LocalPosition:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.pos = (self.x, self.y, self.z)


class TopdownPosition:
    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.pos = (self.x, self.y)


class Position:
    def __init__(self, local, topdown):
        self.local = local
        self.topdown = topdown


class Pair:
    def __init__(self,pole_1,pole_2):
        if pole_1.pos.x < pole_2.pos.x:
            self.pole_1 = pole_1
            self.pole_2 = pole_2
        else:
            self.pole_1 = pole_2
            self.pole_2 = pole_1

        self.mid = None

        self.park = None

        self.help = None

        self.__set_mid()
        self.__set_help()
        self.__set_p()


    def __set_mid(self):
        #print(0.15)
        vector_x = self.pole_2.pos.x - self.pole_1.pos.x
        vector_y = self.pole_2.pos.y - self.pole_1.pos.y
        vector_z = self.pole_2.pos.z - self.pole_1.pos.z

        size = (vector_x**2 + vector_y**2)**(1/2)

        vector_x = 0.035*vector_x/size
        vector_y = 0.035*vector_y/size

        mid_x = self.pole_1.pos.x + (self.pole_2.pos.x - self.pole_1.pos.x) * 0.15
        mid_y = self.pole_1.pos.y + (self.pole_2.pos.y - self.pole_1.pos.y) * 0.15
        mid_z = self.pole_1.pos.z + (self.pole_2.pos.z - self.pole_1.pos.z) / 2

        topdown_mid_x = round(self.pole_1.topdown_pos.x + (self.pole_2.topdown_pos.x - self.pole_1.topdown_pos.x) / 2)
        topdown_mid_y = round(self.pole_1.topdown_pos.y + (self.pole_2.topdown_pos.y - self.pole_1.topdown_pos.y) / 2)

        self.mid = Position(LocalPosition(mid_x,mid_y,mid_z), TopdownPosition(topdown_mid_x,topdown_mid_y))
        #print(self.pole_1.color, self.pole_2.color)

    def __set_help(self):
        top_help_x1 = round(self.mid.topdown.x + (self.pole_2.topdown_pos.y - self.pole_1.topdown_pos.y) * 8)
        top_help_y1 = round(self.mid.topdown.y - (self.pole_2.topdown_pos.x - self.pole_1.topdown_pos.x) * 8)
        top_rng_help1 = round(pow(top_help_x1 ** 2 + top_help_y1 ** 2, 0.5))

        top_help_x2 = round(self.mid.topdown.x - (self.pole_2.topdown_pos.y - self.pole_1.topdown_pos.y) * 8)
        top_help_y2 = round(self.mid.topdown.y + (self.pole_2.topdown_pos.x - self.pole_1.topdown_pos.x) * 8)
        top_rng_help2 = round(pow(top_help_x2 ** 2 + top_help_y2 ** 2, 0.5))

        if top_rng_help1 > top_rng_help2:
            topdown_p_x = top_help_x1
            topdown_p_y = top_help_y1
        else:
            topdown_p_x = top_help_x2
            topdown_p_y = top_help_y2


        v_p1_m_x = (self.pole_2.pos.x - self.pole_1.pos.x) / 2
        v_p1_m_y = (self.pole_2.pos.y - self.pole_1.pos.y) / 2
        v_p1_m_z = (self.pole_2.pos.z - self.pole_1.pos.z) / 2

        mid_x = self.mid.local.x
        mid_y = self.mid.local.y
        mid_z = self.mid.local.z

        local_x1 = mid_x + v_p1_m_y * 8
        local_y1 = mid_y - v_p1_m_x * 8
        local_z1 = mid_z
        local_rng_t1 = (local_x1 ** 2 + local_y1 ** 2) ** 0.5

        local_x2 = mid_x - v_p1_m_y * 8
        local_y2 = mid_y + v_p1_m_x * 8
        local_z2 = mid_z
        local_rng_t2 = (local_x2 ** 2 + local_y2 ** 2) ** 0.5

        if local_rng_t1 < local_rng_t2:
            local_t_x = local_x1
            local_t_y = local_y1
            local_t_z = local_z1
        else:
            local_t_x = local_x2
            local_t_y = local_y2
            local_t_z = local_z2


        self.help = Position(LocalPosition(local_t_x, local_t_y, local_t_z), TopdownPosition(topdown_p_x, topdown_p_y))


    def __set_p(self):
        top_park_x1 = round(self.mid.topdown.x + (self.pole_2.topdown_pos.y - self.pole_1.topdown_pos.y))
        top_park_y1 = round(self.mid.topdown.y - (self.pole_2.topdown_pos.x - self.pole_1.topdown_pos.x))
        top_rng_park1 = round(pow(top_park_x1 ** 2 + top_park_y1 ** 2, 0.5))

        top_park_x2 = round(self.mid.topdown.x - (self.pole_2.topdown_pos.y - self.pole_1.topdown_pos.y))
        top_park_y2 = round(self.mid.topdown.y + (self.pole_2.topdown_pos.x - self.pole_1.topdown_pos.x))
        top_rng_park2 = round(pow(top_park_x2 ** 2 + top_park_y2 ** 2, 0.5))

        if top_rng_park1 > top_rng_park2:
            topdown_t_x = top_park_x1
            topdown_t_y = top_park_y1
        else:
            topdown_t_x = top_park_x2
            topdown_t_y = top_park_y2

        v_p1_m_x = (self.pole_2.pos.x - self.pole_1.pos.x) / 2
        v_p1_m_y = (self.pole_2.pos.y - self.pole_1.pos.y) / 2
        v_p1_m_z = (self.pole_2.pos.z - self.pole_1.pos.z) / 2

        mid_x = self.mid.local.x
        mid_y = self.mid.local.y
        mid_z = self.mid.local.z

        p_x1 = mid_x + v_p1_m_y * 4.5
        p_y1 = mid_y - v_p1_m_x * 4.5
        p_z1 = mid_z
        rng_p1 = (p_x1 ** 2 + p_y1 ** 2) ** 0.5

        p_x2 = mid_x - v_p1_m_y * 4.5
        p_y2 = mid_y + v_p1_m_x * 4.5
        p_z2 = mid_z
        rng_p2 = (p_x2 ** 2 + p_y2 ** 2) ** 0.5

        if rng_p1 < rng_p2:
            local_p_x = p_x1
            local_p_y = p_y1
            local_p_z = p_z1
        else:
            local_p_x = p_x2
            local_p_y = p_y2
            local_p_z = p_z2


        self.park = Position(LocalPosition(local_p_x, local_p_y, local_p_z), TopdownPosition(topdown_t_x, topdown_t_y))



