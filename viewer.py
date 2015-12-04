import os, sys
import pygame
from pygame.locals import *

pixels_per_grid = 32
grid_maxx = 8
grid_maxy = grid_maxx
targetfps = 60

def load_image(name, colorkey=None):
	fullname = os.path.join('assets', name)
	try:
	 	image = pygame.image.load(fullname)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image, image.get_rect()


def grid_to_screen(grid_x, grid_y):
	x = clamp(grid_x, 0, grid_maxx)
	y = grid_maxy - clamp(grid_y, 0, grid_maxy) # inverse y coordinate
	return x * pixels_per_grid, y * pixels_per_grid
	
def clamp(n, smallest, largest): 
	return max(smallest, min(n, largest))

class Roboicon(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('robo_r.png', -1)
		self.rect.topleft = grid_to_screen(x, y)
		self.gridx = x
		self.gridy = y
		self.to_gridx = x
		self.to_gridy = x
		self.move = 0, 0

	def move(self, x, y targettime):
		target_x, target_y = grid_to_screen(x, y)
		
		pixels_per_frame = 1.0 / float(targetfps)
		

	def update(self, dt):
		
	

pygame.init()
screen = pygame.display.set_mode((480, 800))
pygame.display.set_caption('Robo test')
pygame.mouse.set_visible(0)


background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

screen.blit(background, (0, 0))
pygame.display.flip()

p1icon = Roboicon()
allsprites = pygame.sprite.RenderPlain((p1icon))
clock = pygame.time.Clock()
exitgame = False
while not exitgame:
	dt = clock.tick(targetfps)
	for event in pygame.event.get():
		if event.type == QUIT:
			exitgame = True
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			exitgame = True
	
	allsprites.update(dt)
	screen.blit(background, (0, 0))
	allsprites.draw(screen)
	pygame.display.flip()

