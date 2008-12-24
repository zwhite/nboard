#!/usr/bin/python
"""Displays the status for a host."""

import cgi, cgitb, os, sys, urllib
import nagios
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

form = cgi.FieldStorage()

# Parse the CGI vars
host = form.getvalue('host')
hoststatus = nagios.hoststatus[host]
if 'REMOTE_USER' in os.environ:
    user = os.environ['REMOTE_USER']
else:
    user = 'guest'

# Setup the page
bodytext = []
bodytext.append('  <h1>Status for <a href="?host=%s">%s</a></h1>' % (host,host))
if 'comment' in hoststatus:
    for comment in hoststatus['comment']:
        if comment['comment_data'] != '':
            bodytext.append('<h3>%s: %s (%s)</h3>' % (comment['author'].split()[0], comment['comment_data'], comment['source']))

# Print the comment entry field, when appropriate
if nagios.permUserWrite(user):
    # Use display:none here because otherwise certain browsers (webkit)
    # will require two clicks to show.
    bodytext.append('  <div style="display: none;" id="commentEntryBox">')
    bodytext.append('   <form id="commentEntryForm" action="action.cgi">')
    bodytext.append('    <input type="hidden" name="rm" id="rm" value="silence" />')
    bodytext.append('    <input type="hidden" name="commentEntryHost" id="commentEntryHost" value="%s" />')
    bodytext.append('    <input type="hidden" name="commentEntryService" id="commentEntryService" value="%s" />')
    bodytext.append('    <h5 id="commentEntryReason">Reason for silencing </h5>')
    bodytext.append('    <input type="text" name="commentEntryText" id="commentEntryText" />')
    bodytext.append('    <input type="submit" />')
    bodytext.append('   </form>')
    bodytext.append('  </div>')

# Print the Host's status
bodytext.append('  <table>')
bodytext.append('   <tr>')
bodytext.append('    <th>Service</th>')
bodytext.append('    <th>Status</th>')
bodytext.append('    <th>Last OK</th>')
bodytext.append('    <th>Status Information</th>')
if nagios.permUserWrite(user):
    bodytext.append('    <th>')
    bodytext.append('     <img class="icon" onclick="sendMessage(\'%s\', \'host\');" src="images/comment.gif" title="Send Message About %s" />' % (host, host))
    if hoststatus['notifications_enabled'] == '0':
        bodytext.append('     <img class="icon" onclick="enableAlerts(\'%s\', \'all alerts\');" src="images/ndisabled.gif" title="Enable Notifications for %s" />' % (host, host))
    else:
        bodytext.append('     <img class="icon" onclick="disableAlerts(\'%s\', \'all alerts\');" src="images/notify.gif" title="Disable Notifications for %s" />' % (host, host))
    bodytext.append('    </th>')
bodytext.append('   </tr>')
for service in hoststatus['services']:
    service = hoststatus['services'][service]
    description = service['service_description']

    sendMessage = '<img class="icon" onclick="sendMessage(\'%s\', \'%s\');" src="images/comment.gif" title="Send Message About %s on %s" />' % (host, description, host, description)
    if service['notifications_enabled'] == '0':
        notifications = '<img class="icon" onclick="enableAlerts(\'%s\', \'%s\');" src="images/ndisabled.gif" title="Enable Notifications on %s for %s" />' % (host, description, host, description)
    else:
            notifications = '<img class="icon" onclick="disableAlerts(\'%s\', \'%s\');" src="images/notify.gif" title="Disable notifications on %s for %s" />' % (host, description, host, description)
    if service['current_state'] == '0':
        currentState = ('statusGood', 'OK')
    elif service['current_state'] == '1':
        currentState = ('statusWarn', 'WARNING')
    elif service['current_state'] == '2':
        currentState = ('statusCrit', 'CRITICAL')
    lastTimeOK = nagios.relativeTime(int(service['last_time_ok']))
    pluginOutput = nagios.pluginOutput(description,service['plugin_output'])
    if 'comment' in service:
        for comment in service['comment']:
            if comment['comment_data'] != '':
                pluginOutput = '<h4>%s: %s</h4>%s (%s, %s)' % (comment['author'].split()[0], comment['comment_data'], pluginOutput, comment['type'], comment['source'])

    bodytext.append('   <tr>')
    bodytext.append('    <td><a href="?host=%s&service=%s">%s</a></td>' % (hoststatus['host_name'], urllib.quote(service['service_description']), description))
    bodytext.append('    <td class="%s narrow">%s</td>' % currentState)
    bodytext.append('    <td class="timestamp"><p>%s</p></td>' % lastTimeOK)
    bodytext.append('    <td><p>%s</p></td>' % pluginOutput)
    if nagios.permUserWrite(user):
        bodytext.append('    <td>')
        bodytext.append('     ' + sendMessage)
        bodytext.append('     ' + notifications)
        bodytext.append('    </td>')
    bodytext.append('   </tr>')
bodytext.append('  </table>')

# Print the graph(s) associated with what the user clicked on
if nagios.showHostGraphs:
    printDefaultGraphs=True
    if 'service' in form:
        service=form.getvalue('service')
        if service == 'HTTP':
            printDefaultGraphs=False
            bodytext.append('  <img src="hostrrd.cgi?host=%s&graph=apachestats&width=600&height=200" />' % (hoststatus['host_name']))
        elif service == 'Load' or service == 'DB Load':
            printDefaultGraphs=False
            bodytext.append('  <img src="hostrrd.cgi?host=%s&graph=load&width=600&height=200" />' % (hoststatus['host_name']))
    if printDefaultGraphs:
        bodytext.append('  <img src="hostrrd.cgi?host=%s&graph=load&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  <img src="hostrrd.cgi?host=%s&graph=cpu&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  <img src="hostrrd.cgi?host=%s&graph=mem&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  <img src="hostrrd.cgi?host=%s&graph=process&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))

# Render the page and send it to the user
print HTML % {'refresh': 300, 'body': '\n'.join(bodytext)}