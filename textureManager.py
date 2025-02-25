import pygame
import os
from enum import Enum


class TextureName(Enum):
    MOUSE = 1
    SNAKE_HEAD = 2
    SNAKE_NODE = 3
    APPLE = 4
    TELEPORT = 5
    CHOCOLATE = 6
    LEMON = 7
    SLOW_BULLET = 8
    POISON = 9


class TextureManager:
    def __init__(self):
        self.textureDict = {
            TextureName.MOUSE: self.__loadAndGetImageByFileName("snake-mouse.png"),
            TextureName.SNAKE_HEAD: self.__loadAndGetImageByFileName(
                "snake-snake-head.png"
            ),
            TextureName.SNAKE_NODE: self.__loadAndGetImageByFileName(
                "snake-snake-node.png"
            ),
            TextureName.APPLE: self.__loadAndGetImageByFileName("snake-apple.png"),
            TextureName.TELEPORT: self.__loadAndGetImageByFileName(
                "snake-teleport.png"
            ),
            TextureName.CHOCOLATE: self.__loadAndGetImageByFileName(
                "snake-chocolate.png"
            ),
            TextureName.LEMON: self.__loadAndGetImageByFileName("snake-lemon.png"),
            TextureName.SLOW_BULLET: self.__loadAndGetImageByFileName(
                "snake-slow-bullet.png"
            ),
            TextureName.POISON: self.__loadAndGetImageByFileName("snake-poison.png"),
        }

    # private method
    def __loadAndGetImageByFileName(self, fileName):
        return pygame.image.load(os.path.join("images", fileName)).convert_alpha()

    def getTextureByName(self, name: TextureName):
        return self.textureDict[name]
