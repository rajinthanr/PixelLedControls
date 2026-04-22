from functions import *

BLOCK_SIZE   = 4
NUM_COLS     = WIDTH // BLOCK_SIZE   # 28 grid columns
MAX_ACTIVE   = 20                     # simultaneous falling blocks

BLOCK_COLORS = [
    [0,   200, 0  ],   # green
    [255, 255, 240],   # warm white
    [255, 215, 0  ],   # gold
]

# col_height[c] = y of the top of the stack in grid column c (HEIGHT = empty floor)
col_height  = [HEIGHT] * NUM_COLS
# grid_colors[y][x] stores the landed pixel colour, or None if empty
grid_colors = [[None] * WIDTH for _ in range(HEIGHT)]


def spawn_block():
    free = [c for c in range(NUM_COLS) if col_height[c] > BLOCK_SIZE]
    if not free:
        return None
    col   = random.choice(free)
    color = random.choice(BLOCK_COLORS)
    return {'col': col, 'y': -BLOCK_SIZE, 'color': list(color)}


def land_block(b):
    col    = b['col']
    land_y = col_height[col] - BLOCK_SIZE
    if land_y < 0:
        return
    for y in range(land_y, land_y + BLOCK_SIZE):
        for x in range(col * BLOCK_SIZE, (col + 1) * BLOCK_SIZE):
            if 0 <= y < HEIGHT:
                grid_colors[y][x] = b['color']
    col_height[col] = land_y


def render():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            byte_array[y][x] = list(grid_colors[y][x]) if grid_colors[y][x] else [0, 0, 0]
    for b in active_blocks:
        if b is None:
            continue
        y0 = int(b['y'])
        for dy in range(BLOCK_SIZE):
            py = y0 + dy
            if 0 <= py < HEIGHT:
                for x in range(b['col'] * BLOCK_SIZE, (b['col'] + 1) * BLOCK_SIZE):
                    byte_array[py][x] = list(b['color'])


active_blocks = [spawn_block() for _ in range(MAX_ACTIVE)]

current_frame = 30
while True and current_frame < FRAME_COUNT - 30:
    count += 1
    if count - pTloop < 90:
        if count - pre_time > (1000 / 30):
            current_frame += 1
            render()
            save_frame()
            display_frame()
            pre_time = count
        continue

    pTloop = count

    if escape[0]:
        break

    to_replace = []
    for i, b in enumerate(active_blocks):
        if b is None:
            to_replace.append(i)
            continue
        b['y'] += 1
        if b['y'] + BLOCK_SIZE >= col_height[b['col']]:
            b['y'] = col_height[b['col']] - BLOCK_SIZE   # snap to grid
            land_block(b)
            to_replace.append(i)

    for i in to_replace:
        active_blocks[i] = spawn_block()


fade_out_and_close()
