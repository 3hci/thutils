#!/usr/bin/env python
import sys
import os, time, re, types
from thwap.utils import config
from thwap.utils import options
from thwap.dbm import mysql
from thwap.utils import log
# Declare our eptions and optionally
# a default error string.
noHostError = ''
noUserError = ''
noDatabaseError = ''

# DB Connection Class
# figure it out
class DBConn(mysql.DBase):
	def __init__(self, hst='', usr='', pswd='', dbase=''):
		mysql.DBase.__init__(self, hostname=hst, username=usr, password=pswd, database=dbase)

	def secBehind(self, table=''):
		self.cr.execute('SHOW SLAVE STATUS;')
		row = self.cr.fetchone()
		return row[len(row)-1] 

	def getError(self):
		self.cr.execute('SHOW SLAVE STATUS;')
		row = self.cr.fetchone()
		#if row[19].find('Query') != -1 and row[19].find('error on master: 1053') != -1 and row[19].find('INSERT INTO product_page_views') != -1:
		#	sql = row[19].split('Query:')[1]
			#self.cr.cute('use usage_logs;')
			#self.cr.cute(sql.strip()[1:][:-1]+';')
		#	self.cr.execute('SET GLOBAL SQL_SLAVE_SKIP_COUNTER=1; START SLAVE;')


class DBObj:
	def __init__(self, name='', host='', user='', passwd=''):
		global VERBOSE
		global LOG
		self.db = DBConn(hst=host, usr=user, pswd=passwd)
		self.seconds_behind = self.db.secBehind('wfl_ticket')
		self.name = name
		if self.seconds_behind == None:
			if VERBOSE == True:
				LOG.msg('ERROR: host %s\'s replication status is DOWN.' % host)
			self.status = 'Down'
			#while self.db.secBehind('wfl_ticket') == None:
			#	print 'skipping another insert to product_page_views'
			#	self.db.getError()
		elif type(self.seconds_behind) == types.LongType:
			self.status = 'Up'
		else:
			self.status = 'Down'
			if VERBOSE == True:
				LOG.msg('ERROR: host %s\'s replication status is DOWN.' % host)

REP_REPAIR = False
REP_AUTO_REPAIR = False
VERBOSE = False
LOG = log.Log(prog='repCheck.py')

map = ['Usage: %prog <options>']
map.append(['-r','--repair','store_true','Attempt to repair basic replication issues.'])
map.append(['-a','--auto','store_true','Do not prompt for repairs, automatically attempt repairs.'])
map.append(['-v','--verbose','store_true','Store verbose logging messages.'])
opts = options.Options(map)
if opts.opts.repair == True: 
	REP_REPAIR = True 
if opts.opts.auto == True: 
	REP_AUTO_REPAIR = True 
if opts.opts.verbose == True: 
	print 'Verbose mode: ON'
	VERBOSE = True 

secAhead = None
tdb = None
ot = None

LOG.msg('INFO: Loading configuration data.')
cfg = config.Config('repCheck')
srvrs = cfg.getMap()
dbos = []
sys.stdout.write('Creating DB Objects: ')
sys.stdout.flush()
print srvrs
for a in srvrs.keys():
	sys.stdout.write(a+' ')
	sys.stdout.flush()
	if VERBOSE == True:
		LOG.msg('INFO: Creating database connection to host: %s' % srvrs[a]['hostname'])
	dbos.append(DBObj(name=a, host=srvrs[a][
	dbos.append(DBObj(name=a, host=srvrs[a]['hostname'], user=srvrs[a]['username'], passwd=srvrs[a]['password']))
behind_master = {}
for a in dbos:
	behind_master[a.name] = a.seconds_behind
tstr = ''
for a in behind_master.keys():
	tstr = tstr+a+':('+str(behind_master[a])+') '
print ''
print tstr
LOG.msg(tstr)

