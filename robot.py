

class Robot:
	def __init__(self, prog, playernum, x, y, arena):
		self.prog = prog
		self.playernum = playernum
		self.x = x
		self.y = y
		self.arena = arena
		self.hp = 10
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
		target = self.arena.raycast(self, dir, 10)
		if target:
			target.reducehp(1)
	
	def reducehp(self, val):
		print("player %d takes damage" % self.playernum)
		self.hp -= val
	
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
		if etype == 'SHOOT':
			self.shoot(expr[1])
		if etype == 'IF':
			print "wtf"
			relop = expr[1]
			newline = expr[2]
			if self.releval(relop):
				self.goto(newline)

	# evaluate relational expression
	def releval(self,expr):
		etype = expr[1]
		if etype == 'DIR':
			target = arena.raycast(self, expr[3], 10)
			if target: 
				return True
			else:
				return False
		elif etype == 'DIRNOT':
			target = arena.raycast(self, expr[3], 10)
			if target: 
				return False
			else:
				return True
		else:
			print "error in rel eval"

	# current opcode at pc
	def opcode(self):
		line  = self.lines[self.pc]
		return self.prog[line]
			
	# runs through program
	def run(self):  		
		while 1:
			instr = self.opcode()
			op = instr[0]

			# END and STOP statements
			if op == 'END':
				break           # We're done
			else:
				self.eval(instr)
				
			self.pc += 1
			
		print("program ended")
		
	# executes single operation
	def step(self):
		instr = self.opcode()
		op = instr[0]
		if op != 'END':
			self.eval(instr)
			self.pc += 1

	def reportstatus(self):
		print("player %d pos:%d,%d hp:%d" % (self.playernum, self.x, self.y, self.hp))