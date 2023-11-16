from random import randint
import time
from settings import *
from support import *
from sprites import *
import pygame as pg
from pygame.image import load


class TitleScene:
    """Pantalla de inicio"""

    def __init__(self):
        super().__init__()
        font_pixel = pg.font.Font(FNT_MONO, 20)
        self.fontstart_surf = font_pixel.render(
            "PARA JUGAR PULSA ESPACIO", False, GREEN
        )
        self.fontstart_rect = self.fontstart_surf.get_rect(center=(250, 100))
        self.title_surf = load(GUI_MAIN).convert()
        self.pisazombis_surf = load(GUI_TIT).convert_alpha()
        self.pisazombis_rect = self.pisazombis_surf.get_rect(topleft=(60, 300))
        self.blink = 0

    def press_start(self):
        """Hace parpadear el aviso de presionar tecla de inicio."""
        self.blink += 1
        if self.blink % 60 >= 10:
            return True
        return False

    def render(self, screen):
        """Renderiza las imágenes."""
        screen.blit(self.title_surf, (0, 0))
        screen.blit(self.pisazombis_surf, self.pisazombis_rect)
        if self.press_start():
            screen.blit(self.fontstart_surf, self.fontstart_rect)

    def update(self):
        """Esta escena no tiene nada que actualizar."""
        # pass

    def handle_events(self, events):
        """Maneja los eventos. En este caso, cambio de escena."""
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                # manager es la referencia para el SceneManager instanciado en main.
                # sinceramente, me pierdo con cómo una cosa apunta a otra, pero funciona.
                self.manager.go_to(GameScene())


class GameScene:
    """Escena principal de juego."""

    def __init__(self):
        super().__init__()
        # CARGA DE RECURSOS ----------------------------------------------------------------
        self.set_gui()
        self.set_timer()
        self.load_imgs()
        self.load_groups()
        self.jump_sound = pg.mixer.Sound("snd/Jump_1.wav")
        self.hit_sound = pg.mixer.Sound("snd/Boss_hit_1.wav")

        # estados de juego: active, hacker, finishing, finished, game_over.
        self.game_state = "active"
        self.can_i_press = False

    def set_gui(self):
        """Carga recursos de la interfaz: marcadores."""
        # Fuentes
        self.font_gover = pg.font.Font(FNT_BOLD, 50)
        self.font_cont = pg.font.Font(FNT_MONO, 25)

        # marcadores
        self.score_zombis = 0
        self.lifes = 4
        self.z_score_s = load(GUI_Z_CNTR).convert_alpha()
        self.z_score_r = self.z_score_s.get_rect(topleft=(70, 5))
        self.score_s = self.font_cont.render(str(self.score_zombis), True, "White")
        self.score_r = self.score_s.get_rect(topleft=(110, 10))
        self.lifecont_s = load(GUI_L_CNTR).convert_alpha()
        self.lifecont_r = self.lifecont_s.get_rect(topright=(430, 10))
        self.lifeblock_s = load(GUI_LIFE).convert_alpha()
        lblock_r1 = self.lifeblock_s.get_rect(topright=(427, 15))
        lblock_r2 = self.lifeblock_s.get_rect(topright=(410, 15))
        lblock_r3 = self.lifeblock_s.get_rect(topright=(393, 15))
        lblock_r4 = self.lifeblock_s.get_rect(topright=(376, 15))
        self.hearts = [lblock_r1, lblock_r2, lblock_r3, lblock_r4]

        # Rótulos del final
        self.gameover_text = self.font_gover.render("¡HAS PERDIDO!", True, "white")
        self.gameover_text_2 = self.font_cont.render(
            f"PISASTE {self.score_zombis} ZOMBIS, PERO...", True, "white"
        )
        self.gameover_txt_r = self.gameover_text.get_rect(
            center=(WIN_WIDTH / 2, WIN_HEIGHT / 4)
        )
        self.gameover_txt2_r = self.gameover_text_2.get_rect(
            center=(WIN_WIDTH / 2, WIN_HEIGHT / 5)
        )
        self.end_text1_s = self.font_gover.render("¡HAS PISADO", True, "white")
        self.end_text1_r = self.end_text1_s.get_rect(center=(WIN_WIDTH / 2, 100))
        self.end_text2_s = self.font_gover.render(
            f"{self.score_zombis} ZOMBIS!", True, "white"
        )
        self.end_text2_r = self.end_text2_s.get_rect(center=(WIN_WIDTH / 2, 170))
        self.fontstart_surf = self.font_cont.render(
            "PULSA CUALQUIER TECLA", False, GREEN
        )
        self.fontstart_rect = self.fontstart_surf.get_rect(center=(250, 250))

        self.hacker_text_s = self.font_gover.render("¡ERES HACKER!", True, "white")
        self.hacker_text_r = self.hacker_text_s.get_rect(
            center=(WIN_WIDTH / 2, WIN_HEIGHT / 4)
        )

        self.blink = 0

    def set_timer(self):
        """Carga eventos de usuario y variables del temporizador
        para reducir la aparición de zombis."""
        self.tasa_act = randint(1500, 2000)
        self.init_time = pg.time.get_ticks()
        self.time_now = 0
        self.time_bef = 0

        self.obstacle_time = pg.USEREVENT + 1
        pg.time.set_timer(self.obstacle_time, randint(500, 4500))
        self.cloud_time = pg.USEREVENT + 2
        pg.time.set_timer(self.cloud_time, randint(200, 2000))
        self.bg05_time = pg.USEREVENT + 3
        pg.time.set_timer(self.bg05_time, 300)
        self.bg04_time = pg.USEREVENT + 4
        pg.time.set_timer(self.bg04_time, 600)
        self.bg03_time = pg.USEREVENT + 5
        pg.time.set_timer(self.bg03_time, 1200)
        self.bg02_time = pg.USEREVENT + 6
        pg.time.set_timer(self.bg02_time, 2400)
        self.bg01_time = pg.USEREVENT + 7
        pg.time.set_timer(self.bg01_time, 4800)

    def load_imgs(self):
        """Carga los fondos del juego."""
        self.pisazombis_surf = load(GUI_TIT).convert_alpha()
        self.pisazombis_rect = self.pisazombis_surf.get_rect(topleft=(60, 300))

        self.bg00_s = load(BCKGRND_0).convert()
        self.bg01_s = load(BCKGRND_1).convert_alpha()
        self.bg02_s = load(BCKGRND_2).convert_alpha()
        self.bg03_s = load(BCKGRND_3).convert_alpha()
        self.bg04_s = load(BCKGRND_4).convert_alpha()
        self.bg05_s = load(BCKGRND_5).convert_alpha()
        self.bg06_s = load(BCKGRND_6).convert_alpha()

        self.bg00_r = self.bg00_s.get_rect(topleft=(0, 0))
        self.bg01_r = self.bg01_s.get_rect(topleft=(0, 40))
        self.bg02_r = self.bg02_s.get_rect(topleft=(0, 112))
        self.bg03_r = self.bg03_s.get_rect(topleft=(0, 153))
        self.bg04_r = self.bg04_s.get_rect(topleft=(0, 287))
        self.bg05_r = self.bg05_s.get_rect(topleft=(0, 390))
        self.bg06_r = self.bg06_s.get_rect(topleft=(0, 700))

        self.lat_s = load(BCK_LATERAL).convert()
        self.lat_r1 = self.lat_s.get_rect()
        self.lat_r2 = self.lat_s.get_rect(topleft=(435, 0))

        # Máscaras de final de juego
        self.end_finished_s = load("img/background/finished.png").convert_alpha()
        self.end_finished_r = self.end_finished_s.get_rect(topleft=(500, 0))
        self.end_gameover_s = load("img/background/gameover.png").convert_alpha()
        self.end_gameover_r = self.end_gameover_s.get_rect(topleft=(500, 0))
        self.end_hacker_s = load("img/background/hacker.png").convert_alpha()
        self.end_hacker_r = self.end_hacker_s.get_rect(topleft=(500, 0))

        self.ouch_s = load("img/p_mike/ouch.png").convert_alpha()
        self.ouch_r = self.ouch_s.get_rect()

    def load_groups(self):
        """Carga los sprites en sus grupos."""
        self.mike = Player()
        self.player = pg.sprite.GroupSingle()
        self.player.add(self.mike)

        self.zombis = pg.sprite.Group()
        self.zombis.add(Zombie(self.time_now))

        self.clouds = pg.sprite.Group()
        self.clouds.add(Cloud())

        self.obstacles = pg.sprite.Group()

    # MARCADORES ----------------------------------------------------------------
    def score_update(self, screen):
        """
        Actualiza el marcador de zombis.
        """
        score = str(self.score_zombis)
        pg.draw.rect(screen, "Black", (70, 10, 75, 30), 0, 4)
        self.score_s = self.font_cont.render(score, True, "White")
        screen.blit(self.score_s, self.score_r)
        screen.blit(self.z_score_s, self.z_score_r)

    def life_update(self, screen):
        """Muestra las vidas restantes. Si no quedan, el estado es game over."""
        screen.blit(self.lifecont_s, self.lifecont_r)
        # pinta un corazón por cada vida que tiene el jugador.
        for l in range(self.lifes):
            screen.blit(self.lifeblock_s, self.hearts[l])

    # COLISIONES ----------------------------------------------------------------
    # @TODO Mejorar la colisión mediante un rect más pequeño de Player
    # 45x80 pixels centerbottom
    def collision_check(self):
        """Comprueba colisión perfecta de pixel con zombis."""
        colliding = pg.sprite.groupcollide(self.zombis, self.player, False, False)
        if colliding:
            for zombi in colliding:
                if pg.sprite.groupcollide(
                    self.zombis, self.player, False, False, pg.sprite.collide_mask
                ):
                    if zombi.dead is False:
                        self.score_zombis += 1
                        zombi.dead = True
                    if self.mike.gravity == 1:
                        self.mike.animation_index = 0
                        self.mike.gravity -= 15
                        self.jump_sound.play()

    def collision_obstacle(self):
        """Comprueba colisión perfecta de pixel con objetos."""
        colliding = pg.sprite.groupcollide(
            self.obstacles, self.player, False, False, pg.sprite.collide_rect
        )
        if colliding:
            for obstacle in colliding:
                # for bolardo in self.obstacles:
                if self.mike.collide_rect.colliderect(obstacle):
                    if obstacle.destroyed is False:
                        self.mike.animation_index = 0
                        self.mike.animation_status = "hit"
                        if obstacle.rect.centerx > self.mike.rect.centerx:
                            self.mike.rect.x -= 40
                        else:
                            self.mike.rect.x += 40
                        obstacle.destroyed = True
                        self.lifes -= 1
                        self.hit_sound.play()


    # ESTADOS DE JUEGO ----------------------------------------------------------------
    def game_state_check(self):
        """Comprueba qué estado de juego debe tener."""
        if self.mike.rect.bottom >= 675 and self.mike.animation_status == "landed":
            self.zombis.empty()
            self.obstacles.empty()
            self.clouds.empty()
            self.game_state = "finishing"
        elif self.lifes == 0:
            self.zombis.empty()
            self.obstacles.empty()
            self.clouds.empty()
            self.game_state = "game_over"
        elif self.score_zombis > 99:
            self.zombis.empty()
            self.obstacles.empty()
            self.clouds.empty()
            self.game_state = "hacker"
        else:
            self.game_state = "active"

    def landing(self):
        """El jugador ha llegado al fondo e inicia secuencia final."""
        if self.bg06_r.top >= 355:
            self.bg06_r.y -= 61
        else:
            time.sleep(2)
            self.game_state = "finished"

    def gameover(self, screen):
        """Si se acaban todas las vidas."""
        if self.blink < 20:
            pos_x, pos_y = self.mike.rect.centerx, self.mike.rect.centery
            self.ouch_r.center = (pos_x, pos_y)
            screen.blit(self.ouch_s, self.ouch_r)
            self.blink += 1
        else:
            if self.end_gameover_r.x >= -10:
                self.end_gameover_r.x -= 61
                # screen.blit(self.end_gameover_s, self.end_gameover_r)
                self.gameover_text_2 = self.font_cont.render(
                    f"PISASTE {self.score_zombis} ZOMBIS, PERO...", True, "white"
                )

            else:
                screen.blit(self.end_gameover_s, self.end_gameover_r)
                screen.blit(self.gameover_text_2, self.gameover_txt2_r)
                screen.blit(self.gameover_text, self.gameover_txt_r)
                self.can_i_press = True
                if self.press_start():
                    screen.blit(self.fontstart_surf, self.fontstart_rect)

    def endgame(self, screen):
        """Pantalla de finalización con marcador."""
        if self.end_finished_r.x >= -10:
            self.player.draw(screen)
            self.end_finished_r.x -= 61
            self.end_text2_s = self.font_gover.render(
                f"{self.score_zombis} ZOMBIS!", True, "white"
            )
        else:
            self.player.draw(screen)
            screen.blit(self.end_finished_s, self.end_finished_r)
            screen.blit(self.end_text1_s, self.end_text1_r)
            screen.blit(self.end_text2_s, self.end_text2_r)
            self.can_i_press = True
            if self.press_start():
                screen.blit(self.fontstart_surf, self.fontstart_rect)

    def hey_hacker(self, screen):
        """Si supera los 100 zombis."""
        if self.end_hacker_r.x >= -10:
            self.end_hacker_r.x -= 61
        else:
            screen.blit(self.end_hacker_s, self.end_hacker_r)
            screen.blit(self.hacker_text_s, self.hacker_text_r)
            self.can_i_press = True
            if self.press_start():
                screen.blit(self.fontstart_surf, self.fontstart_rect)

    def press_start(self):
        """Hace parpadear el aviso de presionar tecla."""
        self.blink += 1
        if self.blink % 60 >= 10:
            return True
        return False

    # ACTUALIZACIONES Y EVENTOS --------------------------------
    def handle_events(self, events):
        """Maneja los eventos."""
        self.time_now = pg.time.get_ticks() - self.init_time
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                self.manager.go_to(TitleScene())
            if self.game_state == "active":
                if self.time_now >= 5000:
                    if e.type == self.obstacle_time:
                        self.obstacles.add(Bolardos())
                        pg.time.set_timer(self.obstacle_time, randint(500, 4500))
                if self.time_now - self.time_bef >= self.tasa_act:
                    self.zombis.add(Zombie(self.time_now))
                    # Actualiza los valores para la próxima aparición
                    self.tasa_act += randint(8, 12)  # Reducción gradual del intervalo
                    self.time_bef = self.time_now
                if e.type == self.bg05_time:
                    bg_animation(self.bg05_r)
                if e.type == self.bg04_time:
                    bg_animation(self.bg04_r)
                if e.type == self.bg03_time:
                    bg_animation(self.bg03_r)
                if e.type == self.bg02_time:
                    bg_animation(self.bg02_r)
                if e.type == self.bg01_time:
                    bg_animation(self.bg01_r)
                if e.type == self.cloud_time:
                    self.clouds.add(Cloud())
                    self.cloud_time = pg.USEREVENT + 2
                    pg.time.set_timer(self.cloud_time, randint(200, 1000))
            elif self.can_i_press:
                if e.type == pg.KEYDOWN:
                    self.manager.go_to(TitleScene())

    def update(self):
        """Actualiza los cambios y comprueba algunos estados."""
        if self.game_state == "finishing":
            self.landing()
        if self.game_state != "finished":
            self.collision_check()
            self.collision_obstacle()
            self.game_state_check()

    def render(self, screen):
        """Renderiza la escena."""
        if self.game_state == "active":
            # fondo
            screen.blit(self.bg00_s, self.bg00_r)
            screen.blit(self.bg01_s, self.bg01_r)
            screen.blit(self.bg02_s, self.bg02_r)
            screen.blit(self.bg03_s, self.bg03_r)
            screen.blit(self.bg04_s, self.bg04_r)
            screen.blit(self.bg05_s, self.bg05_r)
            screen.blit(self.bg06_s, self.bg06_r)
            screen.blit(self.lat_s, self.lat_r1)
            screen.blit(self.lat_s, self.lat_r2)
            screen.blit(self.pisazombis_surf, self.pisazombis_rect)

            # efectos de movimiento:
            falling_effect(self.lat_r1)
            falling_effect(self.lat_r2)
            title(self.pisazombis_rect)

            # marcadores
            self.score_update(screen)
            self.life_update(screen)

            # sprites
            self.player.draw(screen)
            self.player.update()
            # pg.draw.rect(screen, "black", self.mike.collide_rect, 4)
            self.zombis.draw(screen)
            self.zombis.update()
            self.clouds.draw(screen)
            self.clouds.update()
            self.obstacles.draw(screen)
            self.obstacles.update()

        elif self.game_state == "finishing":
            screen.blit(self.bg00_s, self.bg00_r)
            screen.blit(self.bg01_s, self.bg01_r)
            screen.blit(self.bg02_s, self.bg02_r)
            screen.blit(self.bg03_s, self.bg03_r)
            screen.blit(self.bg04_s, self.bg04_r)
            screen.blit(self.bg05_s, self.bg05_r)
            screen.blit(self.bg06_s, self.bg06_r)
            screen.blit(self.lat_s, self.lat_r1)
            screen.blit(self.lat_s, self.lat_r2)
            self.player.draw(screen)
            self.player.update()

        elif self.game_state == "finished":
            screen.blit(self.bg00_s, self.bg00_r)
            screen.blit(self.bg01_s, self.bg01_r)
            screen.blit(self.bg02_s, self.bg02_r)
            screen.blit(self.bg03_s, self.bg03_r)
            screen.blit(self.bg04_s, self.bg04_r)
            screen.blit(self.bg05_s, self.bg05_r)
            screen.blit(self.bg06_s, self.bg06_r)
            screen.blit(self.lat_s, self.lat_r1)
            screen.blit(self.lat_s, self.lat_r2)
            self.endgame(screen)

        elif self.game_state == "game_over":
            screen.blit(self.bg00_s, self.bg00_r)
            screen.blit(self.bg01_s, self.bg01_r)
            screen.blit(self.bg02_s, self.bg02_r)
            screen.blit(self.bg03_s, self.bg03_r)
            screen.blit(self.bg04_s, self.bg04_r)
            screen.blit(self.bg05_s, self.bg05_r)
            screen.blit(self.bg06_s, self.bg06_r)
            screen.blit(self.lat_s, self.lat_r1)
            screen.blit(self.lat_s, self.lat_r2)

            self.gameover(screen)

        elif self.game_state == "hacker":
            screen.blit(self.bg00_s, self.bg00_r)
            screen.blit(self.bg01_s, self.bg01_r)
            screen.blit(self.bg02_s, self.bg02_r)
            screen.blit(self.bg03_s, self.bg03_r)
            screen.blit(self.bg04_s, self.bg04_r)
            screen.blit(self.bg05_s, self.bg05_r)
            screen.blit(self.bg06_s, self.bg06_r)
            screen.blit(self.lat_s, self.lat_r1)
            screen.blit(self.lat_s, self.lat_r2)
            self.hey_hacker(screen)


class SceneManager:
    """Las escenas se manejan a través de este pointer."""

    def __init__(self):
        self.go_to(TitleScene())

    def go_to(self, scene):
        # A través de las otras clases de escena, permite moverse entre ellas.
        self.scene = scene
        self.scene.manager = self
