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
bodytext.append('<div id="topmenu_wrapper">')
bodytext.append('<ul id="topmenu">')
for group in nagios.grouporder:
    groupstatus, notifications = status[group]
    if groupstatus > 0 and not notifications:
        bodytext.append('  <li class="%s %s">' % (nagios.statuses[1], group))
    else:
        bodytext.append('  <li class="%s %s">' % (nagios.statuses[groupstatus],
                                                  group))
    bodytext.append('   <a target="menu_f" onclick="top.main_f.location=\'groupoverview.cgi?group=%s\';" style="font-size: 110%%;" href="menu.cgi?group=%s">' % (group, group))
    bodytext.append('    ' + group.title())
    bodytext.append('   </a>')
    bodytext.append('  </li>')
bodytext.append('</ul>')
bodytext.append('</div>')

# Return the generated page
print HTML % {'refresh': 20, 'body': '\n'.join(bodytext)}
