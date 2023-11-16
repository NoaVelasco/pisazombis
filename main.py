#!/usr/bin/env python3.11
# Python 3.11.0 UTF-8
# Copyright (c) 2023, Noa Velasco
# pylint: disable=C0103
'''Pisazombis is an arcade game where Mikecrack
hits zombies before he lands from cracking buildings.'''
import sys
from settings import DISPLAY
from game import SceneManager
import pygame as pg


def main():
    """Initialize the game"""
    pg.init()
    screen = pg.display.set_mode((DISPLAY))
    pg.display.set_caption("Pisazombis")
    timer = pg.time.Clock()

    bg_music = pg.mixer.Sound("snd/chocoalmendras.mp3")
    bg_music.set_volume(0.5)
    bg_music.play(loops = -1)

    # Para manejar las escenas desde .game
    manager = SceneManager()

    # Bucle general. Los eventos se pasan a la escena correspondiente
    # y la escena maneja los updates.
    while True:
        if pg.event.get(pg.QUIT):
            pg.quit()
            sys.exit()
        manager.scene.handle_events(pg.event.get())
        manager.scene.update()
        manager.scene.render(screen)
        pg.display.update()
        timer.tick(60)


if __name__ == "__main__":
    main()
