#!/usr/bin/python
"""Displays all alerts that have been disabled."""

import cgi, cgitb, sys, time, urllib
import nagios
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

form = cgi.FieldStorage()
bodytext = []
hosts = {}

# Parse the CGI vars
bodytext.append('  <h2>Disabled Alerts</h2>')
bodytext.append('  <table>')
bodytext.append('   <tr>')
bodytext.append('    <th>Host</th>')
bodytext.append('    <th colspan="20">Services</th>')
bodytext.append('   </tr>')
hostlist = nagios.hoststatus.keys()
hostlist.sort()
for host in hostlist:
    bodytext.append('<!-- %s -->' % host)
    hoststatus = nagios.hoststatus[host]
    if hoststatus['notifications_enabled'] == '0':
        hosts[host] = True
    for service in hoststatus['services']:
        service = hoststatus['services'][service]
        if service['notifications_enabled'] != '0':
            continue
	if host not in hosts:
            hosts[host] = [False, [service['service_description']]]
        elif hosts[host] is True:
            hosts[host] = [True, [service['service_description']]]
        else:
            hosts[host][1].append(service['service_description'])

rowcount = 0
for host in hosts:
    rowcount += 1
    if rowcount % 2 == 0:
        bodytext.append('   <tr class="even">')
    else:
        bodytext.append('   <tr class="odd">')
    bodytext.append('    <td class="host nowrap">')
    uri = 'hoststatus.cgi?host=%s' % host
    bodytext.append('     <a href="%s"><img src="%s" />%s</a>' % \
     (uri, nagios.getHostIcon(host), host))
    hoststatus = nagios.hoststatus[host]
    if 'comment' in hoststatus:
        for comment in hoststatus['comment']:
            bodytext.append('    <br />')
            bodytext.append('<b>%s: %s (%s)</b>' % (comment['author'].split()[0], comment['comment_data'], comment['source']))
    bodytext.append('    </td>')
    if hosts[host] is True:
        bodytext.append('       <td />')
    else:
        for service in hosts[host][1]:
            service = hoststatus['services'][service]
            bodytext.append('       <td>')
            uri = 'hoststatus.cgi?host=%s&service=%s' % (host, 
                                                         urllib.quote(service['service_description']))
            bodytext.append('        <a href="%s">' % uri)
            bodytext.append('         ' + service['service_description'])
            bodytext.append('        </a>')
            if 'comment' in service:
                for comment in service['comment']:
                    if comment['comment_data'] != '':
                        bodytext.append('        <br />')
                        bodytext.append('        <b>%s: %s</b>' % \
                         (comment['author'].split()[0], comment['comment_data']))
            bodytext.append('       </td>')
    bodytext.append('   </tr>')
bodytext.append('  </table>')

print HTML % {'refresh': 60, 'body': '\n'.join(bodytext)}
