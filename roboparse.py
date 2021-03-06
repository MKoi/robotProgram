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
	'''statements : IF relexpr_or NEWLINE statements ENDIF
							| statements IF relexpr_or NEWLINE statements ENDIF'''
	if len(p) == 6:
		ifindex, innerindex, exprindex, endindex = 1,4,2,5
	elif len(p) == 7:
		ifindex, innerindex, exprindex, endindex = 2,5,3,6
	p[0] = p[innerindex]
	if not p[0]: p[0] = { }
	p[0][p.lineno(ifindex)] = ('IF',p[exprindex],p.lineno(endindex)+1,)
	if len(p) == 7:
		p[0].update(p[1])

def p_statements_while(p):
	'''statements : WHILE relexpr_or NEWLINE statements ENDWHILE
							| statements WHILE relexpr_or NEWLINE statements ENDWHILE'''
	if len(p) == 6:
		ifindex, innerindex, exprindex, endindex = 1,4,2,5
	elif len(p) == 7:
		ifindex, innerindex, exprindex, endindex = 2,5,3,6
	p[0] = p[innerindex]
	if not p[0]: p[0] = { }
	p[0][p.lineno(ifindex)] = ('IF',p[exprindex],p.lineno(endindex)+1,)
	p[0][p.lineno(endindex)] = ('GOTO', p.lineno(ifindex),)
	if len(p) == 7:
		p[0].update(p[1])

def p_statements_loop(p):
	'''statements : LOOP NEWLINE statements ENDLOOP
							| statements LOOP NEWLINE statements ENDLOOP'''
	
	if len(p) == 5:
		comindex, innerindex, endindex = 1,3,4
	elif len(p) == 6:
		comindex, innerindex, endindex = 2,4,5
	p[0] = p[innerindex]
	if not p[0]: p[0] = { }
	p[0][p.lineno(comindex)] = ('NOP',)
	p[0][p.lineno(endindex)] = ('GOTO', p.lineno(comindex),)
	if len(p) == 6:
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

def p_statement_empty(p):
	'''statement : '''

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

def p_adv_direction(p):
	'''adv_direction : SOMEWHERE direction
									| DIRECTLY direction
									| direction'''
	if p[1] == 'SOMEWHERE':
		p[0] = p[2] + 'ISH'
	elif p[1] == 'DIRECTLY':
		p[0] = p[2]
	else:
		p[0] = p[1]


def p_relexpr_or(p):
	'''relexpr_or : relexpr_or OR relexpr_and
								| relexpr_and'''
	if len(p) == 4:
		p[0] = ('OR', p[1], p[3])
	elif len(p) == 2:
		p[0] = p[1]


def p_relexpr_and(p):
	'''relexpr_and : relexpr_and AND relexpr
								| relexpr'''
	if len(p) == 4:
		p[0] = ('AND', p[1], p[3])
	elif len(p) == 2:
		p[0] = p[1]


def p_relexpr_dir(p):
	'''relexpr : object_plain IS adv_direction'''
	p[0] = ('DIR',p[3],p[1])

	
def p_relexpr_dir_neg(p):
	'''relexpr : object_plain IS NOT adv_direction'''
	p[0] = ('DIRNOT',p[4],p[1])


def p_relexpr_range(p):
	'''relexpr : object_spec IS WITHIN distance
						| MYROBOT IS WITHIN ENEMY RANGE'''
	p[0] = ('RANGE',p[1],p[4])

	
def p_relexpr_range_neg(p):
	'''relexpr : object_spec IS NOT WITHIN distance
						| MYROBOT IS NOT WITHIN ENEMY RANGE'''
	p[0] = ('RANGENOT',p[5],p[1])


def p_distance(p):
	'''distance : RANGE
							| NUM BLOCK'''
	p[0] = p[1]

def p_object_plain(p):
	'''object_plain : ENEMY
						| BLOCK'''
	p[0] = p[1]

def p_object_spec(p):
	'''object_spec : object_plain IN adv_direction'''
	p[0] = p[1] + '_' + p[3]


#### Catastrophic error handler
def p_error(p):
	if not p:
		print("SYNTAX ERROR AT EOF")

lexer = None
roboparser = None

def init(debug=0):
	global lexer, roboparser
	lexer = lex.lex(module=robolex, debug=debug)
	roboparser = yacc.yacc()
	

def parse(data,debug=0):
	if not lexer or not roboparser:
		return None
	roboparser.error = 0
	lexer.lineno = 1
	p = roboparser.parse(data, debug=debug, lexer=lexer)
	if roboparser.error: return None
	return p
