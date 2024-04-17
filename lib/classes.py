






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












