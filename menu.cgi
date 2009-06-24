#!/usr/bin/python
"""Displays the side menu of our status page."""

import cgi, cgitb, glob, os.path, sys
import nagios
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

# Parse our parameters
form = cgi.FieldStorage()
group = form.getfirst('group')
if not group:
    group = nagios.defaultGroup

# Setup the page
bodytext = []
bodytext.append('<div id="menu_wrapper">')
bodytext.append('<img src="images/nboard.gif" />')

# Show the Nagios menu items
bodytext.append('<h3>Menu</h3>')
bodytext.append('<ul id="menu" class="menu">')
bodytext.append(' <li class="contacts">')
bodytext.append('  <a href="contacts.cgi" target="main_f">Contacts</a>')
bodytext.append(' </li>')
bodytext.append(' <li class="disabledalerts">')
bodytext.append('  <a href="disabledalerts.cgi" target="main_f">Disabled</a>')
bodytext.append(' </li>')
if nagios.showGraphs:
    bodytext.append(' <li class="graphs">')
    bodytext.append('  <a href="graphs.cgi" target="main_f">Graphs</a>')
    bodytext.append(' </li>')
bodytext.append(' <li class="problems">')
bodytext.append('  <a href="problems.cgi" target="main_f">Problems</a>')
bodytext.append(' </li>')
bodytext.append(' <li class="iphone">')
bodytext.append('  <a href="iphone.cgi" target="_blank">iPhone</a>')
bodytext.append(' </li>')
bodytext.append('</ul>')

# Display the items in extras/
bodytext.append('<h3>Extras</h3>')
bodytext.append('<ul id="extras" class="menu">')
extraList = glob.glob('extras/*')
extraList.sort()
for extra in extraList:
    ext = extra.split('.')[-1]
    if ext not in ['cgi', 'htm', 'html', 'php', 'pl']:
        continue
    extraFile=os.path.basename(extra)
    extraName='.'.join(extraFile.split('.')[:-1])
    extraTitle=extraName.title().replace('_', ' ')
    bodytext.append(' <li class="%s">' % extraName)
    bodytext.append('  <a href="extras/%s" target="main_f">%s</a>' % \
        (extraFile, extraTitle))
    bodytext.append(' </li>')

# Show the hosts in this current group
groupstatus, notifications = nagios.groupStatus(group)
if groupstatus > 0 and not notifications:
    statusClass = nagios.statuses[1]
else:
    statusClass = nagios.statuses[groupstatus]
bodytext.append('\n <h2 class="%s list">' % statusClass)
bodytext.append('  <a target="main_f" href="groupoverview.cgi?group=%s">' % group)
icon = nagios.getGroupIcon(group)
bodytext.append('    <img src="%s" />' % icon)
bodytext.append('   ' + group.title())
bodytext.append('  </a>')
bodytext.append(' </h2>')
hostlist = nagios.hoststatus.keys()
hostlist.sort()
for host in hostlist:
    if nagios.inGroup(host, group):
        current_status = int(nagios.hoststatus[host]['current_state'])
	if current_status > 2: current_status=2
        for service in nagios.hoststatus[host]['services']:
            service = nagios.hoststatus[host]['services'][service]
            service_status=int(service['current_state'])
	    if service_status > 2: service_status=2
            if service_status > current_status:
                current_status = service_status
        bodytext.append('  <a class="%s list" target="main_f" href="hoststatus.cgi?host=%s"><img src="%s" /> %s</a>' % (nagios.statuses[current_status], host, nagios.getHostIcon(host), host))

bodytext.append('</div>')

print HTML % {'refresh': 60, 'body': '\n'.join(bodytext)}
