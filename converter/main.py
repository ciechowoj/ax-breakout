# brief         part of ax-breakout level converter
# author        Wojciech Szęszoł keepitsimplesirius[at]gmail.com
# encoding      UTF-8 with BOM
# end of line   LF
# tab           4x space

import pygame
from pygame.locals import *
from mathutils import *
pygame.init()


ROOM_SIZE = vec2(800, 400)

print("give image:")
path = input()
print("give size:")
size = input()
print("give keycolor:")
color = input()
print("give output:")
output = input()

size = tuple(size.split())
color = tuple(color.split())
color = int(color[0]), int(color[1]), int(color[2])
size = tuple([int(x) for x in size])

surface = pygame.image.load(path)
result = []

w, h = surface.get_size()

tile_size = vec2(int(size[0]), int(size[1]))
brick_size = tile_size * 0.5
image_size = vec2(w * size[0], h * size[1])

offset = (ROOM_SIZE - image_size + tile_size) * 0.5
spacing = 0
if len(size) > 2:
    spacing = size[2]

for y in range(h):
    for x in range(w):
        pixel = surface.get_at((x, y))
        if pixel != color:
            result.append("b " + str(offset.x + x * tile_size.x) + " " + str(offset.y + y * tile_size.y) + " " + str(brick_size.x - spacing) + " " + str(brick_size.y - spacing) + " " + str(pixel[0]) + " " + str(pixel[1]) + " " + str(pixel[2]))

file = open(output, "w+")
for l in result:
    file.write(l + "\n")
