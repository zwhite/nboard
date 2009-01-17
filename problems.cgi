#!/usr/bin/env python
"""Show us what's going wrong right now."""

import os, sys, time, urllib
import nagios

print 'Content-Type: text/html\n'
bodytext = []
HTML = open('templates/basic.html').read()

# Check some important settings
if nagios.programstatus['active_host_checks_enabled'] == '0':
    bodytext.append('<h1>WARNING: Active host checks are disabled!</h1>')
if nagios.programstatus['active_service_checks_enabled'] == '0':
    bodytext.append('<h1>WARNING: Active service checks are disabled!</h1>')
if nagios.programstatus['enable_notifications'] == '0':
    bodytext.append('<h1>WARNING: All notifications are disabled!</h1>')

bodytext.append('<h1>Current Known Problems</h1>')
bodytext.append('<table>')
bodytext.append('<tr>')
bodytext.append('<th>Host</th>')
bodytext.append('<th colspan="20">Problems</th>')
bodytext.append('</tr>')
hostproblems=[]
hostlist = nagios.hoststatus.keys()
hostlist.sort()
for host in hostlist:
    hostproblem=[]
    if nagios.hoststatus[host]['current_state'] == "1":
        # Host is Down
        if nagios.hoststatus[host]['notifications_enabled'] == '0':
            notify = ''
        else:
            notify = '<img src="images/notify.gif" />'
        hostproblem.append('<td class="statusCrit">HOST DOWN! %s</td>' % notify)
    else:
        for service in nagios.hoststatus[host]['services']:
            service = nagios.hoststatus[host]['services'][service]
            if service['current_state'] == '0':
                currentState = 'statusGood'
            elif service['current_state'] == '1':
                currentState = 'statusWarn'
            else:
                currentState = 'statusCrit'
            if service['current_state'] in ('1', '2', '3'):
                if service['notifications_enabled'] == '0':
                    notify = ''
                else:
                    notify = '<img src="images/notify.gif" />'
                hostproblem.append('<td class="%s"><a href="hoststatus.cgi?host=%s&service=%s">%s%s</a><hr />%s</td>' % (currentState, host, urllib.quote(service['service_description']), service['service_description'], notify, nagios.pluginOutput(service['service_description'], service['plugin_output'])))
    if hostproblem != []:
        hostproblems.append('<tr><td><a href="hoststatus.cgi?host=%s">%s</a></td>%s</tr>' % (host, host, ''.join(hostproblem)))
bodytext.append('\n'.join(hostproblems))

print HTML % {'refresh': 60, 'body': '\n'.join(bodytext)}
