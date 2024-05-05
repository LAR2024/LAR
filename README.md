# LAR

Robot setup:
cmd1:

```
ssh -X user@turtle..
pass: .....

mount /local

singularity shell /local/robolab_noetic.simg

source /opt/ros/lar/setup.bash

roslaunch robolab_turtlebot bringup_realsense_D435.launch
```

cmd2:

```
ssh -X erbenma2@turtle...
pass: .....

mount /local

singularity shell /local/robolab_noetic.simg

source /opt/ros/lar/setup.bash
```

