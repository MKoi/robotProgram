import os, sys
import math
import re
from collections import defaultdict
import itertools 
import pygame
from pygame.locals import *

pixels_per_grid = 32
grid_maxx = 7
grid_maxy = grid_maxx
targetfps = 60
screen_width = 480
screen_height = 800
arena_width = (grid_maxx + 1) * pixels_per_grid
arena_height = (grid_maxy + 1) * pixels_per_grid
arena_x = 0.5 * (screen_width - arena_width)
arena_y = 0.5 * (screen_height - arena_height)
arena_border = 8
WHITE = (255, 255, 255)



def load_image(name, colorkey=None):
	fullname = os.path.join('assets', name)
	try:
	 	image = pygame.image.load(fullname)
	except pygame.error, message:
		image = pygame.Surface((pixels_per_grid,pixels_per_grid))
		pygame.draw.circle(image, WHITE, (pixels_per_grid/2,pixels_per_grid/2), pixels_per_grid/2, 3)
		#print 'Cannot load image:', name
		#raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()

def parsetrace(tracefile):
	timestamp = -1
	players = {}
	actions = defaultdict(set)
	for line in tracefile:
		tmatch = re.match('t:\d+;', line) # timestamp
		if tmatch:
			timestamp = int(tmatch.group(0)[2:-1])
			continue
		amatch = re.match('p(\d)([ms]):(\d+),(\d+):(\d+);', line) # action
		if amatch:
			pnumber = int(amatch.group(1))
			actioncode = amatch.group(2)
			x, y = int(amatch.group(3)), int(amatch.group(4))
			duration = int(amatch.group(5))
			actions[timestamp].add((pnumber,actioncode,x,y,duration))
			continue
		ptmatch = re.match('p(\d)t:(\w+);', line) # icon type
		if ptmatch:
			i = int(ptmatch.group(1))
			typestr = ptmatch.group(2)
			player = players.get(i)
			if player:
				player.settype(typestr)
			else:
				players[i] = Roboicon(0, 0, typestr)
			continue
		ppmatch = re.match('p(\d)p:(\d+),(\d+);', line) # position
		if ppmatch:
			i = int(ppmatch.group(1))
			x = int(ppmatch.group(2))
			y = int(ppmatch.group(3))
			player = players.get(i)
			if player:
				player.setpos(x, y)
			else:
				players[i] = Roboicon(x, y)
			continue
	return actions, players

def grid_to_screen(grid_x, grid_y, center = False):
	x = clamp(grid_x, 0, grid_maxx)
	y = grid_maxy - clamp(grid_y, 0, grid_maxy) # inverse y coordinate
	offset = pixels_per_grid / 2 if center else 0 
	return arena_x + x * pixels_per_grid + offset, arena_y + y * pixels_per_grid + offset
	
def clamp(n, smallest, largest): 
	return max(smallest, min(n, largest))

class Bullet:
	thickness = 3
	length = 5.0
	def __init__(self, start, end, duration):
		self.start = start
		self.end = end
		self.duration = duration
		
	def update(self, dt):
		if self.duration <= 0.0:
			return
		ratio = min(1.0, float(dt) / float(self.duration))
		dx = ratio * (self.end[0] - self.start[0])
		dy = ratio * (self.end[1] - self.start[1])
		self.start = self.start[0] + dx, self.start[1] + dy
		self.duration -= dt
		
	def draw(self, screen):
		vec = pygame.math.Vector2(self.end[0] - self.start[0], self.end[1] - self.start[1])
		vec.scale_to_length(self.length)
		pygame.draw.line(screen, WHITE, self.start, (self.start[0] + vec.x, self.start[1] + vec.y), self.thickness)

class Projectiles:
	
	bullets = []
	
	def add(self, start, end, duration):
		self.bullets.append(Bullet(start, end, duration))
	
	def update(self, dt):
		for b in self.bullets:
			b.update(dt)
		self.bullets = [b for b in self.bullets if b.duration > 0] # remove old elements

	def draw(self, screen):
		for b in self.bullets:
			b.draw(screen)
		

class Roboicon(pygame.sprite.Sprite):

	filenames = {'robot':'robo_r.png'}

	def __init__(self, x, y, typestr = None):
		pygame.sprite.Sprite.__init__(self)
		self.typestr = typestr
		if typestr:
			self.image, self.rect = load_image(self.filenames.get(typestr, 'robot'), -1)
		else:
			self.image = None
			self.rect = pygame.Rect(0, 0, 0, 0)
		self.goingRight = True
		self.rect.topleft = grid_to_screen(x, y)
		self.targetx = self.rect.topleft[0]
		self.targety = self.rect.topleft[1]
		self.targettime = 0.0


	def settype(self, typestr):
		if typestr != self.typestr:
			self.typestr = typestr
			savex, savey = self.rect.topleft
			self.image, self.rect = load_image(self.filenames.get(typestr, 'robot'), -1)
			self.rect.topleft = (savex, savey)

	def setpos(self, x, y):
		self.rect.topleft = grid_to_screen(x, y)
		self.targetx = self.rect.topleft[0]
		self.targety = self.rect.topleft[1]

	def move(self, x, y, targettime):
		newx, newy = grid_to_screen(x, y)
		if newx < self.targetx and self.goingRight:
			self.goingRight = False
			self.image = pygame.transform.flip(self.image, 1, 0)
		elif newx > self.targetx and not self.goingRight:
			self.goingRight = True
			self.image = pygame.transform.flip(self.image, 1, 0)
		self.targetx, self.targety = newx, newy
		self.targettime = targettime
		

	def update(self, dt):
		if self.targettime <= 0.0:
			self.rect.topleft = self.targetx, self.targety
			return
		
		ratio = min(1.0, float(dt) / float(self.targettime))
		dx = ratio * (self.targetx - self.rect.topleft[0])
		dy = ratio * (self.targety - self.rect.topleft[1])
		self.rect.move_ip(round(dx), round(dy))
		self.targettime -= dt
		
	

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Robo test')
pygame.mouse.set_visible(0)


background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))
pygame.draw.rect(background, WHITE, (arena_x, arena_y, arena_width, arena_height), arena_border)

screen.blit(background, (0, 0))
pygame.display.flip()

inputfile = open(sys.argv[1])

	
actions, players = parsetrace(inputfile)
projectiles = Projectiles()
allsprites = pygame.sprite.RenderPlain(*players.values())
clock = pygame.time.Clock()
exitgame = False
totaltime = 0
while not exitgame:
	dt = clock.tick(targetfps)
	for event in pygame.event.get():
		if event.type == QUIT:
			exitgame = True
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			exitgame = True
	
	allsprites.update(dt)
	projectiles.update(dt)

	nearest = -1
	for key in actions.keys():
		if totaltime <= key and totaltime + dt > key:
			nearest = key

	if nearest >= 0:
		actions_now = actions[nearest]
		for action in actions_now:
			player = players[action[0]]
			if action[1] == 'm':
				x, y = action[2], action[3]
				duration = action[4]
				player.move(x, y, duration)
			elif action[1] == 's':
				endx, endy = grid_to_screen(action[2], action[3], True)
				startx, starty = player.rect.center
				projectiles.add((startx,starty), (endx,endy), action[4])
	
	totaltime += dt
	screen.blit(background, (0, 0))
	allsprites.draw(screen)
	projectiles.draw(screen)
	pygame.display.flip()

