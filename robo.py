import sys
import os

import robolex
import roboparse
import robot
import arena

def printprogtable(p):
	for key, data in p.items():
		print('{} : {}'.format(key, data))


w = 4
h = 4
a = arena.Arena(h,w)
i = 1
players = []
while i < len(sys.argv):
	arg = sys.argv[i]
	filename = os.path.normpath(arg)
	data = open(filename).read()
	if data:
		prog = roboparse.parse(data)
		printprogtable(prog)
		if prog:
			valid, x, y = a.freepos()
			if valid:
				r = robot.Robot(prog, i, x, y, a)
				players.append(r)
				a.addplayer(r)
	i += 1

try:
	while 1:
		for p in players:
			p.step()
			p.reportstatus()
		if all(p.programended() for p in players):
			break
except RuntimeError:
	pass
