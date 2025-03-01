# Import and initialize the pygame library
import pygame
from pygame import Vector2
import random
import os
import constants
import utilities
from player import Player
import snake
import textureManager
import soundManager
from powerUp import PowerUp, TeleportInfo, PoisonInfo

pygame.init()
# you have to call this at the start, if you want to use this module.
pygame.font.init()
# you have to call this at the start, if you want to use this module.
pygame.mixer.init()
my_font = pygame.font.SysFont("Comic Sans MS", 30)


class App:
    def __init__(self):
        self.dt = 0  # delta time - seconds
        self.screen = pygame.display.set_mode(
            [constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT]
        )
        self.clock = pygame.time.Clock()
        self.objs = []
        self.player = None  # for Player reference
        self.remaningSpawnPowerTime = constants.POWER_UP_SPAWN_DELAY_TIME
        self.events = []
        self.isGameOver = False
        self.pressed_keys = []
        self.pressed_mouses = []
        self.playerPoint = 0
        self.snakeSpawnRemainingTime = constants.SNAKE_SPAWN_DELAY_TIME
        self.highlightBgRemainingTime = 0
        self.bgImage = textureManager.TextureName.GRASS

        # init managers
        self.textureManager = textureManager.TextureManager()
        self.soundManager = soundManager.SoundManager()

        # init observers
        self.observers: list[utilities.Observer] = []
        self.observers.append(self.soundManager)

    def getGameState(self) -> int:
        if self.playerPoint < 10:
            return 0
        if self.playerPoint < 20:
            return 1
        return 2

    # run per new game
    def reset(self):
        self.objs = []
        newSnake = snake.Snake(constants.START_SNAKE_X, constants.START_SNAKE_Y)
        player = Player()
        self.player = player
        self.objs.append(player)
        self.objs.append(newSnake)
        self.isGameOver = False
        self.playerPoint = 0
        self.snakeSpawnRemainingTime = constants.SNAKE_SPAWN_DELAY_TIME
        self.highlightBgRemainingTime = 0

    @staticmethod
    def checkAndHandleCollision(a, b):
        collisionSubjectsA = a.getCollisionSubjects()
        collisionSubjectsB = b.getCollisionSubjects()

        for i in collisionSubjectsA:
            for k in collisionSubjectsB:
                if (
                    not i.collisionComp.isDead
                    and not k.collisionComp.isDead
                    and i.collisionComp.checkCollision(k.collisionComp)
                ):
                    a.handleCollision(b)
                    b.handleCollision(a)
                    return

    def addObject(self, obj):
        self.objs.append(obj)

    def handleEvents(self):
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()

            if event.type == constants.PLAYER_DEAD_EVENT:
                self.isGameOver = True

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and self.isGameOver
            ):
                self.running = False

            if event.type == constants.SNAKE_SHOOT_BULLET_EVENT:
                self.onShootBullet(event.data)

            if event.type == constants.PLAYER_GET_APPLE_EVENT:
                self.playerPoint += 1
                self.upgradeToAllSnakes()
                self.highlightBgRemainingTime = constants.HIGHLIGHT_BG_TIME

            self.player.handleInputByEvent(event)
            self.notifyObservers(event)

    # notify event to all observers
    def notifyObservers(self, event):
        for observer in self.observers:
            observer.onNotify(event)

    def run(self):
        self.reset()
        self.running = True
        while self.running:
            # get events and handle
            self.events = pygame.event.get()
            self.handleEvents()

            # save input states
            # self.pressed_keys = pygame.key.get_pressed()
            # self.pressed_mouses = pygame.mouse.get_pressed()

            ## Update
            self.update()

            ## Draw
            self.draw()

            pygame.display.flip()
            self.dt = self.clock.tick(60) / 1000 * constants.GAME_SPEED_SCALE

        self.run()

    def onSpawnMoreSnake(self):
        # check max snake
        snakeCount = self.getObjCountByCondition(lambda obj: obj.name == "snake")
        if snakeCount >= constants.MAX_SNAKE_COUNT:
            return

        # add snake
        randomPos = self.getValidRandomTilePosition()
        newSnake = snake.Snake(randomPos.x, randomPos.y)
        self.addObject(newSnake)

    def onShootBullet(self, data: utilities.ShootBulletEventData):
        PowerUp.generateSlowBullet(self, data)

    def getAllCollisionSubjects(self):
        collisionSubjects = []
        for obj in self.objs:
            subjects: list = obj.getCollisionSubjects()
            collisionSubjects += subjects
        return collisionSubjects

    def update(self):
        if self.highlightBgRemainingTime > 0:
            self.highlightBgRemainingTime -= self.dt

        if self.isGameOver:
            return

        self.powerUpUpdate()
        self.snakeGeneratorUpdate()

        # update objs
        for x in self.objs:
            x.update(self)

        # detect and handle collision
        for x in range(
            0, len(self.objs) - 1
        ):  # [0 -> len - 2] because range ignores the last element
            for y in range(
                x + 1, len(self.objs)
            ):  # [x + 1 -> len - 1] because range ignores the last element
                App.checkAndHandleCollision(self.objs[x], self.objs[y])

        # remove destroyed objs
        for x in self.objs:
            if x.checkIsDead():
                self.objs.remove(x)

    def upgradeToAllSnakes(self):
        for obj in self.objs:
            if obj.name == "snake":
                obj.addLength()
                obj.updateBaseSpeed(
                    constants.SNAKE_SPEED + self.playerPoint / (self.playerPoint + 10)
                )

    def snakeGeneratorUpdate(self):
        self.snakeSpawnRemainingTime -= self.dt
        if self.snakeSpawnRemainingTime <= 0:
            self.onSpawnMoreSnake()
            self.snakeSpawnRemainingTime = constants.SNAKE_SPAWN_DELAY_TIME

    def powerUpUpdate(self):
        self.remaningSpawnPowerTime -= self.dt

        if self.remaningSpawnPowerTime <= 0:
            powerUpCount = self.getObjCountByCondition(
                lambda obj: obj.name == "power-up"
            )
            nextPowerUpSpawnTime = max(
                constants.MIN_POWER_UP_SPAWN_DELAY_TIME,
                constants.POWER_UP_SPAWN_DELAY_TIME - self.playerPoint / 30,
            )
            self.remaningSpawnPowerTime = nextPowerUpSpawnTime

            if powerUpCount < constants.MAX_POWER_UP_COUNT:
                if self.checkShouldGeneratePoison():
                    self.onGeneratePoision()
                else:
                    self.onGenerateRandomPower()

    def checkShouldGeneratePoison(self):
        if self.getGameState() == 0:
            return False

        checkPoisonObj = lambda obj: hasattr(obj, "powerInfo") and isinstance(
            obj.powerInfo, PoisonInfo
        )
        currentPoisonCount = self.getObjCountByCondition(checkPoisonObj)

        if currentPoisonCount >= 4:
            return False

        return random.randint(0, 3) == 0

    def onGeneratePoision(self):
        PowerUp.generatePoisonPower(self)

    def getRandomTilePosition(self) -> Vector2:
        randomX = random.randint(0, int(constants.GRID_SIZE.x) - 1)
        randomY = random.randint(0, int(constants.GRID_SIZE.y) - 1)
        return Vector2(randomX, randomY)

    def getValidRandomTilePosition(
        self,
        exclusionTiles: list = [],
        minExclusionDistance=constants.MIN_TWIN_TELEPORT_DISTANCE,
    ) -> Vector2:
        randomPos = Vector2(0, 0)
        success = False
        tryCount = 0
        while not success:
            success = True
            tryCount += 1
            if tryCount > 10000:
                raise Exception("too many position searches")
            randomPos = self.getRandomTilePosition()

            if randomPos in exclusionTiles:
                success = False
                continue

            for exclusionTile in exclusionTiles:
                distanceToExclusion = (randomPos - exclusionTile).length()
                if distanceToExclusion < minExclusionDistance:
                    success = False
                    break
            if not success:
                continue

            allCollisionSubjects = self.getAllCollisionSubjects()
            for x in allCollisionSubjects:
                vector: Vector2 = randomPos - x.collisionComp.position
                distance = vector.length()
                if distance < constants.MIN_POWER_UP_DISTANCE:
                    success = False
                    break

        return randomPos

    def getObjByCondition(self, cb):
        objs = []
        for obj in self.objs:
            if cb(obj):
                objs.append(obj)
        return objs

    def getObjCountByCondition(self, cb):
        count = 0
        for obj in self.objs:
            if cb(obj):
                count += 1
        return count

    def onGenerateRandomPower(self):
        # teleport count
        checkTeleportObj = lambda obj: hasattr(obj, "powerInfo") and isinstance(
            obj.powerInfo, TeleportInfo
        )
        teleCount = self.getObjCountByCondition(checkTeleportObj)

        # if teleCount >= 4 don't spawn more teleports
        maxPowerUpType = 5 if teleCount < 4 else 3
        randomInd = random.randint(0, maxPowerUpType)
        match randomInd:
            case 0:
                PowerUp.generateSpeedUpPower(self)
            case 1:
                PowerUp.generateResizePower(self)
            case 2:
                PowerUp.generateApplePower(self)
            case 3:
                PowerUp.generateApplePower(self)
            # > 3 -> spawn teleports
            case _:
                PowerUp.generateTeleportPower(self)

    def drawBackground(self):
        utilities.drawImage(
            self.screen,
            self.textureManager.getTextureByName(self.bgImage),
            constants.WINDOW_RECT.size,
        )
        highlightBgRatio = self.highlightBgRemainingTime / constants.HIGHLIGHT_BG_TIME
        bgColor = utilities.lerpColors(
            constants.BACKGROUND_COLOR, constants.HIGHLIGHT_BG_COLOR, highlightBgRatio
        )

        # Create a transparent surface
        transparent_bg = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        transparent_bg.fill(bgColor)  # Red with 20 alpha

        # Blit the transparent surface onto the main screen
        self.screen.blit(transparent_bg, (0, 0))

    def draw(self):
        self.drawBackground()

        # draw objs
        for x in self.objs:
            x.draw(self)

        # game over
        if self.isGameOver:
            txt = f"{self.playerPoint} POINT{"s" if self.playerPoint > 1 else ""} and You Lost! Hit 'SPACE' to play new game"
            text_surface = my_font.render(txt, False, "red")
            self.screen.blit(text_surface, (0, 0))
            return

        # draw player point
        playerSpeed = "{:.2f}".format(self.player.speed)
        playerSize = self.player.collisionComp.size
        txt = f"Points: {self.playerPoint}, Speed: {playerSpeed}, Size: {playerSize}"
        point_surface = my_font.render(txt, False, "black")
        self.screen.blit(point_surface, (0, 0))


App().run()
