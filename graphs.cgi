#!/usr/bin/env python

import cgi, cgitb, ConfigParser
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()
bodytext = []

# Pull in our configuration
config = ConfigParser.SafeConfigParser()
config.read('conf/datasources.ini')
dataSources = {}
for section in config.sections():
    dataSources[section] = {}
    for option, value in config.items(section):
        dataSources[section][option] = value

# Generate the list of graphs
graphs = dataSources.keys()
graphs.sort()
for graph in graphs:
    #if dataSources[graph]['display'].lower() == 'false':
    #    continue
    graphuri = 'rrdpage.cgi?type=datasource&datasource=%s' % graph
    graphimg = 'rrdimg.cgi?width=300&height=100&datasource=%s' % graph
    bodytext.append('  <div class="graphDiv">')
    bodytext.append('  <h2>%s</h2>' % dataSources[graph]['title'])
    bodytext.append('  <a href="%s"><img src="%s" /></a>' % (graphuri,graphimg))
    bodytext.append('  </div>')

print HTML % {'refresh': 60, 'body': '\n'.join(bodytext)}
