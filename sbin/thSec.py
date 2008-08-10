#!/usr/bin/env python
#
# Copyright (c) 2007 Academic Superstore
# Copyright (c) 2007 Mike "Fuzzy" Partin <fuzzy@academicsuperstore.com>
#
# thUtils library path insert
import sys
sys.path.append('/utils/lib')
# Program code
import os, popen2
from optparse import OptionParser
from thwap.system import glsa
from thwap.utils import slurp

def emerge_parse(st):
	if st.find('Calculating') != -1:
		sys.stdout.write('>>> Calculating dependancies'+(' '*70)+'\r')
	elif st.find('>>>') != -1:
		sys.stdout.write(st.strip()+(' '*60)+'\r')
	sys.stdout.flush()

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-s', dest='rhost', help='Specify a remote host.', metavar='RHST')
	parser.add_option('-u', dest='ruser', help='Specify a remote user.', metavar='RUSR')
	parser.add_option('-r', action='store_true', dest='repr', default='False', help='Automatically apply security patches.')
	(opts,args) = parser.parse_args()
	
	gsobj = glsa.GLSA(opts.ruser, opts.rhost)
	gsobj.check()
	if opts.repr == True:
		for aff in gsobj.affectd.keys():
			print 'Attempting to automatically apply fix for GLSA %s.' % aff
			obj = slurp.Proc()
			obj.register_trigger({'t_pattern': '^.*', 't_callback': emerge_parse})
			if opts.rhost != None and opts.ruser != None:
				cmd = 'ssh %s@%s "%s -nf %s"' % (gsobj.user,gsobj.host,gsobj.glsa,aff)
				pd = popen2.Popen4(cmd)
			else:
				cmd = '%s -nf %s' % (gsobj.glsa, aff)
				pd = popen2.Popen4(cmd)
			obj.run(pd.fromchild)
			print ''


