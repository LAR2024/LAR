import cv2
import numpy as np

WHITE = (255, 255, 255)


def draw_pairs(pairs,blank_img):    # TODO: add comments
    # TODO: docstring

    for pair in pairs:
        pole1= pair.pole_1
        pole2 = pair.pole_2

        w = 640
        h = 480


        cv2.drawMarker(blank_img, pair.mid_pos, color=[0, 255, 255], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.drawMarker(blank_img, pair.t_pos, color=[255, 255, 0], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.drawMarker(blank_img, pair.p_pos, color=[128, 0, 128], thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

        cv2.line(blank_img, pair.p_pos , (int(w / 2), int(h - 10)), (128, 0, 128), 2)

        cv2.line(blank_img, pole1.topdown_pos.pos, pole2.topdown_pos.pos, (0, 255, 255), 1)

    return blank_img


def draw_poles(img, poles):
    # TODO: docstring

    for pole in poles.poles:
        # draw pole contours
        cv2.drawContours(img, [pole.contours], 0, WHITE, 2)

        # draw draw rectangle around pole
        cv2.rectangle(img, pole.mask_pos.pos, pole.mask_pos.pos2 , pole.RGB_color, 2)

        # draw cross in the middle of pole
        cv2.drawMarker(img, (pole.mask_pos.middle_x, pole.mask_pos.middle_y), color=pole.RGB_color, thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)


def draw_mid(img):      # TODO: add comments
    # TODO: docstring

    if img is not None:
        cv2.drawMarker(img, (round(len(img[0]) / 2), round(len(img) / 2)), color=WHITE, thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)


def draw_topdown(poles,pc):      # TODO: rework walls drawing
    # TODO: docstring

    w = 640
    h = 480
    f = 70

    # empty img for topdown
    blank_img = np.zeros((h, w, 3), dtype = np.uint8)

    # draw white cross of turtle pos
    cv2.drawMarker(blank_img, (int(w/2), int(h-10)), color=WHITE, thickness=1,
                   markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                   markerSize=10)

    # draw FOV lines
    cv2.line(blank_img, (f, 0), (int(w/2), int(h-10)), WHITE, 1)
    cv2.line(blank_img, (w-f, 0), (int(w / 2), int(h-10)), WHITE, 1)

    # draw straight lines of way
    cv2.line(blank_img, (int(w / 2)+5, 0), (int(w / 2)+5, int(h - 10)), WHITE, 1)
    cv2.line(blank_img, (int(w / 2)-5, 0), (int(w / 2)-5, int(h - 10)), WHITE, 1)

    # draw poles positions
    for pole in poles.poles:
        cv2.drawMarker(blank_img, pole.topdown_pos.pos, color=pole.RGB_color, thickness=1,
                       markerType=cv2.MARKER_TILTED_CROSS, line_type=cv2.LINE_AA,
                       markerSize=10)

    # TODO: draw walls
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

    return blank_img
