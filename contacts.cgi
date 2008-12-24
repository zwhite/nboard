#!/usr/bin/python
"""Displays the status for all contacts."""

import time
import nagios

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

bodytext = []
bodytext.append('  <h2>Contacts</h2>')
bodytext.append('  <table>')
bodytext.append('   <tr>')
bodytext.append('    <th />')
bodytext.append('    <th>Name</th>')
bodytext.append('    <th>Mobile</th>')
bodytext.append('    <th>Email</th>')
bodytext.append('    <th>Address1</th>')
bodytext.append('    <th>Last Notification</th>')
bodytext.append('   </tr>')
contactlist = nagios.contacts.keys()
contactlist.sort()
for contact in contactlist:
    contact = nagios.contacts[contact]
    if 'pager' in contact:
        pager = contact['pager']
    else:
        pager = ''
    if 'email' in contact:
        email = contact['email']
    else:
        email = ''
    if 'address1' in contact:
        address1 = contact['address1']
    else:
        address1 = ''
    if contact['status']['host_notifications_enabled'] == '0' or \
       contact['status']['service_notifications_enabled'] == '0':
        notify = '<img src="images/ndisabled.gif" />'
    else:
        notify = '<img src="images/notify.gif" />'
    lasthostnotify = int(contact['status']['last_host_notification'])
    lastservicenotify = int(contact['status']['last_service_notification'])
    if lasthostnotify > lastservicenotify:
        lastnotification = time.ctime(lasthostnotify)
    else:
        lastnotification = time.ctime(lastservicenotify)
    bodytext.append('   <tr>')
    bodytext.append('    <td><p>%s</p></td>' % notify)
    bodytext.append('    <td><p>%s</p></td>' % contact['alias'])
    bodytext.append('    <td><p>%s</p></td>' % pager)
    bodytext.append('    <td><p>%s</p></td>' % email)
    bodytext.append('    <td><p>%s</p></td>' % address1)
    bodytext.append('    <td><p>%s</p></td>' % lastnotification)
    bodytext.append('   </tr>')
bodytext.append('  </table>')

print HTML % {'refresh': 300, 'body': '\n'.join(bodytext)}
