#!/usr/bin/python
"""Displays the top menu of our status page."""

import nagios

#print 'Content-Type: application/xhtml+xml\n'
print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

# Status for this group. Known values:
# 0 - A-OK
# 1 - Warning
# 2 - Critical
status = {}
for group in nagios.hostlist:
    status[group] = 0
statuses = ['statusGood', 'statusWarn', 'statusCrit']

for host in nagios.hoststatus:
    if nagios.hoststatus[host]['current_state'] == "1":
        for group in status:
            if host in nagios.hostlist[group]:
                if status[group] < 2: status[group] = 2
    else:
        # Check the services
        for service in nagios.hoststatus[host]['services']:
            service = nagios.hoststatus[host]['services'][service]
            if host in nagios.hostlist['critical']:
                if service['notifications_enabled'] == "0" \
                 or service['problem_has_been_acknowledged'] == "1":
                    # Don't count this against the critical
                    continue
            if service['current_state'] == "2":
                for type in status:
                    if host in nagios.hostlist[type]:
                        if service['notifications_enabled'] == "0" \
                         or service['problem_has_been_acknowledged'] == "1":
                            if status[type] < 1: status[type] = 1
			else:
                            if status[type] < 2: status[type] = 2
            elif service['current_state'] == "1":
                for type in status:
                    if host in nagios.hostlist[type]:
                        if status[type] < 1: status[type] = 1

# Generate the page
bodytext = []
grouplist = nagios.grouplist.keys()
grouplist.sort()
for group in grouplist:
    group = nagios.grouplist[group]
    bodytext.append('  <div class="%s"><a target="menu_f" onclick="top.main_f.location=\'groupoverview.cgi?group=%s\';" style="font-size: +2;" href="menu.cgi?group=%s"><img class="%s" src="%s" /> %s</a></div>' % (statuses[status[group]], group, group, statuses[status[group]], nagios.icons[group], group))

# Return the generated page
print HTML % {'refresh': 20, 'body': '\n'.join(bodytext)}
