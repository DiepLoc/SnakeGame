import pygame
import constants


class Snake:
    def __init__(self):
        self.head = SnakeHead(0, 0)
        self.nodes = []
        self.speed = 1  # tiles per second
        self.remainingMoveTime = 0

    def update(self, dt):
        self.remainingMoveTime -= dt
        if self.remainingMoveTime <= 0:
            self.remainingMoveTime = 1 / self.speed
            self.onMove()

    def onMove(self):
        for i in range(len(self.nodes) - 1, 0, -1):
            self.nodes[i].update(self.nodes[i - 1])

        if len(self.nodes) > 0:
            self.nodes[0].update(self.head)
        self.head.update(pygame.math.Vector2(1, 0))

    def draw(self, window, dt):
        self.head.draw(window)
        for x in self.nodes:
            x.draw(window)


class SnakeNode:
    def __init__(self, x, y):
        self.position = pygame.math.Vector2(x, y)
        pass

    def update(self, nextNode):
        self.updatePosition(nextNode.position)

    def updatePosition(self, newPos):
        self.position = newPos

    def draw(self, window: pygame.surface):
        center = self.position + pygame.math.Vector2(0.5, 0.5)
        pygame.draw.circle(
            window,
            (155, 155, 155),
            pygame.math.Vector2(
                center.x * constants.tileSize.x, center.y * constants.tileSize.y
            ),
            constants.tileSize.x / 2,
        )


class SnakeHead(SnakeNode):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self, vecDir: pygame.math.Vector2):
        if vecDir.length_squared != 0:
            self.updatePosition(self.position + vecDir.normalize())

    def draw(self, window: pygame.surface):
        super().draw(window)
