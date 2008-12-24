#!/usr/bin/python
"""Displays the status for a host."""

import cgi, cgitb, sys, time, urllib
import nagios
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

form = cgi.FieldStorage()
bodytext = []

# Parse the CGI vars
group = form.getvalue('group')
if not group:
    group = 'database'
bodytext.append('  <h2>Status for %s Servers</h2>' % group.title())
bodytext.append('  <table>')
bodytext.append('   <tr>')
bodytext.append('    <th>Host</th>')
bodytext.append('    <th>Host Status</th>')
bodytext.append('    <th colspan="10">Service Detail</th>')
bodytext.append('   </tr>')
hostlist = nagios.hoststatus.keys()
hostlist.sort()
for host in hostlist:
    if host not in nagios.hostlist[group]: continue
    hosttext = host
    hoststatus = nagios.hoststatus[host]
    if hoststatus['notifications_enabled'] == '0':
        hosttext = host + ' <img src="images/ndisabled.gif" />'
    if hoststatus['current_state'] == '0':
        currentState = ('statusGood', 'OK')
    elif hoststatus['current_state'] == '1':
        currentState = ('statusWarn', 'WARNING')
    elif hoststatus['current_state'] == '2':
        currentState = ('statusCrit', 'CRITICAL')
    bodytext.append('   <tr>')
    bodytext.append('    <td><a href="hoststatus.cgi?host=%s">%s</a></td>' \
     % (host, hosttext))
    bodytext.append('    <td class="%s narrow">%s</td>' % currentState)
    for service in hoststatus['services']:
        service = hoststatus['services'][service]
        if service['notifications_enabled'] == '0':
            notifications = ' <img src="images/ndisabled.gif" />'
        else:
            notifications = ''
        description = '%s%s' % (service['service_description'], notifications)
        if service['current_state'] == '0':
            currentState = ('statusGood')
        elif service['current_state'] == '1':
            currentState = ('statusWarn')
        elif service['current_state'] == '2':
            currentState = ('statusCrit')
        bodytext.append('       <td class="%s">' % currentState)
        bodytext.append('        <a href="hoststatus.cgi?host=%s&service=%s">' \
         % (host, urllib.quote(service['service_description'])))
        bodytext.append('         ' + description)
        bodytext.append('        </a>')
        bodytext.append('       </td>')
    bodytext.append('   </tr>')
bodytext.append('  </table>')

print HTML % {'refresh': 60, 'body': '\n'.join(bodytext)}
