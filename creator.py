import os, sys
import pygame
from pygame.locals import *


targetfps = 60
screen_width = 480
screen_height = 800
fontsize = 36
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Robo creator')
pygame.mouse.set_visible(1)


background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BLACK)

class TextBuffer():
	
	bufferfont = pygame.font.Font(None, fontsize)
	
	def __init__(self, rect):
		self.pos = (0,0) # word, row
		self.text = [[]]
		self.textgfx = None
		self.rect = rect
		self.cursorgfx = pygame.Surface((self.bufferfont.size('_')[0], self.bufferfont.get_linesize()))
		pygame.draw.rect(self.cursorgfx, WHITE, self.cursorgfx.get_rect(), 0)
		self.cursorpos = self.rect.topleft
		self.cursorVisible = False
	
	def addtext(self, t):
		if not t:
			return

		if t[-1] == '\n':
			if len(t) > 1:
				self.text[-1].append(t[:-1]) # new word
			self.text.append([]) # new line
			self.pos = (0, self.pos[1] + 1)
		else:
			self.text[-1].append(t)
			self.pos = (self.pos[0] + 1, self.pos[1])
		self.generategfx()
		
	def delete(self):
		if self.pos[0]:
			del self.text[self.pos[1]][self.pos[0] - 1] #delete word
			self.pos = (self.pos[0] - 1, self.pos[1]) #decrement word
		elif self.pos[1]:
			if not self.text[self.pos[1]]:
				del self.text[self.pos[1]]
			newrow = self.pos[1] - 1
			self.pos = (len(self.text[newrow]), newrow)
		self.generategfx()
	
	
	def generatelines(self):
		res = []
		for l in self.text:
			line = ''
			for w in l:
				if line:
					line += ' '
				line += w
			res.append(line)
		return res
	
	def generategfx(self):
		lines = self.generatelines()
 		# first pass to find out image dimensions
 		w = h = 0
 		i = 0
 		for l in lines:
 			w = max(w, self.bufferfont.size(l)[0])
 			if i == self.pos[1]:
 				self.cursorpos = (self.rect.x + self.bufferfont.size(l)[0], self.rect.y + h)
 			h += self.bufferfont.get_linesize()
 			i += 1

 		self.textgfx = pygame.Surface((w, h))
 		# second pass to render to surface
 		h = 0
 		for l in lines:
 			t = self.bufferfont.render(l, 0, WHITE)
 			self.textgfx.blit(t, (0, h))
 			h += self.bufferfont.get_linesize()

	
	def draw(self, surface):
		if self.textgfx:
			surface.blit(self.textgfx, self.rect)
		surface.blit(self.cursorgfx, self.cursorpos)
	

class TextButton():
	
	buttonfont = pygame.font.Font(None, fontsize)
	
	def __init__(self, text, x, y):
		self.text = text
		textgfx = self.buttonfont.render(text, 0, WHITE)
		textrect = textgfx.get_rect()		
		margin = fontsize / 3
		self.rect = textrect.inflate(margin,margin)
		self.rect.topleft = (0, 0)
		textrect.center = self.rect.center
		self.surface = pygame.Surface(self.rect.size)
		pygame.draw.rect(self.surface, WHITE, self.rect, 3)
		self.surface.blit(textgfx, textrect)
		self.rect.topleft = (x, y)
		self.pressed = False
		
	def draw(self, surface):
		surface.blit(self.surface, self.rect)

	def handleEvent(self, eventObj):
		if eventObj.type == MOUSEBUTTONDOWN and self.rect.collidepoint(eventObj.pos):
			self.pressed = True
		elif self.pressed and eventObj.type == MOUSEBUTTONUP:
			if self.rect.collidepoint(eventObj.pos):
				return self.text
			self.pressed = False


class TextButtonGroup():
	
	xspacing = 3
	yspacing = 3
	
	def __init__(self, x, y, width, *args):
		self.buttons = []
		startx = x
		for a in args:
			button = TextButton(a,x,y)
			if button.rect.width < width and button.rect.right > startx + width:
				y = button.rect.bottom + self.yspacing
				x = startx
				button.rect.topleft = (x,y)
			self.buttons.append(button)
			x = button.rect.right + self.xspacing
			
	def draw(self, surface):
		for b in self.buttons:
			b.draw(surface)
	
	def handleEvent(self, eventObj):
		for b in self.buttons:
			retval = b.handleEvent(event)
			if retval:
				return retval
		return retval


class InputState():
	states = {
		0: [(1,'move'),(1,'shoot'),(2,'if'),(2,'while'),(0,'loop\n')],
		1: [(0,'north\n'),(0,'west\n'),(0,'south\n'),(0,'east\n')], 
		2: [(3,'my robot'),(5,'enemy'),(5,'block')],
		3: [(4,'is within enemy range'), (4,'is not within enemy range')],
		4: [(2,'and\n'),(2,'or\n'),(0,'[ENTER]')],
		5: [(6,'is'),(6,'is not'),(8,'in')],
		6: [(7,'somewhere'),(7,'directly'),(4,'north'),(4,'west'),(4,'south'),(4,'east')],
		7: [(4,'north'),(4,'west'),(4,'south'),(4,'east')],
		8: [(9,'somewhere'),(9,'directly'),(10,'north'),(10,'west'),(10,'south'),(10,'east')],
		9: [(10,'north'),(10,'west'),(10,'south'),(10,'east')],
		10: [(11, 'is within'),(11, 'is not within')],
		11: [(4,'range'),(12,'1'),(12,'2'),(12,'3'),(12,'4'),(12,'5'),(12,'6'),(12,'7'),(12,'8'),(12,'9')],
		12: [(4,'block')]
		}

	def __init__(self):
		self.istate = [0]

	def gettextlist(self):
		retval = []
		for t in self.states[self.istate[-1]]:
			retval.append(t[1])
		return retval
		
	def nextstate(self,text):
		for t in self.states[self.istate[-1]]:
			if t[1] == text:
				self.istate.append(t[0])
				
	def prevstate(self):
		if len(self.istate) > 1:
			self.istate.pop()
		

class InputManager():
	def __init__(self, x, y, width):
		self.x = x
		self.y = y
		self.width = width
		self.inputstates = InputState()
		self.buttons = TextButtonGroup(x,y,width,*self.inputstates.gettextlist())
		
	def draw(self, surface):
		self.buttons.draw(surface)
	
	def handleEvent(self, eventObj):
		text = self.buttons.handleEvent(eventObj)
		if text:
			self.inputstates.nextstate(text)
			self.buttons = TextButtonGroup(self.x,self.y,self.width,*self.inputstates.gettextlist())
		if text == '[ENTER]':
			text = '\n'
		return text


screen.blit(background, (0, 0))
pygame.display.flip()

inputmgr = InputManager(10, 700, 470)
textbfr = TextBuffer(pygame.Rect(10, 10, 470, 680))

exitgame = False
clock = pygame.time.Clock()
while not exitgame:
	dt = clock.tick(targetfps)
	for event in pygame.event.get():
		if event.type == QUIT:
			exitgame = True
			break
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			exitgame = True
			break
		t = inputmgr.handleEvent(event)
		if t:
			textbfr.addtext(t)
			
	screen.blit(background, (0, 0))
	inputmgr.draw(screen)
	textbfr.draw(screen)
	pygame.display.flip()
