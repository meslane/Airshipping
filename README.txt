~== ENGINE ==~
The game engine has two separate ticks, one for physics and one for drawing frames. Multiple physics ticks happen per drawn frame. The physics time step is kept constant and the number of physics ticks per frame increases as the framerate decreases.

The physics engine evaluates in 1/480 second intervals. This oversampling is done so that the overall time error for higher framerates is lower. The game is capped at max 120 fps. 

~== TODO ==~
Add a sort of synchSM or scheduler to the main loop

~== CREDITS ==~
ENDESGA for the ENDESGA 16 color palette: https://lospec.com/palette-list/endesga-16
