

class Robot:
	def __init__(self, prog, playernum, x, y, arena):
		self.prog = prog
		self.playernum = playernum
		self.x = x
		self.y = y
		self.arena = arena
		self.hp = 10
		self.weaponrange = 5
		self.lines = list(self.prog)
		self.lines.sort()
		self.pc = 0
	
	def move(self, dir):
		if not self.arena.raycast(self, dir, 1):
			if dir == 'NORTH':
				self.y += 1
			if dir == 'EAST':
				self.x += 1
			if dir == 'SOUTH':
				self.y -= 1
			if dir == 'WEST':
				self.x -= 1
	
	def shoot(self, dir):
		print("player %d shoot %s" % (self.playernum, dir))
		target = self.arena.raycast(self, dir, self.weaponrange)
		if target:
			target.reducehp(1)
	
	def reducehp(self, val):
		print("player %d takes damage" % self.playernum)
		self.hp -= val
	
	def typestr(self):
		return 'ROBOT'
	
	def programended(self):
		return self.opcode()[0] == 'END'
	
	def goto(self,linenum):
		if not linenum in self.prog:
		  print("UNDEFINED LINE NUMBER %d AT LINE %d" % (linenum, self.lines[self.pc]))
		  raise RuntimeError
		self.pc = self.lines.index(linenum)
	
	# Evaluate an expression
	def eval(self, expr):
		etype = expr[0]
		if etype == 'MOVE':
			self.move(expr[1])
			self.pc += 1
		elif etype == 'SHOOT':
			self.shoot(expr[1])
			self.pc += 1
		elif etype == 'IF':
			relop = expr[1]
			newline = expr[2]
			if not self.releval(relop):
				self.goto(newline)
			else:
				self.pc += 1
		elif etype == 'GOTO':
			self.goto(expr[1])
		elif etype == 'NOP':
			self.pc += 1

	# evaluate relational expression
	def releval(self,expr):
		etype = expr[0]
		if etype == 'OR':
			return self.releval(expr[1]) or self.releval(expr[2])
		elif etype == 'AND':
			return self.releval(expr[1]) and self.releval(expr[2])
		elif etype == 'DIR' or etype == 'DIRNOT':
			target = self.arena.raycast(self, expr[1], 10)
			typestr = target.typestr()
			if typestr == 'ROBOT':
				typestr = 'ENEMY'
			if etype == 'DIR':
				return typestr == expr[2]
			else:
				return typestr != expr[2]
		else:
			print "error in rel eval"

	# current opcode at pc
	def opcode(self):
		line  = self.lines[self.pc]
		return self.prog[line]
			
	# runs through program
	def run(self):  		
		while not self.programended():
			self.step()
			
		print("program ended")
		
	# executes single operation
	def step(self):
		instr = self.opcode()
		self.eval(instr)

	def reportstatus(self):
		print("player %d pos:%d,%d hp:%d" % (self.playernum, self.x, self.y, self.hp))
