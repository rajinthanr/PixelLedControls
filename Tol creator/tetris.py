from functions import *

escape = False
def exit_program():
    global escape
    escape = True
    print("Exiting program...")

keyboard.add_hotkey('esc', exit_program)

# Define Tetris block shapes

# Define Tetris block shapes and their corresponding colors
TETRIS_SHAPES = [
    [[1, 1, 1, 1]],  # Line
    [[1, 1], [1, 1]],  # S\quare
    [[0, 1, 0], [1, 1, 1]],  # T-shape
    [[1, 1, 0], [0, 1, 1]],  # Z-shape
    [[0, 1, 1], [1, 1, 0]]   # S-shape
]

TETRIS_COLORS = [
    [255, 0, 0],  # Red for Line
    [0, 255, 0],  # Green for Square
    [0, 0, 255],  # Blue for T-shape
    [255, 255, 0],  # Yellow for Z-shape
    [255, 0, 255]   # Magenta for S-shape
]

# Initialize Tetris blocks and their colors
DROP_COUNT = 200  # Number of blocks to drop
blocks = [random.choice(TETRIS_SHAPES) for _ in range(DROP_COUNT)]
block_colors = [TETRIS_COLORS[TETRIS_SHAPES.index(block)] for block in blocks]
block_positions = [(random.randint(0, WIDTH - len(blocks[i][0])), random.randint(-HEIGHT, 0)) for i in range(DROP_COUNT)]

grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]  # Initialize the grid

# Main loop
while True and current_frame < FRAME_COUNT - 30:
    count += 1
    if count - pTloop < 60:
        if count - pre_time > (1000 / 30):
            current_frame += 1

            for row in range(len(grid)):
                for j in range(len(grid[0])):
                    if grid[row][j] == 1:
                        byte_array[row][j] = [255, 255, 255]  # Reset the color to black

            save_frame()  # Save the current frame to the tol file
            display_frame()  # Display the current frame on window

            print("Frame: ", current_frame, " / ", FRAME_COUNT, end="\r")
            pre_time = count
        continue

    pTloop = count
    fade_pixels(byte_array, 255) 
    for i in range(DROP_COUNT):
        block = blocks[i]
        color = block_colors[i]
        x, y = block_positions[i]

        # Check if the block can move down
        can_move_down = True
        for row_idx, row in enumerate(block):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    px, py = x + col_idx, y + row_idx
                    if py + 1 >= HEIGHT or (py + 1 >= 0 and grid[py + 1][px] == 1):
                        can_move_down = False

        if can_move_down:
            # Move the block down
            block_positions[i] = (x, y + 1)
            for row_idx, row in enumerate(block):
                for col_idx, cell in enumerate(row):      
                    px, py = x + col_idx, y + row_idx
                    if cell == 1 and (py >= 0):
                        for j in range(3):
                            byte_array[py][px][j] = color[j]

        else:
            # Mark the block's cells as occupied in the grid
            for row_idx, row in enumerate(block):
                for col_idx, cell in enumerate(row):
                    if cell == 1:
                        px, py = x + col_idx, y + row_idx
                        if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                            grid[py][px] = 1
                            for j in range(3):
                                byte_array[py][px][j] = color[j]

            # Reset the block to a new random position and color
            blocks[i] = random.choice(TETRIS_SHAPES)
            block_colors[i] = TETRIS_COLORS[TETRIS_SHAPES.index(blocks[i])]
            block_positions[i] = (random.randint(0, WIDTH - len(blocks[i][0])), random.randint(-20, 0))

    if escape:
        break

black_frame()  # Clear the screen
for i in range(30):
    save_frame()  # Save the last frame to the tol file

cv2.destroyAllWindows()

# Write to custom file

print("✅ Hex values written to output.tol")
