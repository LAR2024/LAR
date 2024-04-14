#!/usr/bin/env python

from robolab_turtlebot import Turtlebot
import numpy as np
import cv2

x_range = (-0.1, 0.1)
z_range = (0.1, 1.0)
WINDOW = 'obstacles'


def main():

    turtle = Turtlebot(pc=True)
    cv2.namedWindow(WINDOW)

    while not turtle.is_shutting_down():
        # get point cloud
        pc = turtle.get_point_cloud()

        if pc is None:
            continue

        # mask out floor points
        mask = pc[:, :, 1] > x_range[0]

        # mask point too far and close
        mask = np.logical_and(mask, pc[:, :, 2] > z_range[0])
        mask = np.logical_and(mask, pc[:, :, 2] < z_range[1])

        if np.count_nonzero(mask) <= 0:
            continue

        # empty image
        image = np.zeros(mask.shape)

        # assign depth i.e. distance to image
        image[mask] = np.int8(pc[:, :, 2][mask] / 3.0 * 255)
        im_color = cv2.applyColorMap(255 - image.astype(np.uint8),
                                     cv2.COLORMAP_JET)

        # show image
        cv2.imshow(WINDOW, im_color)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
