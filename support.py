from os import walk
import pygame as pg

def import_folder(path):
    surface_list = []
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_s = pg.image.load(full_path).convert_alpha()
            surface_list.append(image_s)
    return surface_list

def bg_animation(rect):
    if rect.y >= 5:
        rect.y -= 1


def title(rect):
    if rect.y > -300:
        rect.y -= 1


def falling_effect(rect):
    if rect.y <= -64:
        rect.y = 0
    else:
        rect.y -= 2


def bg_anim_fin(rect):
    # global game_state
    # esta función es solo para bg06_rect
    if rect.y >= 355:
        rect.y -= 61
        # return True
    # game_state = 2
    # return False
