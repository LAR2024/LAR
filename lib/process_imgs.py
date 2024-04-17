import cv2
import numpy as np

from lib.classes import Masks, Contours, Pole, Poles



def get_pairs_from_cams(image, pc):
    masks, vision_image = get_masks(image)
    contours = get_contours(masks)
    poles = get_poles(contours, pc)
    pairs = find_doubles(poles)
    print('lol')

    return pairs, poles, vision_image


def get_masks(image):
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

def makeMasks(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32) / 255.
    h=hsv_img[:,:,0]
    s=hsv_img[:,:,1]
    v=hsv_img[:,:,2]
    hsv=[h,s,v]
    fil={}

    def f(x,r,d,c):
        return cond[c](np.fabs(x-r),d).astype(np.uint8)

    for key in ['r','g','b']:
        ref ={'r':[.5,1,.6],'g':[.22,.6,.3],'b':[.38,.8,.8]}[key]
        diff={'r':[.47,.3,.3],'g':[.1,.3,.4],'b':[.1,.3,.6]}[key]
        rc  ={'r':[ 1, 0, 0],'g':[ 0, 0, 0],'b':[ 0, 0, 0]}[key]
        cond=[np.matrix.__lt__,np.matrix.__gt__]
        buf =list(map(lambda x,r,d,c:f(x,r,d,c),hsv,ref,diff,rc))
        fil[key]=cv2.bitwise_and(cv2.bitwise_and(buf[0],buf[1]),buf[2])
    return fil

def get_contours(masks):
    contours_r, _ = cv2.findContours(masks.r_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_g, _ = cv2.findContours(masks.g_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_b, _ = cv2.findContours(masks.b_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = Contours(contours_r, contours_g, contours_b)
    return contours

def get_poles(contours,pc):
    ID = 0
    poles = Poles()
    for cnt in contours.contours_r:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500 and w * 3 < h and w * 9 > h:
            new_pole = Pole(w, h, x, y, 'r', cnt)
            dx, dy, dz, r = get_delta(new_pole, pc)
            new_pole.pos = (dx,dy,dz)
            new_pole.ID = ID
            ID+=1
            poles.append(new_pole)

    for cnt in contours.contours_g:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500 and w * 3 < h and w * 9 > h:
            new_pole = Pole(w, h, x, y, 'g', cnt)
            dx, dy, dz, r = get_delta(new_pole, pc)
            new_pole.pos = (dx, dy, dz)
            new_pole.ID = ID
            ID += 1
            poles.append(new_pole)

    for cnt in contours.contours_b:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500 and w * 2 < h and w * 10 > h:
            new_pole = Pole(w, h, x, y, 'b', cnt)
            dx, dy, dz, r = get_delta(new_pole, pc)
            new_pole.pos = (dx, dy, dz)
            new_pole.ID = ID
            ID += 1
            poles.append(new_pole)

    return poles

def get_delta(bod, pc):
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

def draw_poles(img, poles):
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

        pole.m_x = pole.x + round(pole.w/2)
        pole.m_y = pole.y + round(pole.h/2)

        cv2.drawMarker(img, (pole.m_x, pole.m_y), color=color, thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

def draw_mid(img):
    if img is not None:
        cv2.drawMarker(img, (round(len(img[0]) / 2), round(len(img) / 2)), color=[255, 255, 255], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

def draw_topdown(poles,pc):
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
    cv2.line(blank_img, (int(w / 2)+5, 0), (int(w / 2)+5, int(h - 10)), (255, 255, 255), 1)
    cv2.line(blank_img, (int(w / 2)-5, 0), (int(w / 2)-5, int(h - 10)), (255, 255, 255), 1)

    for pole in poles.poles:
        dx_r, dy_r, dz_r, r = get_delta(pole, pc)
        if dx_r is None:
            continue

        x = int(round(w/2+dx_r*200))
        y = int(round(h-dz_r*200))

        pole.topdown_pos = (x,y)

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

    """tady pod tim kreslim stenu pred sebou"""
    for x in range(len(pc[0])):
        p_x,p_y,p_z = pc[int((60/100)*h)][x]
        if not np.isnan(p_x) and not np.isnan(p_y) and not np.isnan(p_z):
            rx = int(round(w / 2 + p_x * 200))
            ry = int(round(h - p_z * 200))
            if 0<=rx<800 and 0<=ry<480:
                blank_img[ry][rx]=[128,128,128]
            #print(rx,ry)
        else:
            pass
            #print('NaN')


    """cv2.imshow('TOP_DOWN', blank_img)
    cv2.moveWindow('TOP_DOWN', 650, 550)
    cv2.waitKey(1)"""
    return blank_img

def find_doubles(poles):
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

def draw_pairs(pairs,blank_img):
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

        """----------------------------------------------------------"""
        t_x1 = round(mid_x + 3*(y2 - y1) / 2)
        t_y1 = round(mid_y - 3*(x2 - x1) / 2)
        rng_t1 = round(pow(t_x1**2+t_y1**2, 0.5))

        t_x2 = round(mid_x - 3*(y2 - y1) / 2)
        t_y2 = round(mid_y + 3*(x2 - x1) / 2)
        rng_t2 = round(pow(t_x2 ** 2 + t_y2 ** 2, 0.5))


        if rng_t1 > rng_t2:
            t_x = t_x1
            t_y = t_y1
        else:
            t_x = t_x2
            t_y = t_y2
        """----------------------------------------------------------"""

        """----------------------------------------------------------"""
        p_x1 = round(mid_x + (y2 - y1) * 4)
        p_y1 = round(mid_y - (x2 - x1) * 4)
        rng_p1 = round(pow(p_x1 ** 2 + p_y1 ** 2, 0.5))

        p_x2 = round(mid_x - (y2 - y1) * 4)
        p_y2 = round(mid_y + (x2 - x1) * 4)
        rng_p2 = round(pow(p_x2 ** 2 + p_y2 ** 2, 0.5))

        if rng_p1 > rng_p2:
            p_x = p_x1
            p_y = p_y1
        else:
            p_x = p_x2
            p_y = p_y2
        """----------------------------------------------------------"""



        cv2.drawMarker(blank_img, (mid_x,mid_y), color=[0, 255, 255], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.drawMarker(blank_img, (t_x, t_y), color=[255, 255, 0], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.drawMarker(blank_img, (p_x, p_y), color=[128, 0, 128], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.line(blank_img, (p_x, p_y), (int(w / 2), int(h - 10)), (128, 0, 128), 2)

        #print(x1,y1,x2,y2)

        cv2.line(blank_img, (x1,y1), (x2,y2), (0, 255, 255), 1)

    return blank_img


