from ply import *
import robolex

tokens = robolex.tokens

#### We represent the program as a dictionary of tuples indexed by line number.

def p_program(p):
	'''program : statements END
							| statements END NEWLINE'''
	p[0] = p[1]
	p[0][p.lineno(2)] = ('END',)


#### This catch-all rule is used for any catastrophic errors.  In this case,
#### we simply return nothing

def p_program_error(p):
	'''program : error'''
	p[0] = None
	p.parser.error = 1

def p_statements(p):
	'''statements : statements statement
							| statement'''
	if len(p) == 2 and p[1]:
		p[0] = { }
		line,stats = p[1]
		p[0][line] = stats
	elif len(p) == 3:
		p[0] = p[1]
		if not p[0]: p[0] = { }
		if p[2]:
			line,stats = p[2]
			p[0][line] = stats	

def p_statements_if(p):
	'''statements : IF relexpr NEWLINE statements ENDIF
							| statements IF relexpr NEWLINE statements ENDIF'''
	if len(p) == 6:
		p[0] = p[4]
		if not p[0]: p[0] = { }
		p[0][p.lineno(1)] = ('IF',p[2],p.lineno(5),)
		p[0][p.lineno(5)] = ('NOP',)
		
	elif len(p) == 7:
		p[0] = p[5]
		if not p[0]: p[0] = { }
		p[0][p.lineno(2)] = ('IF',p[3],p.lineno(6),)
		p[0][p.lineno(6)] = ('NOP',)
		p[0].update(p[1])


def p_statement(p):
	'''statement : command NEWLINE'''
	if isinstance(p[1],str):
		print("%s %s %s" % (p[2],"AT LINE", p[1]))
		p[0] = None
		p.parser.error = 1
	else:
		p[0] = (p.lineno(2),p[1])


def p_statement_bad(p):
	'''statement : error NEWLINE'''
	print("SYNTAX ERROR AT LINE %d" % p.lineno(2))
	p[0] = None
	p.parser.error = 1

#### Blank line

def p_statement_newline(p):
	'''statement : NEWLINE'''
	p[0] = None


#### commands
def p_command_move(p):
	'''command : MOVE direction'''
	p[0] = ('MOVE', p[2])
	
def p_command_shoot(p):
	'''command : SHOOT direction'''
	p[0] = ('SHOOT', p[2])




def p_command_end(p):
	'''command : END'''
	p[0] = ('END',)

#### directions
def p_dir_south(p):
	'''direction : SOUTH'''
	p[0] = 'SOUTH'

def p_dir_north(p):
	'''direction : NORTH'''
	p[0] = 'NORTH'
	
def p_dir_east(p):
	'''direction : EAST'''
	p[0] = 'EAST'
	
def p_dir_west(p):
	'''direction : WEST'''
	p[0] = 'WEST'



def p_relexpr_dir(p):
	'''relexpr : object IS direction'''
	p[0] = ('DIR',p[3],p[1])

	
def p_relexpr_dir_neg(p):
	'''relexpr : object IS NOT direction'''
	p[0] = ('DIRNOT',p[4],p[1])

def p_object_enemy(p):
	'''object : ENEMY'''
	p[0] = 'ENEMY'

def p_object_block(p):
	'''object : BLOCK'''
	p[0] = 'BLOCK'

#### Catastrophic error handler
def p_error(p):
	if not p:
		print("SYNTAX ERROR AT EOF")

roboparser = yacc.yacc()

def parse(data,debug=0):
    roboparser.error = 0
    robolex.lexer.lineno = 1
    p = roboparser.parse(data,debug=debug)
    if roboparser.error: return None
    return p
