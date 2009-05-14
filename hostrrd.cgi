#!/usr/bin/env python

import cgi, cgitb, os, subprocess, sys, tempfile, time, urllib
import nagios
cgitb.enable(logdir="/tmp")

# Variables
graphLegend=True

# Parse our CGI vars
form = cgi.FieldStorage()
if 'host' in form:
    host = form.getfirst('host')
else:
    print 'You must supply a host!'
    sys.exit()
if 'graph' in form:
    graph = form.getfirst('graph')
    graphNum, graphName = graph.split('_', 1)
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
tmpdir=tempfile.mkdtemp()
url = nagios.hostGraphBaseUrl+'%s/%s.rrd'
url = url % (nagios.hosts[host]['address'], graph, graphName)
rrdurlfd=urllib.urlopen(url)
rrdfile=tmpdir+'/%s.rrd' % graphName
rrdfd = open(rrdfile, 'w')
rrdfd.write(rrdurlfd.read())
rrdfd.close()
rrdurlfd.close()

# Build our graph command
graphurl = nagios.hostGraphBaseUrl+'%s/graph.pm'
graphurl = graphurl % (nagios.hosts[host]['address'], graph)
graphfd=urllib.urlopen(graphurl)
graphpm = open(tmpdir+'/graph.pm', 'w')
graphpm.write(graphfd.read())
graphpm.close()
graphfd.close()
perlargs = """-I%s -Mgraph -e"print \$GRAPH_CMDS{'%s'};\""""
perlargs = perlargs % (tmpdir, graphName)
os.system("perl %s > %s/output" % (perlargs, tmpdir))
graphcmd = open('%s/output' % tmpdir).read()

# Masasge the graph command into something usable
graphcmd = graphcmd.replace('\n', ' ')
graphcmd = graphcmd.replace('{#server#}', host)
graphcmd = graphcmd.replace('{#path#}', tmpdir+'/')
for color in ['linecolor', 'color1', 'color2', 'color3', 'color4', 'color5', 'dcolor1', 'dcolor2', 'dcolor3']:
    graphcmd = graphcmd.replace('{#%s#}' % color, nagios.graphs[color])
graphcmd = '--start %s --end %s %s' % (startTime, endTime, graphcmd)

# Do something with the RRD
fd, graphfile=tempfile.mkstemp()
os.system("echo 'rrdtool graph %s %s' > /tmp/rrdoutput" % (graphfile, graphcmd))
os.system("echo 'Source: %s' >> /tmp/rrdoutput" % (url))
os.system("echo 'Graph Command: %s' >> /tmp/rrdoutput" % (graphcmd))
os.system("rrdtool graph %s %s >> /tmp/rrdoutput" % (graphfile, graphcmd))

# Send the user the generated graph
print 'Content-Type: image/png\n'
graphfd=open(graphfile)
print graphfd.read()

# Cleanup
os.remove(rrdfile)
os.remove(graphfile)
