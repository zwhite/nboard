#!/usr/bin/python
"""Display an interface suitable for browsing on an iPhone."""

import re
import nagios

print 'Content-Type: application/xhtml+xml\n'

# Variables
HTML = open('templates/iphone.html').read()
bodytext = []

# Generate the main overview page.
bodytext.append('<ul id="groupList" title="Overview" selected="true">')
for group in nagios.grouporder:
    groupid = re.sub('[^a-zA-Z0-9]', '_', group)
    bodytext.append(' <li>')
    status, notifications = nagios.groupStatus(group)
    if status > 1 and not notifications:
        sclass = nagios.statuses[1]
    else:
        sclass = nagios.statuses[status]
    bodytext.append('  <a class="%s" href="#group_%s">' % (sclass, groupid))
    s_ok = 0
    s_warn = 0
    s_crit = 0
    for host in nagios.hostgroups[group]['members']:
        if nagios.hoststatus[host]['current_state'] == '0':
            s_ok += 1
        elif nagios.hoststatus[host]['current_state'] == '1':
            s_warn += 1
        elif nagios.hoststatus[host]['current_state'] == '2':
            s_crit += 1
        for service in nagios.hoststatus[host]['services']:
            service = nagios.hoststatus[host]['services'][service]
            if service['current_state'] == '0':
                s_ok += 1
            elif service['current_state'] == '1':
                s_warn += 1
            elif service['current_state'] == '2':
                if service['notifications_enabled'] == '0':
                    s_warn += 1
                else:
                    s_crit += 1
    bodytext.append('   %s (OK:%s W:%s C:%s)' % (group, s_ok, s_warn, s_crit))
    bodytext.append('  </a>')
    bodytext.append(' </li>')
bodytext.append('</ul>')

# Generate the group overview pages.
for group in nagios.grouporder:
    groupid = re.sub('[^a-zA-Z0-9]', '_', group)
    bodytext.append('<ul id="group_%s" title="%s">' % (groupid, group.title()))
    for host in nagios.hostgroups[group]['members']:
        hostid = re.sub('[^a-zA-Z0-9]', '_', host)
        bodytext.append(' <li>')
        status, notifications = nagios.hostStatus(host)
        if status > 1 and not notifications:
            sclass = nagios.statuses[1]
        else:
            sclass = nagios.statuses[status]
        bodytext.append('  <a class="%s" href="#host_%s">' % (sclass, hostid))
        bodytext.append('   %s' % host)
        bodytext.append('  </a>')
        bodytext.append(' </li>')
    bodytext.append('</ul>')

# Genereate the host pages.
for host in nagios.hoststatus:
    hostid = re.sub('[^a-zA-Z0-9]', '_', host)
    bodytext.append('<ul id="host_%s" title="%s">' % (hostid, host.title()))
    for service in nagios.hoststatus[host]['services']:
        serviceid = re.sub('[^a-zA-Z0-9]', '_', service)
        service = nagios.hoststatus[host]['services'][service]
        bodytext.append(' <li class="%s">' % status)
        status = nagios.statuses[int(service['current_state'])]
        bodytext.append('  %s' % service['service_description'])
        bodytext.append(' </li>')
    bodytext.append('</ul>')

# Return the generated page
print HTML % {'refresh': 20, 'title': 'Network Dashboard', 'body': '\n'.join(bodytext)}
