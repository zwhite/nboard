#!/usr/bin/env python

import cgi, cgitb, ConfigParser, os, rrdtool, sys, tempfile, time, urllib
#from rrdinfo import dataSources
cgitb.enable(logdir="/tmp")

# Pull in our configuration
config = ConfigParser.SafeConfigParser()
config.read('conf/datasources.ini')
dataSources = {}
for section in config.sections():
    dataSources[section] = {}
    for option, value in config.items(section):
        dataSources[section][option] = value

# Variables
form = cgi.FieldStorage()
if 'datasource' in form:
    datasource=form.getlist('datasource')
else:
    datasource=[]
if 'area' in form:
    area=form.getlist('area')
else:
    area=datasource
if 'line' in form:
    line=form.getlist('line')
else:
    line=[]
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
rrdfiles = []
for source in datasource:
    fd, rrdfile=tempfile.mkstemp()
    rrdurlfd=urllib.urlopen(dataSources[source]['url'])
    rrdfd = open(rrdfile, 'w')
    rrdfd.seek(0)
    rrdfd.write(rrdurlfd.read())
    rrdfd.close()
    rrdfiles.append(rrdfile)

# Build our graph command
graphcmd=[]
graphcmd.append('--title "%s"' % dataSources[datasource[0]]['title'])
graphcmd.append('--lower-limit=0')
graphcmd.append('--start=%s' % startTime)
graphcmd.append('--end=%s' % endTime)
graphcmd.append('--imgformat PNG')
graphcmd.append('--height %s' % graphHeight)
graphcmd.append('--width %s' % graphWidth)
for localfile, ds in zip(rrdfiles, datasource):
    graphcmd.append('DEF:%(ds)s=%(rrdfile)s:%(ds)s:AVERAGE' % \
      {'ds': ds, 'rrdfile': localfile})
for a in area:
    graphcmd.append('AREA:%(ds)s#4568E4:%(ds)s' % {'ds': a})
    graphcmd.append('GPRINT:%(ds)s:LAST:" Current\\: %%lf"' % {'ds': a})
    graphcmd.append('GPRINT:%(ds)s:AVERAGE:" Average\\: %%lf"' % {'ds': a})
    graphcmd.append('GPRINT:%(ds)s:MAX:" Max\\: %%lf\\n"' % {'ds': a})
for l in line:
    graphcmd.append('LINE:%(ds)s#000000:%(ds)s' % {'ds': l})
    graphcmd.append('GPRINT:%(ds)s:LAST:" Current\\: %%lf"' % {'ds': l})
    graphcmd.append('GPRINT:%(ds)s:AVERAGE:" Average\\: %%lf"' % {'ds': l})
    graphcmd.append('GPRINT:%(ds)s:MAX:" Max\\: %%lf\\n"' % {'ds': l})
graphcmds=' '.join(graphcmd)

# Do something with the RRD
fd, graphfile=tempfile.mkstemp()
os.system('rrdtool graph %s %s > /dev/null' % (graphfile, graphcmds))

# Send the user the generated graph
print 'Content-Type: image/png\n'
graphfd=open(graphfile)
print graphfd.read()

# Cleanup
os.remove(rrdfile)
os.remove(graphfile)
