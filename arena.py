from random import randint

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
				
	
	def raycast(self, orig, dir, maxrange = 10):
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
		for o in objects:
			if o and o != orig: return o
		if clampedstart or clampedend:
			return Block()