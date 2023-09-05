~== ENGINE ==~
The game engine has two separate ticks, one for physics and one for drawing frames. Multiple physics ticks happen per drawn frame. The physics time step is kept constant and the number of physics ticks per frame increases as the framerate decreases.

The physics engine evaluates in 1/480 second intervals. This oversampling is done so that the overall time error for higher framerates is lower. The game is capped at max 120 fps. 

~== TODO ==~
-Refine pathfinding to do A* or something similar instead of the current crappy strategy
-Add audio.py file to handle all game audio

~== BUG TRACKER ==~
-Killing weapon objects crashes the game

~== NOTES ==~
-Pymunk does not like very large bodies, kinematic or not. You can get way better performance by simply spawning contiguous kinematic bodies as several individual tiles.

~== CREDITS ==~
ENDESGA for the ENDESGA 16 color palette: https://lospec.com/palette-list/endesga-16
