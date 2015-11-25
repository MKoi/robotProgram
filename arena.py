from random import randint
import math
import sys

class Block:
	def reducehp(self, val):
		print("block takes damage")
	def typestr(self):
		return 'BLOCK'

class Arena:
	def __init__(self, height, width, debug=0):
		self.height = height
		self.width = width
		self.players = []
		self.debug = debug
		
	def freepos(self):
		x, y = randint(0, self.width-1), randint(0, self.height-1)
		i = 0
		while not self.emptypos(x, y) and i < 10:
			x, y = randint(0, self.width-1), randint(0, self.height-1)
			i += 1
		return (i < 10), x, y
	
	def distance(self, A, B):
		dx = (A.x-B.x)
		dy = (A.y-B.y)
		return int(math.sqrt(dx**2 + dy**2))

	def getnearest(self, orig, others=None):
		if not others:
			others = self.players
		mindist = sys.maxsize
		nearest = None
		for p in others:
			if p and p != orig:
				dist = self.distance(orig, p)
				if dist < mindist:
					mindist = dist
					nearest = p
		return nearest

	def isadjacent(self, A, B):
		return abs(A.x - B.x) <= 1 and abs(A.y - B.y) <= 1

	def lineofsigth(self, A, B):
		if self.isadjacent(A, B):
			return True
		points = self.line(A, B)
		return all(self.emptypos(p[0], p[1]) for p in points[1:-1])
			

	def line(self, A, B):
		# Bresenham's Line Algorithm

		# Setup initial conditions
		x1, y1 = A.x, A.y
		x2, y2 = B.x, B.y
		dx = x2 - x1
		dy = y2 - y1
		
		# Determine how steep the line is
		is_steep = abs(dy) > abs(dx)
		
		# Rotate line
		if is_steep:
			x1, y1 = y1, x1
			x2, y2 = y2, x2
		
		# Swap start and end points if necessary and store swap state
		swapped = False
		if x1 > x2:
			x1, x2 = x2, x1
			y1, y2 = y2, y1
			swapped = True
		
		# Recalculate differentials
		dx = x2 - x1
		dy = y2 - y1
		
		# Calculate error
		error = int(dx / 2.0)
		ystep = 1 if y1 < y2 else -1
		
		# Iterate over bounding box generating points between start and end
		y = y1
		points = []
		for x in range(x1, x2 + 1):
			coord = (y, x) if is_steep else (x, y)
			points.append(coord)
			error -= abs(dy)
			if error < 0:
			  y += ystep
			  error += dx
		
		# Reverse the list if the coordinates were swapped
		if swapped:
			points.reverse()
		return points
		
	def addplayer(self, player):
		if self.isinside(player.x, player.y) and self.emptypos(player.x, player.y):
			self.players.append(player)
	
	def emptypos(self, x, y):
		return all((x != p.x and y != p.y) for p in self.players)
	
	def isinside(self, x, y):
		return (x < self.width and x >= 0 and y < self.height and y >= 0)
			
	
	def objectinarea(self, obj, x1, y1, x2, y2):
		minx, miny = min(x1, x2), min(y1, y2)
		maxx, maxy = max(x1, x2), max(y1, y2)
		if obj.x >= minx and obj.x <= maxx and obj.y >= miny and obj.y <= maxy:
			if self.debug: print("%d,%d in area from %d,%d to %d,%d" % (obj.x, obj.y, minx, miny, maxx, maxy))
			return obj
		else:
			return None
	
	def clamp(self, n, smallest, largest):
		return max(smallest, min(n, largest))
	
	def clamptoarea(self, x, y):
		newx, newy =  self.clamp(x, 0, self.width - 1), self.clamp(y, 0, self.height - 1)
		return (newx != x or newy != y), newx, newy
				
	
	def objectindir(self, orig, dir, maxrange = 10):
		beamlength = maxrange
		if dir[-3:] == 'ISH':
			beamwidth = maxrange / 2
			dir = dir[:-3]
		else:
			beamwidth = 0
		endx, endy = orig.x, orig.y
		startx, starty = orig.x, orig.y
		if dir == 'NORTH':
			endx, endy = orig.x + beamwidth, orig.y + beamlength
			startx, starty = orig.x - beamwidth, orig.y + 1
		elif dir == 'EAST':
			endx, endy = orig.x + beamlength, orig.y + beamwidth
			startx, starty = orig.x + 1, orig.y - beamwidth
		elif dir == 'SOUTH':
			endx, endy = orig.x + beamwidth, orig.y - beamlength
			startx, starty = orig.x - beamwidth, orig.y - 1
		elif dir == 'WEST':
			endx, endy = orig.x - beamlength, orig.y + beamwidth
			startx, starty = orig.x - 1, orig.y - beamwidth
		else:
			return None
		clampedstart, startx, starty = self.clamptoarea(startx, starty)
		clampedend, endx, endy = self.clamptoarea(endx, endy)
		objects = [self.objectinarea(p, startx, starty, endx, endy) for p in self.players]
		nearest = self.getnearest(orig, objects)
		if nearest:
			return nearest
		elif clampedstart or clampedend:
			return Block()
		return None