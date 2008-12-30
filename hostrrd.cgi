#!/usr/bin/env python

import cgi, cgitb, os, sys, tempfile, time, urllib
import nagios
cgitb.enable(logdir="/tmp")

# Variables
graphLegend=True
# FIXME: Put this into an ini, which will require reworking the code that 
#        builds the rrdtool command below.
graphs = {
    'load': '01_load',
    'cpu': '02_cpu',
    'mem': '03_mem',
    'process': '04_process',
    'space': '07_space',
    'apachestats': '08_apachestats',
}

# Parse our CGI vars
form = cgi.FieldStorage()
if 'host' in form:
    host=form.getfirst('host')
else:
    print 'You must supply a host!'
    sys.exit()
if 'graph' in form:
    graph=form.getfirst('graph')
else:
    print 'You must supply a graph!'
    sys.exit()
if 'height' in form:
    graphHeight=form.getfirst('height')
else:
    graphHeight=200
if 'width' in form:
    graphWidth=form.getfirst('width')
else:
    graphWidth=600
if 'start' in form:
    startTime=int(form.getfirst('start'))
    endTime=startTime + 86400
else:
    endTime=int(time.time())
    startTime=endTime - 86400
if 'end' in form:
    endTime=int(form.getfirst('end'))
startTime_s=time.strftime('%Y-%m-%d %H\:%M\:%S', time.localtime(startTime))
endTime_s=time.strftime('%Y-%m-%d %H\:%M\:%S', time.localtime(endTime))
if 'graphlegend' in form:
    if form.getfirst('graphlegend') == 'false':
        graphLegend=False

# Fetch the remote RRD
# FIXME: Make the URL structure more robust
url = nagios.hostGraphBaseUrl % (host, graphs[graph], graph)
fd, rrdfile=tempfile.mkstemp()
rrdurlfd=urllib.urlopen(url)
rrdfd = open(rrdfile, 'w')
rrdfd.seek(0)
rrdfd.write(rrdurlfd.read())
rrdfd.close()

# Build our graph command
graphcmd=[]
graphcmd.append('--start=%s' % startTime)
graphcmd.append('--end=%s' % endTime)
graphcmd.append('--imgformat PNG')
graphcmd.append('--height %s' % graphHeight)
graphcmd.append('--width %s' % graphWidth)
if graphLegend:
    graphcmd.append('COMMENT:"From %s to %s\\c"' % (startTime_s, endTime_s))
    graphcmd.append('COMMENT:"\\n"')
if graph == 'load':
    graphcmd.append('--lower-limit=0')
    graphcmd.append('--title "%s Load Average"' % host.title())
    graphcmd.append('--vertical-label="Load"')
    graphcmd.append('DEF:load_1mn=%s:load_1mn:AVERAGE' % rrdfile)
    graphcmd.append('DEF:load_5mn=%s:load_5mn:AVERAGE' % rrdfile)
    graphcmd.append('DEF:load_15mn=%s:load_15mn:AVERAGE' % rrdfile)
    graphcmd.append('CDEF:mysum=load_1mn,load_5mn,+,load_15mn,+')
    graphcmd.append('AREA:load_1mn#EACC00:"1mn average "')
    if graphLegend:
        graphcmd.append('GPRINT:load_1mn:LAST:"Current\\: %5.2lf "')
        graphcmd.append('GPRINT:load_1mn:AVERAGE:"Average\\: %5.2lf "')
        graphcmd.append('GPRINT:load_1mn:MAX:"Max\\: %5.2lf\\n"')
    graphcmd.append('STACK:load_5mn#EA8F00:"5mn average "')
    if graphLegend:
        graphcmd.append('GPRINT:load_5mn:LAST:"Current\\: %5.2lf "')
        graphcmd.append('GPRINT:load_5mn:AVERAGE:"Average\\: %5.2lf "')
        graphcmd.append('GPRINT:load_5mn:MAX:"Max\\: %5.2lf\\n"')
    graphcmd.append('STACK:load_15mn#FF0000:"15mn average "')
    if graphLegend:
        graphcmd.append('GPRINT:load_15mn:LAST:"Current\\: %5.2lf "')
        graphcmd.append('GPRINT:load_15mn:AVERAGE:"Average\\: %5.2lf "')
        graphcmd.append('GPRINT:load_15mn:MAX:"Max\\: %5.2lf\\n"')
    graphcmd.append('LINE1:mysum#000000')
if graph == 'cpu':
    graphcmd.append('--title "%s CPU Usage"' % host.title())
    graphcmd.append('--vertical-label="Percent"')
    graphcmd.append('--lower-limit=0')
    graphcmd.append('--upper-limit 100')
    graphcmd.append('DEF:user=%s:user:AVERAGE' % rrdfile)
    graphcmd.append('DEF:system=%s:system:AVERAGE' % rrdfile)
    graphcmd.append('DEF:nice=%s:nice:AVERAGE' % rrdfile)
    graphcmd.append('DEF:idle=%s:idle:AVERAGE' % rrdfile)
    graphcmd.append('CDEF:total=user,system,+,nice,+,idle,+')
    graphcmd.append('CDEF:p_user=user,total,/,100,*')
    graphcmd.append('CDEF:p_system=system,total,/,100,*')
    graphcmd.append('CDEF:p_nice=nice,total,/,100,*')
    graphcmd.append('CDEF:mysum=p_user,p_system,+,p_nice,+')
    graphcmd.append('AREA:p_user#EACC00:"User "')
    if graphLegend:
        graphcmd.append('GPRINT:p_user:LAST:"  Current\\: %5.2lf%% "')
        graphcmd.append('GPRINT:p_user:AVERAGE:"Average\\: %5.2lf%% "')
        graphcmd.append('GPRINT:p_user:MAX:"Max\\: %5.2lf%%\\n"')
    graphcmd.append('STACK:p_system#EA8F00:"System "')
    if graphLegend:
        graphcmd.append('GPRINT:p_system:LAST:"Current\\: %5.2lf%% "')
        graphcmd.append('GPRINT:p_system:AVERAGE:"Average\\: %5.2lf%% "')
        graphcmd.append('GPRINT:p_system:MAX:"Max\\: %5.2lf%%\\n"')
    graphcmd.append('STACK:p_nice#FF0000:"Nice "')
    if graphLegend:
        graphcmd.append('GPRINT:p_nice:LAST:"  Current\\: %5.2lf%% "')
        graphcmd.append('GPRINT:p_nice:AVERAGE:"Average\\: %5.2lf%% "')
        graphcmd.append('GPRINT:p_nice:MAX:"Max\\: %5.2lf%%\\n"')
    graphcmd.append('LINE1:mysum#000000')
if graph == 'mem':
    graphcmd.append('--title "%s Memory"' % host.title())
    graphcmd.append('--vertical-label="Percent"')
    graphcmd.append('--lower-limit 0')
    graphcmd.append('--upper-limit 100')
    graphcmd.append('DEF:mem=%s:mem:AVERAGE' % rrdfile)
    graphcmd.append('DEF:swap=%s:swap:AVERAGE' % rrdfile)
    graphcmd.append('AREA:mem#F51C2F:"Physical "')
    if graphLegend:
        graphcmd.append('GPRINT:mem:LAST:"Current\\: %3.0lf%% "')
        graphcmd.append('GPRINT:mem:AVERAGE:"Average\\: %3.0lf%% "')
        graphcmd.append('GPRINT:mem:MAX:"Maximum\\: %3.0lf%%\\n"')
    graphcmd.append('AREA:swap#002997:"Swap     "')
    if graphLegend:
        graphcmd.append('GPRINT:swap:LAST:"Current\\: %3.0lf%% "')
        graphcmd.append('GPRINT:swap:AVERAGE:"Average\\: %3.0lf%% "')
        graphcmd.append('GPRINT:swap:MAX:"Maximum\\: %3.0lf%%"')
if graph == 'process':
    graphcmd.append('--title "%s Processes"' % host.title())
    graphcmd.append('--vertical-label="Processes"')
    graphcmd.append('--units-exponent 0')
    graphcmd.append('--lower-limit 0')
    graphcmd.append('DEF:all=%s:all:AVERAGE' % rrdfile)
    graphcmd.append('DEF:running=%s:running:AVERAGE' % rrdfile)
    graphcmd.append('AREA:all#F51C2F:"All     "')
    if graphLegend:
        graphcmd.append('GPRINT:all:LAST:"Current\\: %5.0lf "')
        graphcmd.append('GPRINT:all:AVERAGE:"Average\\: %5.0lf "')
        graphcmd.append('GPRINT:all:MAX:"Maximum\\: %5.0lf\\n"')
    graphcmd.append('AREA:running#002997:"Running "')
    if graphLegend:
        graphcmd.append('GPRINT:running:LAST:"Current\\: %5.0lf "')
        graphcmd.append('GPRINT:running:AVERAGE:"Average\\: %5.0lf "')
        graphcmd.append('GPRINT:running:MAX:"Maximum\\: %5.0lf"')
if graph == 'space':
    graphcmd.append('--title "%s Used Space on /"' % host.title())
    graphcmd.append('--vertical-label="Percent"')
    graphcmd.append('--lower-limit 0')
    graphcmd.append('--upper-limit 100')
    graphcmd.append('DEF:space=%s:space:AVERAGE' % rrdfile)
    graphcmd.append('AREA:space#4568E4:"Used Space "')
    if graphLegend:
        graphcmd.append('GPRINT:space:LAST:"Current\\: %3.0lf%% "')
        graphcmd.append('GPRINT:space:AVERAGE:"Average\\: %3.0lf%% "')
        graphcmd.append('GPRINT:space:MAX:"Maximum\\: %3.0lf%%\\n"')
    graphcmd.append('LINE1:space#000000')
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
