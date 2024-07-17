# Simulates the three body problem using pygame

import pygame
import math
import threading
import time

# simulation timestep in seconds
SIM_TIMESTEP = 0.005
# simulation time to real time conversion
SIM_TO_REAL = 0.04

# a class representing a point like object floating in 2D space
class Object:
    def __init__(self, mass, pos, vel):
        self.mass = mass
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)

    # symmetric
    def force_magnitude(self, other):
        delta = other.pos - self.pos
        r_squared = delta.magnitude_squared()
        return self.mass * other.mass / r_squared

    # asymmetric
    def force_direction(self, other):
        delta = other.pos - self.pos
        r = delta.magnitude()
        return delta / r

# reset the simulation 
def reset():
    global objects
    objects = []
    # try changing some of these numbers
    #                     mass,position,velocity
    objects.append(Object(60, (-25, 0), (0, -1)))
    objects.append(Object(100, (20, 0), (0, 0)))
    objects.append(Object(80, (0, 30), (3, 0)))

# simulate the next step
def update():
    for i in range(len(objects)):
        obj = objects[i]
        force_total = pygame.math.Vector2(0, 0)
        for j in range(len(objects)):
            if i == j:
                continue
            # if (obj.pos - objects[j].pos).magnitude_squared() < 1:
            #     force_total += -10000 * obj.force_direction(objects[j])
            # else:
            force_total += obj.force_magnitude(objects[j]) * \
            obj.force_direction(objects[j])

        obj.vel += SIM_TIMESTEP * force_total / obj.mass
        obj.pos += SIM_TIMESTEP * obj.vel

reset()

# do the physics
def physics():
    while True:
        ts = time.time()
        update()
        ts_old = ts
        time.sleep(SIM_TIMESTEP * SIM_TO_REAL - (ts_old - ts))

physics_thread = threading.Thread(target=physics, args=()).start()

# pygame setup
running = True
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

traces = [[] for _ in range(len(objects))]

trace_ball = []
trace_center = []

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    width, height = screen.get_size()
    mid = pygame.math.Vector2(width / 2, height / 2)
    scale = min(width, height)

    avg_pos = pygame.math.Vector2(0, 0)
    for obj in objects:
        avg_pos += obj.pos
    avg_pos /= len(objects)

    convert = lambda pos: mid + \
        (pos - avg_pos) * scale / 100
    
    # draw traces
    trace_len = len(traces[0])
    for i in range(trace_len):
        if i == 0:
            continue
        for trace in traces:
            prev = convert(trace[i - 1])
            curr = convert(trace[i])

            t = i / trace_len
            w = int(scale/100.0)
            b = t * 100

            pygame.draw.line(screen, (b, b, b), prev, curr, width=w)
    
    # draw circles
    for i in range(len(objects)):
        obj = objects[i]
        trace = traces[i]

        trace.append(pygame.math.Vector2(obj.pos))
        if len(trace) > 100:
            trace.pop(0)

        c = scale / 600.0
        radius = math.sqrt(obj.mass) * c
        pygame.draw.circle(screen, (255, 255, 255), center=convert(obj.pos), radius=radius)

        
    # flip() the display to put your work on screen
    pygame.display.flip()
    

    clock.tick(60)  # limits FPS to 60

pygame.quit()
physics_thread.join()
