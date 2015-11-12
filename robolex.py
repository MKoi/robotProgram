from ply import *


reserved = {
	'MOVE' : 'MOVE',
	'SHOOT' : 'SHOOT',
	'IF' : 'IF',
	'AND' : 'AND',
	'OR' : 'OR',
	'ENDIF' : 'ENDIF',
	'WHILE' : 'WHILE',
	'ENDWHILE' : 'ENDWHILE',
	'LOOP' : 'LOOP',
	'ENDLOOP' : 'ENDLOOP',
	'SOMEWHERE' : 'SOMEWHERE',
	'DIRECTLY' : 'DIRECTLY',
	'IS' : 'IS',
	'ENEMY' : 'ENEMY',
	'MYROBOT' : 'MYROBOT',
	'RANGE' : 'RANGE',
	'WITHIN' : 'WITHIN',
	'NOT' : 'NOT',		
	'N' : 'NORTH',
	'S' : 'SOUTH',
	'E' : 'EAST',
	'W' : 'WEST',
	'END' : 'END',
	'BLOCK' : 'BLOCK'
}


tokens = [
	'COMMAND','COMMENT','NEWLINE','NUM'
] + list(reserved.values())


t_ignore = ' \t'

t_ignore_COMMENT = r'\#.*'

def t_COMMAND(t):
	r'[A-Z][A-Z]*'
	t.type = reserved.get(t.value)
	if t.type is not None:
		return t

def t_NUM(t):
	r'[0-9]+'
	try:
		t.value = int(t.value)
	except ValueError:
		print("Integer value too large %d", t.value)
		t.value = 0
	return t
	

def t_NEWLINE(t):
	r'\n+'
	t.lexer.lineno += 1
	return t

	

def t_error(t):
	print("Illegal character %s" % t.value[0])
	t.lexer.skip(1)

lexer = lex.lex(debug=1)
