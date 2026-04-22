from functions import *


PARTICLE_COUNT = 1000


def _panel(x):
    return x // STRIPS_PER_SIDE


def reset_drop(i):
    x_positions[i] = random.randint(0, WIDTH - 1)
    if _panel(x_positions[i]) % 2 == 1:
        drops[i]      = float(random.randint(HEIGHT, HEIGHT + 20))
        directions[i] = -1   # upward
    else:
        drops[i]      = float(random.randint(-20, 0))
        directions[i] =  1   # downward


x_positions = [random.randint(0, WIDTH - 1) for _ in range(PARTICLE_COUNT)]
directions  = [-1 if _panel(x) % 2 == 1 else 1 for x in x_positions]
drops       = [float(random.randint(HEIGHT, HEIGHT + 20)) if d == -1
               else float(random.randint(-HEIGHT, 0))
               for d in directions]

current_frame = 30
while True and current_frame < FRAME_COUNT-30:
    count+=1
    if(count-pTloop<30):
        if(count-pre_time>(1000/30)):
            current_frame += 1
            save_frame()
            display_frame()
            pre_time = count
            fade_pixels(byte_array, 25)
        continue

    pTloop = count

    for i in range(PARTICLE_COUNT):
        y = int(drops[i])
        x = x_positions[i]
        d = directions[i]

        if x % 2:
            color = [255, 255, 255]
        else:
            color = [0, 255, 0]

        for j in range(3):
            for b in range(3):
                ty = y + b * d   # trail follows direction of travel
                if 0 <= ty < HEIGHT:
                    byte_array[ty][x][j] = min(255, byte_array[ty][x][j] + int(color[j] * 0.7))

        drops[i] += 0.3 * d

        if d == 1 and drops[i] >= HEIGHT and current_frame < FRAME_COUNT - 120:
            reset_drop(i)
        elif d == -1 and drops[i] < 0 and current_frame < FRAME_COUNT - 120:
            reset_drop(i)
    
    

    if escape[0]:
        break

fade_out_and_close()
