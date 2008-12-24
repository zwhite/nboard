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
status = nagios.allGroupStatus()
statuses = ['statusGood', 'statusWarn', 'statusCrit']

# Generate the page
bodytext = []
grouplist = nagios.grouplist.keys()
grouplist.sort()
for group in grouplist:
    group = nagios.grouplist[group]
    bodytext.append('  <div class="%s"><a target="menu_f" onclick="top.main_f.location=\'groupoverview.cgi?group=%s\';" style="font-size: +2;" href="menu.cgi?group=%s"><img class="%s" src="%s" /> %s</a></div>' % (statuses[status[group]], group, group, statuses[status[group]], nagios.icons[group], group))

# Return the generated page
print HTML % {'refresh': 20, 'body': '\n'.join(bodytext)}
