from ply import *


reserved = {
	'MOVE' : 'MOVE',
	'SHOOT' : 'SHOOT',
	'IF' : 'IF',
	'ENDIF' : 'ENDIF',
	'IS' : 'IS',
	'ENEMY' : 'ENEMY',
	'NOT' : 'NOT',		
	'N' : 'NORTH',
	'S' : 'SOUTH',
	'E' : 'EAST',
	'W' : 'WEST',
	'END' : 'END'
}


tokens = [
	'COMMAND','COMMENT','NEWLINE',
] + list(reserved.values())


t_ignore = ' \t'

t_ignore_COMMENT = r'\#.*'

def t_COMMAND(t):
	r'[A-Z][A-Z]*'
	t.type = reserved.get(t.value)
	if t.type is not None:
		return t
	

def t_NEWLINE(t):
	r'\n'
	t.lexer.lineno += 1
	return t

	

def t_error(t):
	print("Illegal character %s" % t.value[0])
	t.lexer.skip(1)

lexer = lex.lex(debug=1)
