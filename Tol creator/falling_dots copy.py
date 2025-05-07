from functions import *

escape = False
def exit_program():
    global escape
    escape = True
    print("Exiting program...")

keyboard.add_hotkey('esc', exit_program)

GREEN = [0, 255, 0]  # RGB color for green
WHITE = [255, 255, 255]  # RGB color for white
BLACK = [0, 0, 0]  # RGB color for black
YELLOW = [255, 130, 0]  # RGB color for yellow


# Main loop
for t in range(5):
    for side in range(4):
        for i in range(HEIGHT):
                if(escape):
                    break
                for j in range(side*(WIDTH//8), (side+1)*(WIDTH//8)):
                    if(side % 2 == 0):
                        byte_array[i][j]= WHITE
                        byte_array[i][j+WIDTH//2] = WHITE
                    else:
                        byte_array[i][j] = GREEN
                        byte_array[i][j+WIDTH//2] = GREEN
                display_frame()
                save_frame()
    for i in range(HEIGHT//2):
        if(escape):
            break
        for j in range(WIDTH):
            byte_array[i][j] = BLACK
        display_frame()
        save_frame()
    for i in range(HEIGHT//2):
        if(escape):
            break
        for j in range(WIDTH):
            byte_array[i][j] = YELLOW
        display_frame()
        save_frame()
    for i in range(HEIGHT//2, HEIGHT):
        if(escape):
            break
        for j in range(WIDTH):
            byte_array[i][j] = BLACK
        display_frame()
        save_frame()
    for i in range(HEIGHT//2, HEIGHT):
        if(escape):
            break
        for j in range(WIDTH):
            byte_array[i][j] = WHITE
        display_frame()
        save_frame()
    for i in range(0, HEIGHT):
        if(escape):
            break
        for j in range(WIDTH):
            byte_array[i][j] = BLACK
        display_frame()
        save_frame()
         
    


black_frame()  # Clear the screen
for i in range(30):
    save_frame()  # Save the last frame to the tol file

cv2.destroyAllWindows()

# Write to custom file

print("✅ Hex values written to output.tol")
