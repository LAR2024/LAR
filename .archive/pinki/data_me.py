#!/usr/bin/env python

import cv2

import numpy as np

import me

from robolab_turtlebot import Turtlebot, detector

WINDOW = 'markers'




def main():

    turtle = Turtlebot(rgb=True)
    cv2.namedWindow(WINDOW)

    while not turtle.is_shutting_down():
        # get point cloud
        image = turtle.get_rgb_image()

        # wait for image to be ready
        if image is None:
            continue

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


        print('update')
        """for y in range(len(image)):
            for x in range(len(image[0])):
                cceck(hsv[y][x],image,x,y)"""

        r_low = np.array([0,130,80])
        r_up = np.array([10,255,255])
        b_low = np.array([90,130,80])
        b_up = np.array([150,255,255])
        g_low = np.array([50,130,80])
        g_up = np.array([70,255,255])

        #r_mask = cv2.inRange(hsv, r_low, r_up)
        #b_mask = cv2.inRange(hsv, b_low, b_up)
        #g_mask = cv1.inRange(hsv, g_low, g_up)

        #a_mask = cv2.bitwise_or(r_mask,b_mask)
        #c_mask = cv2.bitwise_or(a_mask,g_mask)
        c_mask=me.cceck(hsv)
        #c_mask=cv2.bitwise_or(c_mask_rgb['r'],c_mask_rgb['b'])
        #c_mask=cv2.bitwise_or(c_mask,c_mask_rgb['g'])
        print(type(c_mask))

        masked_img = cv2.bitwise_and(image, image, mask = c_mask)
        img=masked_img       

        #contours={}
        #contours['r'], _ = cv2.findContours(r_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #contours['g'], _ = cv2.findContours(g_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #contours['b'], _ = cv2.findContours(b_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #pill, img = me.drawBoxes(contours,masked_img)

                #map(,hsv)

                # show image
        cv2.imshow(WINDOW, img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
