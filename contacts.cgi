#!/usr/bin/python
"""Displays the status for all contacts."""

import time
import html, nagios

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

bodytext = []
bodytext.append('  <h2>Contacts</h2>')
bodytext.append('  <table>')
bodytext.append('   <tr>')
bodytext.append('    <th>Name</th>')
bodytext.append('    <th>Mobile</th>')
bodytext.append('    <th>Email</th>')
bodytext.append('    <th>Address1</th>')
bodytext.append('    <th>Last Notification</th>')
if nagios.programstatus['enable_notifications'] == '0':
    bodytext.append('    <th>%s</th>' % html.iconNotify('global', None, 'Enable ALL Notifications', False))
else:
    bodytext.append('    <th>%s</th>' % html.iconNotify('global', None, 'Disable ALL Notifications', True))
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
        notify = html.iconNotify('contact', contact['contact_name'], 'Enable Notifications', False)
    else:
        notify = html.iconNotify('contact', contact['contact_name'], 'Disable Notifications', True)
    lasthostnotify = int(contact['status']['last_host_notification'])
    lastservicenotify = int(contact['status']['last_service_notification'])
    if lasthostnotify > lastservicenotify:
        lastnotification = nagios.relativeTime(lasthostnotify)
    else:
        lastnotification = nagios.relativeTime(lastservicenotify)
    bodytext.append('   <tr>')
    bodytext.append('    <td><p>%s</p></td>' % contact['alias'])
    bodytext.append('    <td><p>%s</p></td>' % pager)
    bodytext.append('    <td><p>%s</p></td>' % email)
    bodytext.append('    <td><p>%s</p></td>' % address1)
    bodytext.append('    <td><p>%s</p></td>' % lastnotification)
    bodytext.append('    <td><p>%s</p></td>' % notify)
    bodytext.append('   </tr>')
bodytext.append('  </table>')

print HTML % {'refresh': 300, 'body': '\n'.join(bodytext)}
