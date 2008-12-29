#!/usr/bin/python
"""Displays the top menu of our status page."""

import nagios

#print 'Content-Type: application/xhtml+xml\n'
print 'Content-Type: text/html\n'

# Variables
HTML = open('templates/basic.html').read()
status = nagios.allGroupStatus()

# Generate the page
bodytext = []
grouplist = nagios.grouplist.keys()
grouplist.sort()
for group in grouplist:
    group = nagios.grouplist[group]
    groupstatus, notifications = status[group]
    if groupstatus > 0 and not notifications:
        bodytext.append('  <div class="%s">' % nagios.statuses[1])
    else:
        bodytext.append('  <div class="%s">' % nagios.statuses[groupstatus])
    bodytext.append('   <a target="menu_f" onclick="top.main_f.location=\'groupoverview.cgi?group=%s\';" style="font-size: +2;" href="menu.cgi?group=%s">' % (group, group))
    bodytext.append('    <img src="%s" />' % nagios.icons[group])
    bodytext.append('    ' + group)
    bodytext.append('   </a>')
    bodytext.append('  </div>')

# Return the generated page
print HTML % {'refresh': 20, 'body': '\n'.join(bodytext)}
