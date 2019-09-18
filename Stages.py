# brief         part of ax-breakout game
# author        Wojciech Szęszoł keepitsimplesirius[at]gmail.com
# encoding      UTF-8 with BOM
# end of line   LF
# tab           4x space

import pickle
from Entities import *

BAT_VERTICAL_POSITION = 36
BAT_VELOCITY = 1000.0
BALL_VERTICAL_POSITON = 100
FONT_COLOR = (255, 255, 0)
HIGHLIGHT_COLOR = (0, 0, 255)
MENU_NUMBER = 5
CONTINUE = 4
NEW_GAME = 3
CREDITS = 1
HIGH_SCORES = 2
EXIT = 0
TABLE_WIDTH = 0.7
START_LIVES = 3

class SharedState:
    def __init__(self):
        self.roomSize = vec2(800, 600)
        self.bricky = vec2(800, 400)
        self.smallFont = pygame.font.Font("data/atari.ttf", 32)
        self.bigFont = pygame.font.Font("data/atari.ttf", 64)
        self.loadSprites()
        self.gameStage = GameStage(self)
        self.highScores = HighScores(self)
        self.credits = Credits(self)
        self.mainMenu = MainMenu(self)
        self.gameOver = GameOver(self)

    def loadSprites(self):
        self.powerups = [POWERUP_NUMBER] * 6
        self.powerups[POWERUP_SHORTEN] = pygame.image.load("data/shorten.png")
        self.powerups[POWERUP_WIDEN] = pygame.image.load("data/widen.png")
        self.powerups[POWERUP_LIVE] = pygame.image.load("data/live.png")
        self.powerups[POWERUP_BALL] = pygame.image.load("data/ball.png")
        self.powerups[POWERUP_SPEED_UP] = pygame.image.load("data/speedup.png")
        self.powerups[POWERUP_SLOW_DOWN] = pygame.image.load("data/slowdown.png")

class GameStage:
    def __init__(self, sharedState):
        self.sharedState = sharedState
        self.nextStage = self
        self.quadTree = None

        self.bricks = []
        self.wrecks = []
        self.powerups = []
        self.balls = []
        self.bat = None
        
        self.score = 0
        self.level = 0
        self.lives = 0

    def onHandle(self, event):
        if self.bat != None:
            if event.type == KEYDOWN or event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.sharedState.mainMenu.enableReturn()
                    self.nextStage = self.sharedState.mainMenu
                    self.sharedState.mainMenu.nextStage = self.sharedState.mainMenu
                else:
                    state = pygame.key.get_pressed()
                    if state[K_a] or state[K_LEFT]:
                        self.bat.velocity = -BAT_VELOCITY
                    elif state[K_d] or state[K_RIGHT]:
                        self.bat.velocity = BAT_VELOCITY
                    else:
                        self.bat.velocity = 0.0
            elif event.type == MOUSEMOTION:
                self.bat.velocity = 0
                self.bat.origin.x += event.rel[0]

    def onUpdate(self, delta, current):
        if self.lives == 0:
            self.gameOver()
        else:
            if len(self.bricks) == 0:
                self.loadNextLevel()
            else:
                self.checkCollisions()

                i = 0; s = len(self.bricks)
                while i < s:
                    brick = self.bricks[i].onUpdate(delta, current)
                    if brick.type == ENTITY_WRECK:
                        self.wrecks.append(brick)
                    elif brick.type == ENTITY_POWERUP:
                        brick.init(self.sharedState)
                        self.powerups.append(brick)
                    if brick.type != ENTITY_BRICK:
                        self.quadTree.remove(self.bricks[i])
                        self.score += self.bricks[i].value() % 8 * 3
                        del self.bricks[i]
                        i -= 1
                        s -= 1
                    i += 1

                for ball in self.balls:
                    ball.onUpdate(delta, current)

                i = 0; s = len(self.wrecks)
                while i < s:
                    wreck = self.wrecks[i].onUpdate(delta, current)
                    if wreck == None:
                        del self.wrecks[i]
                        i -= 1
                        s -= 1
                    i += 1

                i = 0; s = len(self.powerups)
                while i < s:
                    powerup = self.powerups[i].onUpdate(delta, current)
                    if powerup == None:
                        del self.powerups[i]
                        i -= 1
                        s -= 1
                    i += 1

                if self.bat != None:
                    self.bat.onUpdate(delta, current)
        return self.nextStage

    def onRedraw(self, surface):
        for wreck in self.wrecks:
            wreck.onRedraw(surface)
        for brick in self.bricks:
            brick.onRedraw(surface)
        for ball in self.balls:
            ball.onRedraw(surface)
        for powerup in self.powerups:
            powerup.onRedraw(surface)
        if self.bat != None:
            self.bat.onRedraw(surface)
        self.redrawHUD(surface)

    def loadTestLevel(self):
        bat_position = +self.sharedState.roomSize
        bat_position.x *= 0.5
        bat_position.y -= BAT_VERTICAL_POSITION
        self.bat = Bat(bat_position, 1, self.sharedState)
        ball_position = +self.sharedState.roomSize
        ball_position.x *= 0.5
        ball_position.y *= 0.5
        self.balls.append(Ball(ball_position, 5, (255, 255, 255)))

        for x in range(int(self.sharedState.roomSize.x) // 50):
            self.bricks.append(Brick(vec2(x * 50, 100), vec2(15, 15), (255, 0, 0)))
    
        for x in range(int(self.sharedState.roomSize.x) // 50):
            self.bricks.append(Brick(vec2(x * 50, 200), vec2(15, 15), (0, 255, 0)))

        for x in range(int(self.sharedState.roomSize.x) // 50):
            self.bricks.append(Brick(vec2(x * 50, 400), vec2(15, 15), (0, 0, 255)))

    def loadNextLevel(self):
        self.level += 1
        self.bricks = []
        self.balls = []
        self.wrecks = []
        self.powerups = []
        try:
            lines = open("data/level" + str(self.level) + ".dat").readlines()
            for l in lines:
                line = l.split()
                if line[0] == 'b':
                    position = vec2(float(line[1]), float(line[2]))
                    size = vec2(float(line[3]), float(line[4]))
                    color = int(line[5]), int(line[6]), int(line[7])
                    self.bricks.append(Brick(position, size, color))
        
            self.quadTree = QuadTree(self.sharedState.bricky * 0.5, self.sharedState.bricky * 0.5,  5)
            for brick in self.bricks:
                self.quadTree.insert(brick)

            bat_position = +self.sharedState.roomSize
            bat_position.x *= 0.5
            bat_position.y -= BAT_VERTICAL_POSITION
            self.bat = Bat(bat_position, 1, self.sharedState)
            ball_position = +self.sharedState.roomSize
            ball_position.x *= 0.5
            ball_position.y -= BALL_VERTICAL_POSITON
            self.balls.append(Ball(ball_position, 5, (255, 255, 255)))
        except:
            self.gameOver()

    def loadFirstLevel(self):
        self.score = 0
        self.level = 0
        self.lives = START_LIVES
        self.loadNextLevel()

    def gameOver(self):
        self.sharedState.gameOver.setScore(self.score)
        self.nextStage = self.sharedState.gameOver
        self.sharedState.gameOver.nextStage = self.sharedState.gameOver
        self.sharedState.mainMenu.enabled = False

    def checkCollisions(self):
        for c in self.balls:
            possible = self.quadTree.collide(c)
            for r in possible:
                couple = circleRectangleCollide(c.position, c.radius, r.position, r.size)
                if couple:
                    r.onCollide(c.type, couple[0], -couple[1])
                    c.onCollide(r.type, couple[0], couple[1])

            couple = circleSectorCollide(c.position, c.radius, self.bat.origin, self.bat.radius, self.bat.angle)
            if not couple:
                couple = circleCircleCollide(c.position, c.radius, self.bat.left(), self.bat.half)
            if not couple:
                couple = circleCircleCollide(c.position, c.radius, self.bat.right(), self.bat.half)
            if couple:
                self.bat.onCollide(c.type, couple[0], -couple[1])
                c.onCollide(self.bat.type, couple[0], couple[1])
            
            for cc in self.balls:
                if cc.position != c.position:
                    couple = circleCircleCollide(c.position, c.radius, cc.position, cc.radius)
                    if couple:
                        c.onCollide(cc.type, couple[0], couple[1])
                        cc.onCollide(c.type, couple[1], -couple[1])

        i = 0; s = len(self.balls)
        while i < s:
            c = self.balls[i]
            couple = circleInsideCollision(c.position, c.radius, self.sharedState.roomSize * 0.5, self.sharedState.roomSize * 0.5)
            if couple:
                c.onCollide(ENTITY_BORDER, couple[0], couple[1])
                if c.wait == 0.0:
                    if s > 1:
                        del self.balls[i]
                        i -= 1
                        s -= 1
                    else:
                        self.lives -= 1
            i += 1

        for c in self.powerups:
            couple = circleSectorCollide(c.position, c.radius, self.bat.origin, self.bat.radius, self.bat.angle)
            if not couple:
                couple = circleCircleCollide(c.position, c.radius, self.bat.left(), self.bat.half)
            if not couple:
                couple = circleCircleCollide(c.position, c.radius, self.bat.right(), self.bat.half)
            if couple:
                if c.bonus == POWERUP_BALL:
                    self.balls.append(self.balls[-1].copy())
                elif c.bonus == POWERUP_LIVE:
                    self.lives += 1
                elif c.bonus == POWERUP_SPEED_UP:
                    for ball in self.balls:
                        ball.speedUp()
                elif c.bonus == POWERUP_SLOW_DOWN:
                    for ball in self.balls:
                        ball.slowDown()
                self.bat.onCollide(c.bonus, couple[0], -couple[1])
                c.onCollide(self.bat.type, couple[0], couple[1])
    
    def redrawHUD(self, surface):
        score = self.sharedState.smallFont.render("SCORE: " + str(self.score), True, (255, 255, 0))
        lives = self.sharedState.smallFont.render("LIVES: " + str(self.lives), True, (255, 255, 0))
        surface.blit(score, (0, 0))
        surface.blit(lives, (surface.get_size()[0] - lives.get_size()[0], 0))

class MainMenu:
    def __init__(self, sharedState):
        self.sharedState = sharedState
        self.nextStage = self
        self.position = NEW_GAME
        self.labels = [None] * MENU_NUMBER
        self.enabled = False
        self.labels[4] = sharedState.bigFont.render("CONTINUE", True, FONT_COLOR)
        self.labels[3] = sharedState.bigFont.render("NEW GAME", True, FONT_COLOR)
        self.labels[2] = sharedState.bigFont.render("HIGH SCORES", True, FONT_COLOR)
        self.labels[1] = sharedState.bigFont.render("CREDITS", True, FONT_COLOR)
        self.labels[0] = sharedState.bigFont.render("EXIT",  True, FONT_COLOR)

    def onHandle(self, event):
        if event.type == KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                self.position = (self.position + 1) % (len(self.labels)- int(not self.enabled))
            elif event.key == K_s or event.key == K_DOWN:
                self.position = (self.position - 1) % (len(self.labels) - int(not self.enabled))
            elif event.key == K_RETURN:
                if self.position == CONTINUE:
                    self.nextStage = self.sharedState.gameStage
                    self.sharedState.gameStage.nextStage = self.sharedState.gameStage
                elif self.position == NEW_GAME: 
                    self.sharedState.gameStage.loadFirstLevel()
                    self.nextStage = self.sharedState.gameStage
                    self.sharedState.gameStage.nextStage = self.sharedState.gameStage
                elif self.position == HIGH_SCORES:
                    self.nextStage = self.sharedState.highScores
                    self.sharedState.highScores.nextStage = self.sharedState.highScores
                elif self.position == CREDITS:
                    self.nextStage = self.sharedState.credits
                    self.sharedState.credits.nextStage = self.sharedState.credits
                elif self.position == EXIT:
                    self.nextStage = None
            elif event.key == K_ESCAPE:
                if self.position == EXIT:
                    self.nextStage = None
                else:
                    self.position = EXIT

    def onUpdate(self, delta, current):
        return self.nextStage

    def onRedraw(self, surface):
        height = self.sharedState.bigFont.get_height() * 2
        offset = surface.get_size()[1] - height * (MENU_NUMBER)
        for i in range(MENU_NUMBER - int(not self.enabled)):
            if i == self.position:
                rect = (0, (MENU_NUMBER - i - 1) * height + offset) + self.labels[i].get_size()
                pygame.gfxdraw.box(surface, rect, HIGHLIGHT_COLOR + (GLOBAL_ALPHA,))
                pygame.gfxdraw.rectangle(surface, rect, HIGHLIGHT_COLOR)
            surface.blit(self.labels[i], (0, (MENU_NUMBER - i - 1) * height + offset))

    def enableReturn(self):
        self.enabled = True
        self.position = CONTINUE

class Credits:
    def __init__(self, sharedState):
        self.sharedState = sharedState
        self.nextStage = self
        self.text = multilineText(sharedState.smallFont, "ax-breakout by\n\nWojciech Szeszol\n\natari1.ttf font from\n\nwww.dafont.com\n\nversion 1.0\n\nkeepitsimplesirius\n[at]gmail.com", True, FONT_COLOR, None)

    def onHandle(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.nextStage = self.sharedState.mainMenu
            self.sharedState.mainMenu.nextStage = self.sharedState.mainMenu

    def onUpdate(self, delta, current):
        return self.nextStage

    def onRedraw(self, surface):
        surface.blit(self.text, (0, surface.get_size()[1] - self.text.get_size()[1]) + self.text.get_size())

class HighScores:
    def __init__(self, sharedState):
        self.sharedState = sharedState
        self.nextStage = self
        file = None
        try:
            file = open("data/player.dat", "rb")
        except IOError:
            file = None
        if file != None:
            self.score_list = pickle.load(file)
        else:
            self.score_list = [("Unknown", 0)] * 10
        self.score_cache = None
        self.head = sharedState.bigFont.render("high scores", True, (255, 255, 0))
        self.back = False

    def addScore(self, name, score):
        self.score_list.append((name, score))
        self.score_list.sort(key = lambda x: -x[1])
        if len(self.score_list) > 10:
            self.score_list = self.score_list[0:10]
        file = open("data/player.dat", "wb+")
        pickle.dump(self.score_list, file)
        self.score_cache = None
        
    def renderCache(self, width):
        names = [self.sharedState.smallFont.render(self.score_list[x][0], True, (255, 255, 0)) for x in range(len(self.score_list))]
        scores = [self.sharedState.smallFont.render(str(self.score_list[x][1]), True, (255, 255, 0)) for x in range(len(self.score_list))]
        height = names[0].get_size()[1]
        self.score_cache = pygame.Surface((width * TABLE_WIDTH, height * len(scores)))
        for i in range(len(scores)):
            self.score_cache.blit(names[i], (0, height * i))
            self.score_cache.blit(scores[i], (width * TABLE_WIDTH - scores[i].get_size()[0], height * i))

    def onHandle(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.nextStage = self.sharedState.mainMenu
            self.sharedState.mainMenu.nextStage = self.sharedState.mainMenu

    def onUpdate(self, delta, current):
        return self.nextStage
    
    def onRedraw(self, surface):
        if self.score_cache == None:
            self.renderCache(surface.get_size()[0])
        cache_size = self.score_cache.get_size()
        head_size = self.head.get_size()
        surface_size = surface.get_size()
        surface.blit(self.head, ((surface_size[0] - head_size[0]) // 2, int(surface_size[1] - head_size[1] * 1.5 - cache_size[1]) // 2))
        surface.blit(self.score_cache, ((surface_size[0] - cache_size[0]) // 2, int(surface_size[1] - head_size[1] * 0.5 - cache_size[1]) // 2 + head_size[1]))

class GameOver:
    def __init__(self, sharedState):
        self.sharedState = sharedState
        self.nextStage = self
        self.name = ""
        self.score = 0
        self.head = multilineText(sharedState.smallFont, "GAME OVER\nGIVE YOUR NAME:", True, FONT_COLOR, None)
        self.done = False

    def setScore(self, score):
        self.score = score

    def onHandle(self, event):
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE and len(self.name) != 0:
                self.name = self.name[0:-1]
            if ('a' <= event.unicode and event.unicode <= 'z') or ('A' <= event.unicode and event.unicode <= 'Z'):
                self.name += event.unicode
            if event.key == K_RETURN:
                self.nextStage = self.sharedState.highScores
                self.sharedState.highScores.nextStage = self.sharedState.highScores

    def onUpdate(self, delta, current):
        if self.nextStage != self:
            if self.name != "":
                self.sharedState.highScores.addScore(self.name, self.score)
                self.name = ""
        return self.nextStage
    
    def onRedraw(self, surface):
        name = self.sharedState.smallFont.render(self.name, True, FONT_COLOR)
        name_size = name.get_size()
        head_size = self.head.get_size()
        surface_size = surface.get_size()
        surface.blit(self.head, (0, (surface_size[1] - head_size[1] - name_size[1]) // 2))
        surface.blit(name, (0, (surface_size[1] - head_size[1] - name_size[1]) // 2 + head_size[1]))
