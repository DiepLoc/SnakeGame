import pygame
import os
import constants
import utilities
from enum import Enum


class SoundName(Enum):
    PICK_UP_POINT = 1
    POWER_UP = 2  # for lemon, chocolate pick up
    TELEPORT = 3
    HIT_SLOW = 4
    DEAD = 5


class SoundManager(utilities.Observer):
    def __init__(self):
        self.soundDict = {
            SoundName.PICK_UP_POINT: self.__loadSound("Pickup_point.wav"),
            SoundName.POWER_UP: self.__loadSound("Power_up.wav"),
            SoundName.TELEPORT: self.__loadSound("Teleport.wav"),
            SoundName.HIT_SLOW: self.__loadSound("Hit_slow.wav"),
            SoundName.DEAD: self.__loadSound("Dead.wav"),
        }

    def __loadSound(self, soundFileName):
        return pygame.mixer.Sound(os.path.join("sounds", soundFileName))

    def __getSoundByName(self, name: SoundName):
        return self.soundDict[name]

    def onNotify(self, event: pygame.event.Event):
        if event.type == constants.PLAYER_GET_APPLE_EVENT:
            self.__getSoundByName(SoundName.PICK_UP_POINT).play()
        elif (
            event.type == constants.PLAYER_GET_LEMON_EVENT
            or event.type == constants.PLAYER_GET_CHOCOLATE_EVENT
        ):
            self.__getSoundByName(SoundName.POWER_UP).play()
        elif event.type == constants.PLAYER_HIT_SLOW_BULLET_EVENT:
            self.__getSoundByName(SoundName.HIT_SLOW).play()
        elif event.type == constants.PLAYER_GET_TELEPORT_EVENT:
            self.__getSoundByName(SoundName.TELEPORT).play()
        elif event.type == constants.PLAYER_DEAD_EVENT:
            self.__getSoundByName(SoundName.DEAD).play()
