# Import and initialize the pygame library
import pygame
import random
import constants
import utilities
from snake import *
from player import *
from powerUp import *

pygame.init()
pygame.font.init()  # you have to call this at the start,
# if you want to use this module.
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
        self.remaningSpawnPowerTime = 3
        self.events = []
        self.isGameOver = False
        self.pressed_keys = []
        self.pressed_mouses = []
        self.playerPoint = 0
        self.snakeSpawnRemainingTime = constants.SNAKE_SPAWN_DELAY_TIME

    def getGameState(self) -> int:
        if self.playerPoint < 10:
            return 0
        if self.playerPoint < 20:
            return 1
        return 2

    # run per new game
    def reset(self):
        self.objs = []
        snake = Snake(constants.START_SNAKE_X, constants.START_SNAKE_Y)
        player = Player()
        self.player = player
        self.objs.append(player)
        self.objs.append(snake)
        self.isGameOver = False
        self.playerPoint = 0
        self.snakeSpawnRemainingTime = constants.SNAKE_SPAWN_DELAY_TIME

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

    def run(self):
        self.reset()
        running = True
        while running:
            # Did the user click the window close button?
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

                if event.type == constants.PLAYER_DEAD_EVENT:
                    self.isGameOver = True

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                    and self.isGameOver
                ):
                    running = False

                if event.type == constants.SNAKE_SHOOT_BULLET_EVENT:
                    self.onShootBullet(event.data)
                    print("shoot")

                if event.type == constants.GOT_FRUIT_EVENT:
                    self.playerPoint += 1
                    self.speedUpToAllSnakes()

                self.player.handleEvent(event)

            self.pressed_keys = pygame.key.get_pressed()
            self.pressed_mouses = pygame.mouse.get_pressed()

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
        snake = Snake(randomPos.x, randomPos.y)
        self.addObject(snake)

    def onShootBullet(self, data: utilities.ShootBulletEventData):
        PowerUp.generateSlowBullet(self, data)

    def getAllCollisionSubjects(self):
        collisionSubjects = []
        for obj in self.objs:
            subjects: list = obj.getCollisionSubjects()
            collisionSubjects += subjects
        return collisionSubjects

    def update(self):
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

    def speedUpToAllSnakes(self):
        for obj in self.objs:
            if obj.name == "snake":
                obj.speed = constants.SNAKE_SPEED + self.playerPoint / 10

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
            self.remaningSpawnPowerTime = constants.POWER_UP_SPAWN_DELAY_TIME
            if powerUpCount < constants.MAX_POWER_UP_COUNT:
                self.onGenerateRandomPower()

    def getRandomTilePosition(self) -> Vector2:
        randomX = random.randint(0, int(constants.GRID_SIZE.x) - 1)
        randomY = random.randint(0, int(constants.GRID_SIZE.y) - 1)
        return Vector2(randomX, randomY)

    def getValidRandomTilePosition(
        self, exclusionTiles: list = [], minExclusionDistance=20
    ) -> Vector2:
        randomPos = Vector2(0, 0)
        success = False
        tryCount = 0
        while not success:
            success = True
            tryCount += 1
            if tryCount > 100:
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
                if distance < 4:
                    success = False
                    break

        return randomPos

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
        maxPowerUpType = 6 if teleCount < 4 else 3
        randomInd = random.randint(0, maxPowerUpType)
        match randomInd:
            case 0:
                PowerUp.generateSpeedUpPower(self)
            case 1:
                PowerUp.generateResizePower(self)
            case 2:
                PowerUp.generateFruitPower(self)
            case 3:
                PowerUp.generateFruitPower(self)
            # any other number
            case _:
                PowerUp.generateTeleportPower(self)

    def draw(self):
        self.screen.fill((0, 0, 0))  # clean screen
        # game over
        if self.isGameOver:
            text_surface = my_font.render(
                "You Lose! Hit 'SPACE' to play new game", False, (255, 255, 0)
            )
            self.screen.blit(text_surface, (0, 0))
            return

        self.drawGrid()

        # draw objs
        for x in self.objs:
            x.draw(self)

        # draw player point
        point_surface = my_font.render(
            f"Point: {self.playerPoint}, Objs: {self.objs.__len__()}, Speed: {self.player.speed}",
            False,
            (255, 255, 0),
        )
        self.screen.blit(point_surface, (0, 0))

    def drawGrid(self):
        for x in range(0, constants.WINDOW_WIDTH, int(constants.TILE_SIZE.x)):
            pygame.draw.line(
                self.screen, constants.GRID_COLOR, (x, 0), (x, constants.WINDOW_HEIGHT)
            )

        for y in range(0, constants.WINDOW_HEIGHT, int(constants.TILE_SIZE.y)):
            pygame.draw.line(
                self.screen, constants.GRID_COLOR, (0, y), (constants.WINDOW_WIDTH, y)
            )


App().run()
