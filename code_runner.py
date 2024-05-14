from lib.main import NewControl
import math

print("19:41")

xd = NewControl()

#xd.rotate(math.pi)
#xd.move(-0.1)

xd.update_imgs()
xd.update_imgs()
xd.update_imgs()
xd.update_imgs()

print('!!! Starting !!!')

#xd.start_turn()

xd.move_to_nearest_pair()

#xd.start()
#xd.find_nearest_pair()
#xd.main_loop()


"""while True:
    xd.update_imgs()"""

#xd.new_move(1, False)

#xd.new_rotate(math.pi)

"""xd.rotate(math.pi)
xd.new_move(3, True)
xd.rotate(math.pi)"""

#xd.move_to_nearest_pair()

#xd.move2xyf(-0.5,0.5, -math.pi*0)
#xd.move2xyf(1,1, -math.pi)


