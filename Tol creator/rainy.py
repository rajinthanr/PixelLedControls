from functions import *

escape = False
def exit_program():
    global escape
    escape = True
    print("Exiting program...")

keyboard.add_hotkey('esc', exit_program)

drops = [random.randint(-HEIGHT, 0) for _ in range(DROP_COUNT)]
x_positions = [random.randint(0, WIDTH - 1) for _ in range(DROP_COUNT)]

current_frame = 30
while True and current_frame < FRAME_COUNT-30:
    count+=1
    if(count-pTloop<30):
        if(count-pre_time>(1000/30)):
            current_frame += 1
            save_frame() #save the current frame to the tol file
            display_frame() # Display the current frame on window

            print("Frame: ", current_frame, " / ", FRAME_COUNT, end="\r")
            pre_time = count
        continue

    pTloop = count

    for i in range(DROP_COUNT):
        y = drops[i]
        x = x_positions[i]

        # Draw the raindrop as a single pixel
        if 0 <= y < HEIGHT:
            if(x%2):
                color = [255, 255, 255]  
            else:
                color = [0, 255, 0]
            for j in range(3):
                byte_array[y][x][j] += int(color[j])
                byte_array[y][x][j] = min(255, byte_array[y][x][j])  # Limit the range to 0-255
            
            #draw.point((x, y), fill=color)

        # Move the raindrop down
        drops[i] += 1

        # If the raindrop goes beyond the bottom, reset it at a random position
        if drops[i] >= HEIGHT and current_frame < FRAME_COUNT-120:
            drops[i] = random.randint(-20, 0)
            x_positions[i] = random.randint(0, WIDTH - 1)
    
    
    fade_pixels(byte_array, 15)  # Fade all pixels by 10

    if(escape):
        break

black_frame()  # Clear the screen
for i in range(30):
    save_frame()  # Save the last frame to the tol file

cv2.destroyAllWindows()


# Write to custom file

print("✅ Hex values written to output.tol")
