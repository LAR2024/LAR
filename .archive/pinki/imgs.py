from robolab_turtlebot import Turtlebot

from imageio import imwrite
import cv2

turtle = Turtlebot(rgb=True)
turtle.wait_for_rgb_image()
bgr = turtle.get_rgb_image()

rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


filename = 'capture_rgb23.png'

print('Image saved as {}'.format(filename))
imwrite(filename, rgb)
