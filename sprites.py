from random import randint, choice
from settings import *
from support import import_folder
import pygame as pg
from pygame.image import load


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # animations
        self.import_images()

        self.animation_index = 0
        self.animation_speed = 0.20
        self.image = self.animations["idle"][self.animation_index]
        self.rect = self.image.get_rect()
        self.rect.center = (250, 50)

        # Rect más pequeño para colisiones. Debe moverse con el rect original.
        # NUEVO. Tendré que actualizar los collides para comprobarlo
        self.collide_rect = pg.rect.Rect(0, 0, 45, 80)
        self.collide_rect.midbottom = self.rect.midbottom
        # FIN DE LO NUEVO ------------------------------------------

        self.mask = pg.mask.from_surface(self.image)

        # estados: idle, land, landed, hit, jump
        self.animation_status = "idle"

        self.gravity = 1
        self.movement = 3
        # señala si mira a derecha (True) o a izquierda (False).
        self.flipped = False

    def import_images(self):
        self.animations = {"idle": [], "jump": [], "hit": [], "land": []}
        for animation in self.animations.keys():
            full_path = PLAYER_PATH + animation
            self.animations[animation] = import_folder(full_path)

    def player_input(self):
        """Movimiento con botones de dirección."""
        # Si cae por debajo de 650 de y, se detiene.
        if self.rect.bottom <= 650:
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] and self.rect.left >= 65:
                self.flipped = False
                self.rect.x -= self.movement
                self.collide_rect.midbottom = self.rect.midbottom
            if keys[pg.K_RIGHT] and self.rect.right <= 435:
                self.flipped = True
                self.rect.x += self.movement
                self.collide_rect.midbottom = self.rect.midbottom

    def fall_gravity(self):
        """Velocidad de caída, animaciones y límites."""
        # Si pisa un zombi y la gravedad baja por el salto:
        if self.gravity <= 0:
            self.gravity += 1
        self.rect.y += self.gravity
        self.rect.bottom = min(self.rect.bottom, 680)
        self.rect.top = max(self.rect.top, 0)
        self.collide_rect.midbottom = self.rect.midbottom

    def end_check(self):
        """Comprueba si ha tocado fondo."""
        if self.rect.bottom >= 650:
            self.animation_status = "land"
            if self.rect.bottom >= 675:
                self.animation_status = "landed"
        elif self.rect.bottom <= 650 and self.animation_status in ["landed", "land"]:
            self.animation_status = "idle"

    def get_status(self):
        """Maneja los frames de animación."""
        if self.gravity < 1:
            self.jump()
        elif self.animation_status == "hit":
            self.beated()
        elif self.animation_status == "land":
            self.landing()
        elif self.animation_status == "landed":
            self.landed()
        else:
            self.falls()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pg.mask.from_surface(self.image)

    def falls(self):
        animation = self.animations["idle"]
        self.animation_index += 0.15
        if self.animation_index >= len(animation):
            self.animation_index = 0
        if self.flipped:
            self.image = pg.transform.flip(animation[int(self.animation_index)], 1, 0)
        else:
            self.image = animation[int(self.animation_index)]

    def jump(self):
        """Al chocar con un zombi, salta."""
        animation = self.animations["jump"]
        if self.animation_index < 1:
            self.animation_index += 0.25
        if self.flipped:
            self.image = pg.transform.flip(animation[int(self.animation_index)], 1, 0)
        else:
            self.image = animation[int(self.animation_index)]

    def beated(self):
        """Animación cuando choca con un objeto."""
        animation = self.animations["hit"]

        if self.animation_index < len(animation) - 0.25:
            self.animation_index += 0.15
            if self.flipped:
                self.image = pg.transform.flip(
                    animation[int(self.animation_index)], 1, 0
                )
            else:
                self.image = animation[int(self.animation_index)]
        else:
            self.animation_index = 0
            self.animation_status = "idle"

    def landing(self):
        animation = self.animations["land"]
        if self.flipped:
            self.image = pg.transform.flip(animation[0], 1, 0)
        else:
            self.image = animation[0]
        # animation = self.animations["land"]
        # if self.animation_index < 1:
        #     self.animation_index += 0.25
        # if self.flipped:
        #     self.image = pg.transform.flip(animation[int(self.animation_index)], 1, 0)
        # else:
        #     self.image = animation[int(self.animation_index)]

    def landed(self):
        animation = self.animations["land"]
        if self.flipped:
            self.image = pg.transform.flip(animation[1], 1, 0)
        else:
            self.image = animation[1]

    def update(self):
        """Actualiza mediante sus propios métodos."""
        self.player_input()
        self.fall_gravity()
        self.end_check()
        self.get_status()


class Zombie(pg.sprite.Sprite):
    def __init__(self, time):
        super().__init__()
        self.zombi = load(Z_STND).convert_alpha()
        self.boom = load(Z_XPL).convert_alpha()

        self.image = self.zombi
        x_pos, y_pos = randint(80, 400), randint(750, 1250)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
        self.mask = pg.mask.from_surface(self.image)

        if time <= 20000:
            self.speed = randint(3, 6)
        elif 20000 < time < 40000:
            self.speed = randint(5, 9)
        else:
            self.speed = randint(10, 18)

        self.angle = 0
        self.rot_vel = randint(-200, 200)
        self.flip = randint(0, 1)
        self.dead = False
        self.fade = 255
        self.spawn()

    def spawn(self):
        if self.flip:
            self.zombi = pg.transform.flip(self.zombi, 1, 0)
            self.image = self.zombi

    def move(self):
        self.rect.y -= self.speed
        if self.flip:
            self.angle += self.speed
            self.image = pg.transform.flip(load(Z_STND).convert_alpha(), 1, 0)
            self.image = pg.transform.rotozoom(self.image, self.angle / 3, 1)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pg.mask.from_surface(self.image)
        else:
            self.angle -= self.speed
            self.image = pg.transform.rotozoom(
                load(Z_STND).convert_alpha(), self.angle / 3, 1
            )
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pg.mask.from_surface(self.image)

    def smashed(self):
        if self.fade <= 0:
            self.kill()
        self.image = self.boom
        self.boom.set_alpha(self.fade)
        self.fade -= 20

    def update(self):
        if self.dead is False:
            self.move()
            self.destroy()
        else:
            self.smashed()

    def destroy(self):
        if self.rect.bottom <= 0:
            self.kill()


class Cloud(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        alpha = randint(20, 100)
        scale = randint(20, 80) / 100
        cloud01_surf = pg.transform.scale_by(load(CLD_1).convert_alpha(), scale)
        cloud02_surf = pg.transform.scale_by(load(CLD_2).convert_alpha(), scale)
        cloud03_surf = pg.transform.scale_by(load(CLD_3).convert_alpha(), scale)
        self.image = choice([cloud01_surf, cloud02_surf, cloud03_surf])
        self.image.set_alpha(alpha)

        x_pos, y_pos = randint(10, 300), randint(750, 1250)
        self.rect = self.image.get_rect(topleft=(x_pos, y_pos))

        self.speed = randint(1, 4)

    def update(self):
        if self.rect.bottom <= 0:
            self.kill()
        else:
            self.rect.y -= self.speed


class Bolardos(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.boom = load(Z_XPL).convert_alpha()

        xtinguisher = pg.transform.scale2x(load(O_XTING).convert_alpha())
        barrel = pg.transform.scale2x(load(O_BARREL).convert_alpha())
        self.image = choice([xtinguisher, barrel])
        x_pos, y_pos = randint(150, 350), randint(750, 1250)
        self.rect = self.image.get_rect(midtop=(x_pos, y_pos))
        # self.mask = pg.mask.from_surface(self.image)
        self.speed = randint(1, 8)
        self.fade = 255
        self.destroyed = False

    def smashed(self):
        if self.fade <= 0:
            self.kill()
        self.image = pg.transform.scale_by(self.boom, self.fade / 255)
        self.boom.set_alpha(self.fade)
        self.fade -= 51

    def update(self):
        if self.rect.bottom <= 0:
            self.kill()
        elif self.destroyed:
            self.smashed()
        else:
            self.rect.y -= self.speed
