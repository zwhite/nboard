#!/usr/bin/env python

import cgi, cgitb, ConfigParser, os, rrdtool, sys, tempfile, time, urllib
cgitb.enable(logdir="/tmp")

# Pull in our configuration
config = ConfigParser.SafeConfigParser()
config.read('conf/datasources.ini')

# Colors for the graphs
areaColors = ['#FF0000', '#EA8F00', '#EACC00', '#00FF00']
lineColors = ['#CCCCCC', '#999999', '#666666', '#333333', '#000000']
# Variables
form = cgi.FieldStorage()
ds=form.getfirst('datasource')
dataSource={}
area=[]
line=[]
for option, value in config.items(ds):
    if option == 'display':
        dataSource[option] = config.getboolean(ds, option)
    elif option == 'area':
        area = value.replace(' ','').split(',')
    elif option == 'line':
        line = value.replace(' ','').split(',')
    else:
        dataSource[option] = value
graphHeight=form.getfirst('height')
graphWidth=form.getfirst('width')
if 'start' in form:
    startTime=int(form.getfirst('start'))
    endTime=startTime + 86400
else:
    endTime=int(time.time())
    startTime=endTime - 86400
if 'end' in form:
    endTime=int(form.getfirst('end'))

# Fetch the remote RRD(s)
fd, rrdfile=tempfile.mkstemp()
rrdurlfd=urllib.urlopen(dataSource['url'])
rrdfd = open(rrdfile, 'w')
rrdfd.seek(0)
rrdfd.write(rrdurlfd.read())
rrdfd.close()

# Build our graph command
graphcmd=[]
graphcmd.append('--title "%s"' % dataSource['title'])
graphcmd.append('--lower-limit=0')
if dataSource.has_key('max'):
	graphcmd.append('--upper-limit=%s' % dataSource['max'])
	graphcmd.append('--rigid')
graphcmd.append('--start=%s' % startTime)
graphcmd.append('--end=%s' % endTime)
graphcmd.append('--imgformat PNG')
graphcmd.append('--height %s' % graphHeight)
graphcmd.append('--width %s' % graphWidth)
firstArea = True
for a in area:
    if firstArea:
        firstArea = False
        areatype = 'AREA'
    else:
        areatype = 'STACK'
    graphcmd.append('DEF:%(ds)s=%(rrdfile)s:%(ds)s:AVERAGE' % \
      {'ds': a, 'rrdfile': rrdfile})
    graphcmd.append('%(atype)s:%(ds)s%(color)s:%(ds)s' % {'atype': areatype, 'ds': a, 'color': areaColors.pop()})
    graphcmd.append('GPRINT:%(ds)s:LAST:" Current\\: %%lf"' % {'ds': a})
    graphcmd.append('GPRINT:%(ds)s:AVERAGE:" Average\\: %%lf"' % {'ds': a})
    graphcmd.append('GPRINT:%(ds)s:MAX:" Max\\: %%lf\\n"' % {'ds': a})
for l in line:
    graphcmd.append('DEF:%(ds)s=%(rrdfile)s:%(ds)s:AVERAGE' % \
      {'ds': l, 'rrdfile': rrdfile})
    graphcmd.append('LINE:%(ds)s%(color)s:%(ds)s' % {'ds': l, 'color': lineColors.pop()})
    graphcmd.append('GPRINT:%(ds)s:LAST:" Current\\: %%lf"' % {'ds': l})
    graphcmd.append('GPRINT:%(ds)s:AVERAGE:" Average\\: %%lf"' % {'ds': l})
    graphcmd.append('GPRINT:%(ds)s:MAX:" Max\\: %%lf\\n"' % {'ds': l})
graphcmds=' '.join(graphcmd)

# Do something with the RRD
fd, graphfile=tempfile.mkstemp()
os.system('echo rrdtool graph %s %s > /tmp/rrdtool_output' % (graphfile, graphcmds))
os.system('rrdtool graph %s %s >> /tmp/rrdtool_output' % (graphfile, graphcmds))

# Send the user the generated graph
print 'Content-Type: image/png\n'
graphfd=open(graphfile)
print graphfd.read()

# Cleanup
os.remove(rrdfile)
os.remove(graphfile)
