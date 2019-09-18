# brief         part of ax-breakout game
# author        Wojciech Szęszoł keepitsimplesirius[at]gmail.com
# encoding      UTF-8 with BOM
# end of line   LF
# tab           4x space

import pygame
import threading
from pygame.locals import *

def Issue20891_workaround():
    # PyGILState_Ensure on non-Python thread causes fatal error

    class MyThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)

        def run (self):
            pass

    MyThread().start()

Issue20891_workaround()

# init pygame modules
pygame.init()
pygame.font.init()
pygame.mixer.init(buffer = 32)
if pygame.font.get_init() == False:
    input("Cannot initialize pygame.font module...")
if pygame.mixer.get_init() == False:
    input("Cannot initialize pygame.mixer module...")
pygame.mouse.set_visible(False)

from Entities import *
from Stages import *

screen = pygame.display.set_mode( (800, 600) )
quit = False

TIME_STEP = 0.002
oldTime = pygame.time.get_ticks() * 0.001
newTime = pygame.time.get_ticks() * 0.001
deltaTime = 0

sharedState = SharedState()
currentStage = sharedState.mainMenu

while not quit:
    # compute time
    newTime = pygame.time.get_ticks() * 0.001
    deltaTime += newTime - oldTime
    oldTime = newTime
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        else:
            currentStage.onHandle(event)
    # update state
    while deltaTime > TIME_STEP:
        currentStage = currentStage.onUpdate(TIME_STEP, newTime)
        if currentStage == None:
            quit = True
            break
        deltaTime -= TIME_STEP

    screen.fill((0, 0, 0))
    if currentStage != None:
        currentStage.onRedraw(screen)
    pygame.display.update()
