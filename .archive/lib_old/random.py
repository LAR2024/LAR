import cv2
import os
import signal

bumper_names = ['LEFT', 'CENTER', 'RIGHT']
state_names = ['RELEASED', 'PRESSED']

main_pid = None

def draw_image(window_name, image, pos):
    cv2.imshow(window_name, image)
    cv2.moveWindow(window_name, pos[0], pos[1])
    cv2.waitKey(1)

def bumper_cb(msg):
    """Bumber callback."""
    # msg.bumper stores the id of bumper 0:LEFT, 1:CENTER, 2:RIGHT
    bumper = bumper_names[msg.bumper]

    # msg.state stores the event 0:RELEASED, 1:PRESSED
    state = state_names[msg.state]

    # Print the event
    print('{} bumper {}'.format(bumper, state))
    os.kill(main_pid, signal.SIGKILL)

