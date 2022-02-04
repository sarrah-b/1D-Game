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
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1D Shooter")



#Loading the images
simon_url = resource_path(os.path.join("assets", "simon_face.png"))
SIMON_FACE = pygame.image.load(simon_url)


#PLAYER SHIP
ONED_PLAYER_url = resource_path(os.path.join("assets", "1d_player.png"))
ONED_PLAYER = pygame.image.load(ONED_PLAYER_url)



#LASERS
# ONED_LASER = pygame.image.load(os.path.join("assets", "1d_logo.png"))
ONED_LASER_url = resource_path(os.path.join("assets", "1d_logo.png"))
ONED_LASER = pygame.image.load(ONED_LASER_url)
ONED_LASER_NEW = pygame.transform.scale(ONED_LASER,(50,40))


CROSS_LASER_url = resource_path(os.path.join("assets", "cross.png"))
CROSS_LASER = pygame.image.load(CROSS_LASER_url)

#background
# BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_main.jpg")), (WIDTH, HEIGHT))

BG_url = resource_path(os.path.join("assets", "background_main.jpg"))
BG = pygame.transform.scale(pygame.image.load(BG_url), (WIDTH,HEIGHT))

# HELP = pygame.image.load(os.path.join("assets", "help_icon.png"))
HELP_url = resource_path(os.path.join("assets", "help_icon.png"))
HELP = pygame.image.load(HELP_url).convert_alpha()
HELP_NEW = pygame.transform.scale(HELP,(30,30))


mixer.init()

start_channel = pygame.mixer.Channel(0)
run_channel = pygame.mixer.Channel(1)


class Button:
	def __init__(self,x,y,img):
		self.img =img
		self.rect = self.img.get_rect()
		self.rect.topleft = (x,y)
		self.clicked = False

	def draw (self):

		action = False

		pos = pygame.mouse.get_pos()

		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		WIN.blit(self.img, (self.rect.x, self.rect.y))

		return action

help_button = Button(0,0, HELP_NEW)


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
		self.ship_img = None #draw ship
		self.laser_img = None #draw lasers
		self.lasers = []
		self.cool_down_counter = 0 #how long to wait till you shoot again


	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)


	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)


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


	def draw(self,window):
		super().draw(window)
		self.healthbar(window)


	def healthbar(self, window):
		pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
		pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (1-((self.max_health-self.health)/self.max_health)), 10))



class Enemy(Ship):
	

	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = SIMON_FACE
		self.laser_img = CROSS_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self, vel):
		self.y += vel


	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x + 10, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1



def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None



class Game:

	def __init__(self, WIN):
		self.pause = False
		self.help_menu = False
		self.score = 0
		self.run = False
		self.FPS	= 60 #frames per second
		self.level = 0
		self.main_font = pygame.font.SysFont("arial", 30)
		self.click = pygame.mouse.get_pressed()
		

		run_channel.play(pygame.mixer.Sound("1d_music.wav"), loops=-1, fade_ms=5000)


		enemies = []
		wave_length = 5
		enemy_vel = 1

		player_vel = 5
		laser_vel = 5

		player = Player(WIDTH/2 - ONED_PLAYER.get_width()/2, 300)

		clock = pygame.time.Clock()

		lost = False

		lost_count = 0

	def redraw_window():
		WIN.blit(BG, (0,0)) #redraws image
		#draw text
		score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))
		level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

		WIN.blit(score_label, (10,10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

		for enemy in enemies:
			enemy.draw(WIN)


		player.draw(WIN)

		if lost:
			run = False
			score = player.score
			lost_page()

			
		pygame.display.update()


	while run:  #when the program is running
		clock.tick(FPS)
		redraw_window()

		if player.health <= 0:
			lost = True
			lost_count += 1
	
		if len(enemies) == 0:
			level += 1
			wave_length += 5
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
				enemies.append(enemy)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:  #if press X button
				quit()
		

		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT] and player.x - player_vel > 0:# left
			player.x -= player_vel
		if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH:
			player.x += player_vel
		if keys[pygame.K_UP] and player.y - player_vel > 0:
			player.y -= player_vel
		if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()
		if keys[pygame.K_ESCAPE]:
			pause = True
			paused()


		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)


			if random.randrange(0, 2*60) == 1:
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 50
				enemies.remove(enemy)
			elif enemy.y + enemy.get_height() > HEIGHT:
				score -= 1
				enemies.remove(enemy)





		player.move_lasers(-laser_vel, enemies)





def unpaused():
	global pause
	pause = False
	
	
def paused():
	pause = True
	run_channel.pause()
	PAUSE_font = pygame.font.SysFont("arial", 30)
	mouse = pygame.mouse.get_pos()		
	while pause:
		WIN.blit(BG, (0,0))
		PAUSE_label = PAUSE_font.render("Game is Paused. Click to Continue", 1, (255,255,255))
		WIN.blit(PAUSE_label, (WIDTH/2 - PAUSE_label.get_width()/2, 200))
		button("RESUME", WIDTH/2 - 200, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "resume")
		button("QUIT", WIDTH - 150, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "quit")

		
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			


def button(msg,x,y,w,h,ic,ac, action = None):
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()
	pygame.SYSTEM_CURSOR_HAND

	if x+w > mouse[0] > x and y+h > mouse[1] > y:

		pygame.draw.rect(WIN, ac, (x,y,w,h))

		if click[0] == 1 and action != None:
			
			if action == "start":
				start_channel.pause()
				main()
			if action == "resume":
				unpaused()
				run_channel.unpause()
			if action == "quit":
				quit()
			if action == "help":
				help_menu()
			if action == "main":
				main_menu()

	else:
		pygame.draw.rect(WIN, ic, (x,y,w,h))


	button_font = pygame.font.SysFont("arial",20)
	button_label = button_font.render(msg, 1, (255,255,255))
	WIN.blit(button_label, (x + w/4, y + h/4))


def help_menu():
	help_menu = True
	help_font = pygame.font.SysFont("arial", 30)
	mouse = pygame.mouse.get_pos()		
	while help_menu:
		WIN.blit(BG, (0,0))
		help_label = help_font.render("Kill Simon Cowell!! Use your arrow keys", 1, (255,255,255))
		help_label2 = help_font.render("to move 1D and shoot with SpaceBar", 1, (255,255,255))

		WIN.blit(help_label, (WIDTH/2 - help_label.get_width()/2, 100))
		WIN.blit(help_label2, (WIDTH/2 - help_label2.get_width()/2, 150))

		button("BACK", WIDTH/2 - 200, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "main")
		button("QUIT", WIDTH - 150, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "quit")

		
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			


	pygame.quit()	

def lost_page():
	run = False
	run_channel.pause()
	WIN.blit(BG, (0,0))
	lost_font = pygame.font.SysFont("arial", 30)
	lost_label = lost_font.render(f"You lost!! Your score was: " + str(score), 1, (255,255,255))
	WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 100))
	button("MAIN MENU", WIDTH/2 - 200, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "main")
	button("QUIT", WIDTH - 150, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "quit")

def main_menu():
	global help_menu
	start_channel.unpause()

	title_font = pygame.font.SysFont("arial", 30)
	run = True
	while run:
		WIN.blit(BG, (0,0))
		WIN.blit(HELP_NEW, (0,0))

		title_label = title_font.render("Press the button to begin...", 1, (255,255,255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))
		
		button("START", WIDTH/2 - 50, HEIGHT/2, 100, 50, (255,0,0), (200,0,0), "start")
		if help_button.draw():
			help_menu()

		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

	pygame.quit()		

mixer.init()

start_channel.play(pygame.mixer.Sound("1d_start.mp3"), loops=-1, fade_ms=5000)


main_menu()
main()