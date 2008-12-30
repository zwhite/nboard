#!/usr/bin/python
"""Displays the side menu of our status page."""

import cgi, cgitb, glob, os.path, sys
import nagios
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

form = cgi.FieldStorage()

group = form.getfirst('group')
if not group:
    group = nagios.defaultGroup
bodytext = []

# Display the items in extras/
extraList = glob.glob('extras/*')
extraList.sort()
for extra in extraList:
    ext = extra.split('.')[-1]
    if ext not in ['cgi', 'htm', 'html', 'php', 'pl']:
        continue
    extraFile=os.path.basename(extra)
    extraTitle='.'.join(extraFile.split('.')[:-1]).title()
    bodytext.append(' <h2><a href="extras/%s" target="main_f">%s</a></h2>' \
      % (extraFile, extraTitle))

# Show the Nagios menu items
bodytext.append('\n <hr />')
bodytext.append(' <h2><a href="contacts.cgi" target="main_f">Contacts</a></h2>')
bodytext.append(' <h2><a href="iphone.cgi" target="_blank">iPhone</a></h2>')

# Show the hosts in this current group
bodytext.append('\n <hr />')
groupstatus, notifications = nagios.groupStatus(group)
if groupstatus > 0 and not notifications:
    statusClass = nagios.statuses[1]
else:
    statusClass = nagios.statuses[groupstatus]
bodytext.append('\n <h2 class="%s">' % statusClass)
bodytext.append('  <a target="main_f" href="groupoverview.cgi?group=%s">' % group)
icon = nagios.icons[group]
bodytext.append('    <img src="%s" />' % icon)
bodytext.append('   ' + group.title())
bodytext.append('  </a>')
bodytext.append(' </h2>')
hostlist = nagios.hoststatus.keys()
hostlist.sort()
for host in hostlist:
    if nagios.hoststatus[host]['host_name'] in nagios.hostlist[group]:
        current_status = int(nagios.hoststatus[host]['current_state'])
        for service in nagios.hoststatus[host]['services']:
            service = nagios.hoststatus[host]['services'][service]
            service_status=int(service['current_state'])
            if service_status > current_status:
                current_status = service_status
        bodytext.append('  <a class="%s list" target="main_f" href="hoststatus.cgi?host=%s"><img src="%s" /> %s</a>' % (nagios.statuses[current_status], host, nagios.icons[group], host))

print HTML % {'refresh': 60, 'body': '\n'.join(bodytext)}
