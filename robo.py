import sys
import os
from fractions import Fraction
import cProfile, pstats, StringIO

import robolex
import roboparse
import robot
import arena

debug = 0
profiler = 0

def printprogtable(p):
	if p and debug:
		for key, data in p.items():
			print('{} : {}'.format(key, data))

def startProfiler(p):
	if p and profiler:
		p.enable()

def stopProfiler(p):
	if p and profiler:
		p.create_stats()
		printstats(p)

def printstats(profiler):
	s = StringIO.StringIO()
	sortby = 'cumulative'
	ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
	ps.print_stats()
	print s.getvalue()


def getcycletime(i):
	return Fraction(1,2) if i%2 == 0 else Fraction(1,3)


w = 8
h = 8
a = arena.Arena(h,w)
players = []


filenames = []
for i in range(1,len(sys.argv)):
	arg = sys.argv[i]
	if arg == 'debug':
		debug = 1
	elif arg == 'profile':
		profiler = 1
	else:
		filenames.append(os.path.normpath(arg))

pr = None
if profiler:
	pr = cProfile.Profile()
	
startProfiler(pr)
outputfile = open('trace.txt', 'w')
roboparse.init(debug)
for i in range(0,len(filenames)):
	data = open(filenames[i]).read()
	if data:
		prog = roboparse.parse(data, debug)
		printprogtable(prog)
		if prog:
			valid, x, y = a.freepos()
			if valid:
				r = robot.Robot(prog, i, x, y, a, getcycletime(i), Fraction(0), outputfile)
				players.append(r)
				a.addplayer(r)
stopProfiler(pr)
	
dt = Fraction(1)
for p in players:
	if p.cycletime < dt:
		dt = p.cycletime

startProfiler(pr)
try:
	maxtime = Fraction(20)
	currenttime = Fraction(0)
	while currenttime < maxtime:
		print float(currenttime)
		outputfile.write('t:{0};\n'.format(robot.to_ms(currenttime)))
		for p in players:
			p.step(currenttime)
			p.reportstatus()
		if all(p.programended() for p in players):
			break
		currenttime += dt
except RuntimeError:
	pass
stopProfiler(pr)
outputfile.close()
