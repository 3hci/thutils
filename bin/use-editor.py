#!/usr/bin/env python
import os, sys, popen2

class UseEd:
	def __init__(self, pkgs=''):
		self.pkgs = pkgs
		self.mkmap()	
		self.editFlags()

	def mkmap(self):
		sys.stdout.write('>>> Please wait, gathering USE flag data ... ')
		sys.stdout.flush()
		# This is a two stage mapper
		# Stage 1: Collect all the lines with USE flags from pretend output
		lines = []
		o = popen2.Popen4('EMERGE_DEFAULT_OPTS="-vpuD" emerge %s' % self.pkgs)
		buff = o.fromchild.readline()
		while buff != '':
			if buff.strip().find('USE') != -1:
				lines.append(buff.strip())
			buff = o.fromchild.readline()
		# Stage 2: Parse each of the lines into a dictionary
		# containing: {type: ebuild/binary, package: name-vers-rev, flags: uflags}
		# then we can go about editing in later stages
		data = []
		for i in lines:
			tmp = {}
			tmp['type'] = i.split()[0].split('[')[1]
			tmp['package'] = i.split()[3]
			tmp['flags'] = i.split('"')[1]
			data.append(tmp)
		self.data = data
		print 'Done'
	
	def isDup(self, lst=[], itm=''):
		for i in lst:
			if i == itm:
				return True
		return False

	def editFlags(self):
		# generate a map of all flags that are turned on or off
		flag_on = []
		flag_off = []
		for a in self.data:
			for b in a['flags'].split():
				if b[:1] == '-':
					if not self.isDup(flag_off, b): flag_off.append(b)
				else:
					if b[:1] == '(' and b[1] == '-':
						if not self.isDup(flag_off, b): flag_off.append(b)
					else:
						if not self.isDup(flag_on, b): flag_on.append(b)
		self.dumpInterface(flag_on, flag_off)
	
	def formatRows(self, str):
		count = 0
		retv = '    '
		for a in str.strip().split():
			count += 1
			if count < 6:
				retv = retv+a+'\t'
			if count >= 6:
				retv = retv+'\n    '+a+'\t'
				count = 1
		return retv

	def dumpInterface(self, on=[], off=[]):
		os.system('clear')
		print "Packages:"
		print '-'*79
		for a in self.data:
			if a['type'] == 'ebuild':
				print '%s:\n  %s' % (a['package'], self.formatRows(a['flags']))
		print ''
		print 'Currently off USE flags:'
		print '-'*79
		st = ''
		for b in off:
			st = st+b+' '
		print self.formatRows(st)

if __name__ == '__main__':
	o = UseEd('evolution')
