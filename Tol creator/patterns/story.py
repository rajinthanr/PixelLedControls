import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *


GREEN = [0, 255, 0]  # RGB color for green
WHITE = [255, 255, 255]  # RGB color for white
BLACK = [0, 0, 0]  # RGB color for black
YELLOW = [255, 130, 0]  # RGB color for yellow


# Main loop
for t in range(5):
    for side in range(SIDES):
        for i in range(HEIGHT):
                if escape[0]:
                    break
                for j in range(side * STRIPS_PER_SIDE, (side + 1) * STRIPS_PER_SIDE):
                    if side % 2 == 0:
                        byte_array[i][j] = WHITE
                    else:
                        byte_array[i][j] = GREEN
                display_frame()
                save_frame()
    for i in range(HEIGHT//2):
        if escape[0]:
            break
        for j in range(WIDTH):
            byte_array[i][j] = BLACK
        display_frame()
        save_frame()
    for i in range(HEIGHT//2):
        if escape[0]:
            break
        for j in range(WIDTH):
            byte_array[i][j] = YELLOW
        display_frame()
        save_frame()
    for i in range(HEIGHT//2, HEIGHT):
        if escape[0]:
            break
        for j in range(WIDTH):
            byte_array[i][j] = BLACK
        display_frame()
        save_frame()
    for i in range(HEIGHT//2, HEIGHT):
        if escape[0]:
            break
        for j in range(WIDTH):
            byte_array[i][j] = WHITE
        display_frame()
        save_frame()
    for i in range(0, HEIGHT):
        if escape[0]:
            break
        for j in range(WIDTH):
            byte_array[i][j] = BLACK
        display_frame()
        save_frame()
         
    


fade_out_and_close()
