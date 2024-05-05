import cv2
import numpy as np

from lib.classes import Masks, Contours, Pole, Poles, Pair




def get_pairs_from_cams(image, pc):
    # TODO: docstring

    masks, vision_image = get_masks(image)
    contours = get_contours(masks)
    poles = get_poles(contours, pc)
    pairs = find_doubles(poles)
    print('14:45')

    return pairs, poles, vision_image


def get_masks(image):
    """ function that founds masks for poles

        :parameter image        # cv2 image of rgb colors from cam

        :return masks           #
        :return vision_image    #
    """
    # TODO: docstring

    rgb_masks = make_masks(image)

    r_mask = rgb_masks['r']
    b_mask = rgb_masks['b']
    g_mask = rgb_masks['g']

    a_mask = cv2.bitwise_or(r_mask, b_mask)
    c_mask = cv2.bitwise_or(a_mask, g_mask)

    masked_img = cv2.bitwise_and(image, image, mask=c_mask)
    vision_image = cv2.bitwise_and(image, image, mask=c_mask)

    masks = Masks(r_mask, g_mask, b_mask, c_mask, masked_img)

    return masks, vision_image


def make_masks(img):     # TODO: rework/prettify
    """ erbiho funkce """
    # TODO: docstring

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


def get_contours(masks):    # TODO: add comments
    """ function that founds contours of r,g,b masks

        :parameter masks    # tuple of (r,g,b) masks

        :return contours    # tuple of (r,g,b) contours
    """
    contours_r, _ = cv2.findContours(masks.r_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_g, _ = cv2.findContours(masks.g_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_b, _ = cv2.findContours(masks.b_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = Contours(contours_r, contours_g, contours_b)
    return contours


def get_poles(contours,pc):     # TODO: add better pole recognition, add comments
    # TODO: docstring
    ID = 0
    poles = Poles()
    for cnt in contours.contours_r:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500 and w * 3 < h and w * 9 > h:
            new_pole = Pole(w, h, x, y, 'r', cnt,pc)
            new_pole.ID = ID
            ID+=1
            poles.append(new_pole)

    for cnt in contours.contours_g:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500 and w * 3 < h and w * 9 > h:
            new_pole = Pole(w, h, x, y, 'g', cnt,pc)
            new_pole.ID = ID
            ID += 1
            poles.append(new_pole)

    for cnt in contours.contours_b:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500 and w * 2 < h and w * 10 > h:
            new_pole = Pole(w, h, x, y, 'b', cnt,pc)
            new_pole.ID = ID
            ID += 1
            poles.append(new_pole)

    return poles


def find_doubles(poles):    # TODO: add comments, prettify
    # TODO: docstring

    Pairs_id = []
    Pairs = []
    for index1,pole1 in enumerate(poles.poles):
        for index2,pole2 in enumerate(poles.poles):
            if pole1.pos.x is not None and pole2.pos.x is not None:
                if index1!=index2:
                    diff = ((pole1.pos.x-pole2.pos.x)**2+(pole1.pos.y-pole2.pos.y)**2+(pole1.pos.z-pole2.pos.z)**2)**0.5
                    if diff<0.2 and ((pole1.color == 'r' and pole2.color == 'b') or (pole1.color == 'b' and pole2.color == 'r') or (pole1.color == 'g' and pole2.color == 'g') ):
                        if [pole1, pole2] not in Pairs_id and [pole2,pole1] not in Pairs_id:
                            Pairs_id.append([pole1, pole2])

                            New_Pair = Pair(pole1,pole2)
                            Pairs.append(New_Pair)

            else:
                print("err None in pole.pos")
    return Pairs


