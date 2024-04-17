import cv2




def get_pairs_from_cams(image, pc):
    cv2.imwrite('images/image.png', image)
    cv2.imwrite('images/pc.png', pc)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    masks, vision_image = self.get_masks(hsv, image)

    contours = self.get_contours(masks)

    poles = self.get_poles(contours, pc)

    self.draw_poles(vision_image, poles)

    self.draw_mid(vision_image)

    self.draw_masks(vision_image)

    cv2.imwrite('images/vision_image.png', vision_image)

    blank_img = self.draw_topdown(poles, pc)

    pairs = self.find_doubles(poles)

    self.draw_pairs(pairs, blank_img)
    cv2.imwrite('images/blank_img.png', blank_img)
    return pairs























