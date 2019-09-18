# brief         part of ax-breakout game
# author        Wojciech Szęszoł keepitsimplesirius[at]gmail.com
# encoding      UTF-8 with BOM
# end of line   LF
# tab           4x space

import pygame
import pygame.gfxdraw
from pygame.locals import *
from mathutils import *
from random import random
from random import randint
from QuadTree import *

ENTITY_BRICK = 0
ENTITY_BALL = 6
ENTITY_BAT = 2
ENTITY_POWERUP = 3
ENTITY_BORDER = 4
ENTITY_WRECK = 5

POWERUP_SHORTEN = 0
POWERUP_WIDEN = 1
POWERUP_LIVE = 2
POWERUP_BALL = 3
POWERUP_SPEED_UP = 4
POWERUP_SLOW_DOWN = 5
POWERUP_NUMBER = 6

GLOBAL_ALPHA = 128
BALL_VELOCITY = 300.0
MAX_BALL_VELOCITY = 800.0
MIN_BALL_VELOCITY = 300.0
BALL_WAIT = 2.0
GRAVITY = 98.1 * 4.0
BAT_SIZES = [(100, 10, 0.7), (200, 10, 0.49971), (300, 10, 0.44), (500, 10, 0.33)]
SQRT2 = 1.41

crashes = [pygame.mixer.Sound("data/glass" + str(x) + ".wav") for x in range(0, 8)]
metal = pygame.mixer.Sound("data/wood0.wav")

class Ball:
    def __init__(self, position, radius, color):
        self.type = ENTITY_BALL
        self.position = position
        self.startPos = position
        self.radius = radius
        self.size = vec2(radius, radius)
        self.color = color
        self.velocity = rotate2(vec2(0, -BALL_VELOCITY), (random() - 0.5) * pi * 0.5)
        self.wait = 0.0

    def onUpdate(self, delta, current):
        if self.wait < BALL_WAIT:
            self.wait += delta
        else:
            self.position += self.velocity * delta
            self.predicted = self.position + self.velocity * delta * 2
        return self

    def onRedraw(self, surface):
        position = self.position.intcpl()
        pygame.gfxdraw.filled_circle(surface, position[0], position[1], int(self.radius), self.color)
        pygame.gfxdraw.aacircle(surface, position[0], position[1], int(self.radius), self.color)

    def onCollide(self, obstacle, point, normal):
        if obstacle == ENTITY_BORDER and dot2(normal, vec2(0.0, -1.0)) > SQRT2 * 0.4:
            self.position = self.startPos
            self.velocity = -self.velocity
            self.wait = 0.0
        else:
            penetration = abs(self.radius - (self.position - point).length())
            self.position += normal * penetration
            self.velocity = -reflect2(self.velocity, normal)
            x = self.velocity.normal().x
            if x > 0.98:
                self.velocity = rotate2(self.velocity, 0.2)

        if obstacle == ENTITY_BORDER or obstacle == ENTITY_BAT:
            metal.play()

    def copy(self):
        return Ball(+self.startPos, self.radius, self.color)

    def speedUp(self):
        normal = self.velocity.normal()
        length = self.velocity.length()
        length = min(MAX_BALL_VELOCITY, length + 100)
        self.velocity = normal * length
        
    def slowDown(self):
        normal = self.velocity.normal()
        length = self.velocity.length()
        length = max(MIN_BALL_VELOCITY, length - 100)
        self.velocity = normal * length

class Wreck:
    def __init__(self, brick):
        self.type = ENTITY_WRECK
        self.startPos = brick.position
        self.position = brick.position
        self.size = brick.size
        self.color = brick.color
        self.cracks = brick.cracks
        self.velocity = vec2()

    def onUpdate(self, delta, current):
        self.velocity.y += GRAVITY * delta
        self.position += self.velocity * delta
        if self.position.y > 2000.0:
            return None
        else:
            return self

    def onRedraw(self, surface):
        rect = (self.position - self.size).couple() + (self.size * 2).couple()
        pygame.gfxdraw.box(surface, rect, self.color + (GLOBAL_ALPHA,))
        pygame.gfxdraw.rectangle(surface, rect, self.color)
        offset = self.position - self.startPos
        for i in self.cracks:
            pygame.draw.aaline(surface, self.color, (i[0] + offset).intcpl() , (i[1] + offset).intcpl())

    def onCollide(self, obstacle, point, normal):
        pass

class PowerUp:
    def __init__(self, brick):
        self.type = ENTITY_POWERUP
        self.bonus = randint(0, POWERUP_NUMBER - 2)
        if self.bonus == POWERUP_BALL:  # disable the ball powerup, there are some troubles with it ;)
            self.bonus = POWERUP_LIVE
        self.position = brick.position
        self.radius = 15
        self.color = brick.color
        self.cracks = brick.cracks
        self.velocity = vec2()
        self.sprite = None
        self.destroy = False

    def onUpdate(self, delta, current):
        self.velocity.y += GRAVITY * delta
        self.position += self.velocity * delta
        if self.destroy or self.position.y > 2000.0:
            return None
        else:
            return self

    def onRedraw(self, surface):
        position = self.position.intcpl()
        size = self.sprite.get_size()
        pygame.gfxdraw.filled_circle(surface, position[0], position[1], int(self.radius), self.color + (GLOBAL_ALPHA,))
        pygame.gfxdraw.aacircle(surface, position[0], position[1], int(self.radius), self.color)
        surface.blit(self.sprite, (position[0] - size[0] // 2, position[1] - size[1] // 2 + 1))

    def onCollide(self, obstacle, point, normal):
        if obstacle == ENTITY_BAT:
            self.destroy = True
            crashes[self.value() % 8].play()

    def value(self):
        return self.color[0] + self.color[1] * 3 + self.color[2] * 5

    def init(self, sharedState):
        self.sprite = sharedState.powerups[self.bonus]

class Brick:
    def __init__(self, position, size, color):
        self.type = ENTITY_BRICK
        self.position = position
        self.size = size
        self.color = color
        self.cracks = []
        self.durability = int(size.x * size.y) // 200

    def onUpdate(self, delta, current):
        if len(self.cracks) > self.durability:
            if randint(0, 4):
                return Wreck(self)
            else:
                return PowerUp(self)
        else:
            return self

    def onRedraw(self, surface):
        rect = (self.position - self.size).couple() + (self.size * 2).couple()
        pygame.gfxdraw.box(surface, rect, self.color + (GLOBAL_ALPHA,))
        pygame.gfxdraw.rectangle(surface, rect, self.color)
        for i in self.cracks:
            pygame.draw.aaline(surface, self.color, i[0].intcpl(), i[1].intcpl())

    def onCollide(self, obstacle, point, normal):
        crashes[self.value() % 8].play()
        self.addCrack(point, normal)

    def value(self):
        return self.color[0] + self.color[1] * 3 + self.color[2] * 5

    def addCrack(self, point, normal):
        result = []
        tanget = rotate2(normal, (random() - 0.5) * 2.0)

        A = vec2(self.position.x - self.size.x, self.position.y + self.size.y - 1)
        B = vec2(self.position.x + self.size.x, self.position.y + self.size.y - 1)
        intersection = lineSegmentIntersect(point, tanget, A, B)
        if intersection:
            result.append(intersection)
           
        A = vec2(self.position.x - self.size.x, self.position.y - self.size.y)
        B = vec2(self.position.x + self.size.x - 1, self.position.y - self.size.y)
        intersection = lineSegmentIntersect(point, tanget, A, B)
        if intersection:
            result.append(intersection)

        if len(result) < 2:
            A = vec2(self.position.x + self.size.x - 1, self.position.y + self.size.y)
            B = vec2(self.position.x + self.size.x - 1, self.position.y - self.size.y)
            intersection = lineSegmentIntersect(point, tanget, A, B)
            if intersection:
                result.append(intersection)
           
        if len(result) < 2:
            A = vec2(self.position.x - self.size.x, self.position.y + self.size.y)
            B = vec2(self.position.x - self.size.x, self.position.y - self.size.y)
            intersection = lineSegmentIntersect(point, tanget, A, B)
            if intersection:
                result.append(intersection)

        if len(result) == 2:
            self.cracks.append(tuple(result))

class Bat:
    def __init__(self, position, size, sharedState):
        self.sharedState = sharedState
        self.type = ENTITY_BAT
        self.color = (0, 255, 0)
        self.size = size
        self.velocity = 0.0
        self._initBat(position, size)

    def onUpdate(self, delta, current):
        self.origin.x += delta * self.velocity
        l = self.left().x - self.half
        r = self.sharedState.roomSize.x - self.right().x - self.half
        if l < 0.0:
            self.origin.x -= l
        if r < 0.0:
            self.origin.x += r

    def onRedraw(self, surface):
        points = [ (x[0] + self.origin.x, x[1] + self.origin.y) for x in self.points ]
        pygame.gfxdraw.aapolygon(surface, points, self.color)
        pygame.draw.polygon(surface, self.color, points)

    def onCollide(self, obstacle, point, normal):
        if obstacle == POWERUP_SHORTEN:
            self.size = max(0, self.size - 1)
            position = +self.origin
            position.y -= self.radius
            self._initBat(position, self.size)
        elif obstacle == POWERUP_WIDEN:
            self.size = min(len(BAT_SIZES) - 1, self.size + 1)
            position = +self.origin
            position.y -= self.radius
            self._initBat(position, self.size)

    def left(self):
        return self.xleft + self.origin

    def right(self):
        return self.xright + self.origin

    def _initBat(self, position, size):
        self.origin = position + vec2(0.0, BAT_SIZES[size][0])
        self.radius = BAT_SIZES[size][0]
        self.half = BAT_SIZES[size][1] * 0.5
        self.angle = BAT_SIZES[size][2]
        self.xleft = vec2()
        self.xright = vec2()
        self.points = Bat._createBat(BAT_SIZES[size][0], BAT_SIZES[size][1], BAT_SIZES[size][2], self.xleft, self.xright)

    def _createBat(radius, thickness, angle, left, right):
        STEPS = int(radius / 10 * angle) 
        result = []
        alpha = angle / STEPS
        beta = alpha * 0.05
        # outer edge
        i = -angle
        center = vec2(0.0, 1.0) * radius
        while i < angle:
            p = rotate2(center, -i)
            result.append((-p).intcpl())
            i += alpha

        # left cap
        normal = rotate2(center, -i).normal() * (thickness * 0.5)
        origin = rotate2(center, -i).normal() * (radius - thickness * 0.5)
        left.x = -origin.x
        left.y = -origin.y
        i = 0.0
        while i < pi:
            p = rotate2(normal, -i)
            result.append((-origin - p).intcpl())
            i += beta

        # inner edge
        i = angle
        center = vec2(0.0, 1.0) * (radius - thickness)
        while i > -angle:
            p = rotate2(center, -i)
            result.append((-p).intcpl())
            i -= alpha

        # right cap
        normal = -rotate2(center, -i).normal() * (thickness * 0.5)
        origin = rotate2(center, -i).normal() * (radius - thickness * 0.5)
        right.x = -origin.x
        right.y = -origin.y
        i = 0.0
        while i < pi:
            p = rotate2(normal, -i)
            result.append((-origin - p).intcpl())
            i += beta

        return result

def multilineText(font, text, antialias, color, background):
    L = [font.render(x, antialias, color) for x in text.split('\n')]
    width = max(L, key = lambda x: x.get_size()[0]).get_size()[0]
    height = max(L, key = lambda x: x.get_size()[1]).get_size()[1]
    result = pygame.Surface((width, height * len(L)))
    for i in range(len(L)):
        result.blit(L[i], (0, i * height))
    return result