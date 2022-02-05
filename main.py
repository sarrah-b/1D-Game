import pygame
from pygame.locals import *
from pygame import mixer
import os
import time
import random
import sys


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


pygame.font.init()


WIDTH, HEIGHT = 500, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1D Shooter")


# Loading the images
simon_url = resource_path(os.path.join("assets", "simon_face.png"))
SIMON_FACE = pygame.image.load(simon_url)

#boosts images

album_covers = []
album_files = ["uan.jpg", "tmh.png", "mm.png", "mitam.png", "four.png"]
for album_file in album_files:
    album_url = resource_path(os.path.join("assets", album_file))
    album_image = pygame.image.load(album_url)
    album_image = pygame.transform.scale(album_image, (50, 50))
    album_covers.append(album_image)


# PLAYER SHIP
ONED_PLAYER_url = resource_path(os.path.join("assets", "1d_player.png"))
ONED_PLAYER = pygame.image.load(ONED_PLAYER_url)


# LASERS
# ONED_LASER = pygame.image.load(os.path.join("assets", "1d_logo.png"))
ONED_LASER_url = resource_path(os.path.join("assets", "1d_logo.png"))
ONED_LASER = pygame.image.load(ONED_LASER_url)
ONED_LASER_NEW = pygame.transform.scale(ONED_LASER, (50, 40))


CROSS_LASER_url = resource_path(os.path.join("assets", "cross.png"))
CROSS_LASER = pygame.image.load(CROSS_LASER_url)

# background
# BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_main.jpg")), (WIDTH, HEIGHT))

BG_url = resource_path(os.path.join("assets", "background_main.jpg"))
BG = pygame.transform.scale(pygame.image.load(BG_url), (WIDTH, HEIGHT))

# HELP = pygame.image.load(os.path.join("assets", "help_icon.png"))
HELP_url = resource_path(os.path.join("assets", "help_icon.png"))
HELP = pygame.image.load(HELP_url).convert_alpha()
HELP_NEW = pygame.transform.scale(HELP, (30, 30))


mixer.init()

start_sound = pygame.mixer.Sound(os.path.join("assets", "1d_start.mp3"))
game_sound = pygame.mixer.Sound(os.path.join("assets", "1d_music.ogg"))
buzzer_sound = pygame.mixer.Sound(os.path.join("assets", "buzzer.mp3"))

start_channel = pygame.mixer.Channel(0)
run_channel = pygame.mixer.Channel(1)
buzzer_channel = pygame.mixer.Channel(2)



class Button:
    def __init__(self, x, y, img, WIN):
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.WIN = WIN

    def hover(self):
        is_hovering = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            is_hovering = True

        return is_hovering

    def draw(self):

        action = False

        pos = pygame.mouse.get_pos()

        if self.hover():
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        self.WIN.blit(self.img, (self.rect.x, self.rect.y))

        return action


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None  # draw ship
        self.laser_img = None  # draw lasers
        self.lasers = []
        self.cool_down_counter = 0  # how long to wait till you shoot again

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        did_a_hit = False
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                did_a_hit = True
                obj.health -= 10
                self.lasers.remove(laser)
        return did_a_hit

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=50):
        super().__init__(x, y, health)
        self.ship_img = ONED_PLAYER
        self.laser_img = ONED_LASER_NEW
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.score += 1
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                         self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                         self.ship_img.get_width() * (1-((self.max_health-self.health)/self.max_health)), 10))

class Enemy(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SIMON_FACE
        self.laser_img = CROSS_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.attack = 10

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Boost(Ship):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.ship_img = random.choice(album_covers)
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.attack = 10

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Game:

    def __init__(self, WIN):
        self.pause = False
        self.helping = False
        self.score = 0
        self.run = False
        self.FPS = 60  # frames per second
        self.level = 0
        self.main_font = pygame.font.SysFont("arial", 30)
        self.click = pygame.mouse.get_pressed()
        self.WIN = WIN

        self.enemies = []
        self.boosts = []
        self.wave_length = 5
        self.enemy_vel = 1
        self.enemy_vel = 2

        self.player_vel = 5
        self.laser_vel = 5

        self.player = Player(WIDTH/2 - ONED_PLAYER.get_width()/2, 300)

        self.clock = pygame.time.Clock()

        self.lost = False

        self.lost_count = 0

    def redraw_window(self):

        self.mouse_pointer()
        
        self.WIN.blit(BG, (0, 0))  # redraws image
        # draw text
        score_label = self.main_font.render(
            f"Score: {self.player.score}", 1, (255, 255, 255))
        level_label = self.main_font.render(
            f"Level: {self.level}", 1, (255, 255, 255))

        self.WIN.blit(score_label, (10, 10))
        self.WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in self.enemies:
            enemy.draw(self.WIN)
            
        for boost in self.boosts:
            boost.draw(self.WIN)


        self.player.draw(self.WIN)

        if self.lost:
            self.run = False
            self.score = self.player.score
            self.lost_page()
        self.display_mouse()
        pygame.display.update()

    def game_loop(self):  # when the program is running
        start_channel.stop()
        run_channel.play(game_sound, loops=-1, fade_ms=1000)
        self.lost = False
        self.level = 0
        self.enemies = []
        self.wave_length = 5
        self.enemy_vel = 1
        self.boost_vel = 3
        self.player_vel = 7
        self.laser_vel = 4

        self.player = Player(WIDTH/2 - ONED_PLAYER.get_width()/2, 300)

        while self.run:
            self.clock.tick(self.FPS)
            self.redraw_window()
            if self.player.health <= 0:
                self.lost = True
                self.lost_count += 1

            if len(self.enemies) == 0:
                self.level += 1
                self.wave_length += 5
                for i in range(self.wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100),
                                  random.randrange(-1500, -100))
                    self.enemies.append(enemy)

            if random.random() < 0.00167:
                
                boost = Boost(random.randrange(50, WIDTH - 50),
                        random.randrange(-1500, -100))
                self.boosts.append(boost)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # if press X button
                    quit()

            self.controls()

            got_hit = False
            for enemy in self.enemies:
                enemy.move(self.enemy_vel)
                if enemy.move_lasers(self.laser_vel, self.player):
                    got_hit = True

                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()

                if collide(enemy, self.player):
                    self.player.health -= enemy.attack
                    self.enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    self.score -= 1
                    self.enemies.remove(enemy)
            
            if got_hit:
                buzzer_channel.play(buzzer_sound)

            for boost in self.boosts:
                boost.move(self.boost_vel)
                if collide(boost, self.player):
                    self.player.health = min(self.player.health + boost.attack, self.player.max_health)
                    self.boosts.remove(boost)
                elif boost.y + boost.get_height() > HEIGHT:
                    self.boosts.remove(boost)

            self.player.move_lasers(-self.laser_vel, self.enemies)

    def controls(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player.x - self.player_vel > 0:  # left
            self.player.x -= self.player_vel
        if keys[pygame.K_RIGHT] and self.player.x + self.player_vel + self.player.get_width() < WIDTH:
            self.player.x += self.player_vel
        if keys[pygame.K_UP] and self.player.y - self.player_vel > 0:
            self.player.y -= self.player_vel
        if keys[pygame.K_DOWN] and self.player.y + self.player_vel + self.player.get_height() + 15 < HEIGHT:
            self.player.y += self.player_vel
        if keys[pygame.K_SPACE]:
            self.player.shoot()
        if keys[pygame.K_ESCAPE]:
            self.paused()

    def unpaused(self):
        self.pause = False
        run_channel.unpause()
        buzzer_channel.unpause()

    def paused(self):
        self.pause = True
        run_channel.pause()
        buzzer_channel.pause()
        self.PAUSE_font = pygame.font.SysFont("arial", 30)
        mouse = pygame.mouse.get_pos()
        while self.pause:
            self.WIN.blit(BG, (0, 0))
            self.PAUSE_label = self.PAUSE_font.render(
                "Game is Paused. Click to Continue", 1, (255, 255, 255))
            self.WIN.blit(self.PAUSE_label, (WIDTH/2 -
                          self.PAUSE_label.get_width()/2, 200))

            self.mouse_pointer()
            button_y = HEIGHT/2 + 100
            self.button("MAIN MENU", WIDTH/2 - 150, button_y, 100,
                        50, (255, 0, 0), (200, 0, 0), "new_game", True)
            self.button("RESUME", WIDTH/2, button_y, 100,
                        50, (255, 0, 0), (200, 0, 0), "resume", True)
            self.button("QUIT", WIDTH/2 + 150, button_y, 100,
                        50, (255, 0, 0), (200, 0, 0), "quit", True)
            self.display_mouse()

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

    def mouse_pointer(self):
        self.cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)

    def mouse_hand(self):
        self.cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

    def display_mouse(self):
        pygame.mouse.set_cursor(*self.cursor)

    def button(self, msg: str, x: int, y: int, w: int, h: int, ic, ac, action=None, centered=False):
        """
        Add a button
        """

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        button_font = pygame.font.SysFont("arial", 20)
        button_label = button_font.render(msg, 1, (255, 255, 255))

        text_w = button_label.get_width()
        text_h = button_label.get_height()

        center_x = x + w/2
        center_y = x + h/2

        w = max(w, text_w)
        h = max(h, text_h)

        if centered:
            x = x - w/2
            y = y - h/2

        mouse_is_released = (click[0] == 1)
        # mouse_is_released = pygame.MOUSEBUTTONUP in [event.type for event in pygame.event.get()]

        if x+w > mouse[0] > x and y+h > mouse[1] > y:

            pygame.draw.rect(self.WIN, ac, (x, y, w, h))
            self.mouse_hand()
            if mouse_is_released and action != None:

                if action == "start":
                    start_channel.pause()
                    self.game_loop()
                if action == "resume":
                    self.unpaused()
                if action == "quit":
                    quit()
                if action == "help":
                    self.help_menu()
                if action == "main":
                    self.main_menu()
                if action == "new_game":
                    self.new_game()

        else:
            pygame.draw.rect(self.WIN, ic, (x, y, w, h))

        self.WIN.blit(button_label, (x + (w - text_w)/2, y + (h - text_h)/2))

    def help_menu(self):
        helping = True
        self.help_font = pygame.font.SysFont("arial", 30)
        mouse = pygame.mouse.get_pos()
        while helping:
            self.WIN.blit(BG, (0, 0))
            help_label = self.help_font.render(
                "Kill Simon Cowell!! Use your arrow keys", 1, (255, 255, 255))
            help_label2 = self.help_font.render(
                "to move 1D and shoot with SpaceBar", 1, (255, 255, 255))

            self.WIN.blit(
                help_label, (WIDTH/2 - help_label.get_width()/2, 100))
            self.WIN.blit(
                help_label2, (WIDTH/2 - help_label2.get_width()/2, 150))
            self.mouse_pointer()
            self.button("BACK TO MAIN MENU", WIDTH/2, HEIGHT/2 + 25, 100,
                        50, (255, 0, 0), (200, 0, 0), "main", True)
            self.button("QUIT", WIDTH/2, HEIGHT/2 + 100, 100,
                        50, (255, 0, 0), (200, 0, 0), "quit", True)
            self.display_mouse()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

        pygame.quit()

    def lost_page(self):
        self.run = True
        run_channel.stop()
        buzzer_channel.stop()
        self.WIN.blit(BG, (0, 0))
        self.lost_font = pygame.font.SysFont("arial", 30)
        self.lost_label = self.lost_font.render(
            "Game Over!! Your score was: " + str(self.score), 1, (255, 255, 255))
        self.WIN.blit(self.lost_label, (WIDTH/2 -
                      self.lost_label.get_width()/2, 100))

        self.mouse_pointer()
        button_y = HEIGHT/2
        self.button("MAIN MENU", WIDTH/2 - 150, button_y, 100,
                    50, (255, 0, 0), (200, 0, 0), "new_game", True)
        self.button("RESTART", WIDTH/2, button_y, 100,
                    50, (255, 0, 0), (200, 0, 0), "start", True)
        self.button("QUIT", WIDTH/2 + 150, button_y, 100,
                    50, (255, 0, 0), (200, 0, 0), "quit", True)
        self.display_mouse()

    def new_game(self):
        start_channel.stop()
        run_channel.stop()
        buzzer_channel.stop()
        start_channel.play(start_sound, loops=-1, fade_ms=5000)
        self.main_menu()

    def main_menu(self):
        self.title_font = pygame.font.SysFont("arial", 30)
        self.run = True
        while self.run:
            self.WIN.blit(BG, (0, 0))
            self.WIN.blit(HELP_NEW, (0, 0))

            self.title_label = self.title_font.render(
                "Press the button to begin...", 1, (255, 255, 255))
            self.WIN.blit(self.title_label, (WIDTH/2 -
                          self.title_label.get_width()/2, 200))
            self.mouse_pointer()
            self.button("START", WIDTH/2, HEIGHT/2 + 100, 100,
                        50, (255, 0, 0), (200, 0, 0), "start", True)
            help_button = Button(0, 0, HELP_NEW, self.WIN)
            
            if help_button.hover():
                self.mouse_hand()

            self.display_mouse()
            
            if help_button.draw():
                self.help_menu()

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
        pygame.quit()


if __name__ == "__main__":
    mixer.init()

    start_channel.play(start_sound, loops=-1, fade_ms=5000)

    game = Game(WINDOW)

    game.main_menu()
