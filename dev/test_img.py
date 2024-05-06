from robolab_turtlebot import Turtlebot

from imageio import imwrite
import cv2


turtle = Turtlebot(rgb=True, pc=True)
turtle.wait_for_rgb_image()
bgr = turtle.get_rgb_image()

rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

i = 6

filename = 'capture_rgb'+str(i)+'.png'


print('Image saved as {}'.format(filename))
imwrite(filename, rgb)


pc = turtle.get_point_cloud()

filename = 'capture_pc'+str(i)+'.png'
imwrite(filename, pc)
