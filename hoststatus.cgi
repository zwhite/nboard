#!/usr/bin/python
"""Displays the status for a host."""

import cgi, cgitb, os, sys, urllib
import html, nagios
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'
HTML = open('templates/basic.html').read()
form = cgi.FieldStorage()

# Parse the CGI vars
host = form.getfirst('host')
hoststatus = nagios.hoststatus[host]

# Setup the page
bodytext = []
bodytext.append('  <h1>Status for <a href="?host=%s">%s</a></h1>' % (host,host))
if 'comment' in hoststatus:
    for comment in hoststatus['comment']:
        if comment['comment_data'] != '':
            bodytext.append('<h2>%s: %s (%s)</h2>' % (comment['author'].split()[0], comment['comment_data'], comment['source']))

# Print the comment entry field, when appropriate
if nagios.permUserWrite():
    # Use display:none here because otherwise certain browsers (webkit)
    # will require two clicks to show.
    bodytext.append('  <div style="display: none;" id="commentEntryBox">')
    bodytext.append('   <form id="commentEntryForm" action="action.cgi">')
    bodytext.append('    <input type="hidden" name="rm" id="rm" value="silence" />')
    bodytext.append('    <input type="hidden" name="commentEntryHost" id="commentEntryHost" value="%s" />')
    bodytext.append('    <input type="hidden" name="commentEntryService" id="commentEntryService" value="%s" />')
    bodytext.append('    <h5 id="commentEntryReason">Reason for silencing </h5>')
    bodytext.append('    <p>(Include "sms" in your comment if you want SMS notification.)</p>')
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
if hoststatus['notifications_enabled'] == '0':
    bodytext.append('     <th class="nowrap">%s</th>' % html.iconNotify('service', host, 'all services', False))
else:
    bodytext.append('     <th class="nowrap">%s</th>' % html.iconNotify('service', host, 'all services', True))
bodytext.append('   </tr>')
rownum = 0
for service in hoststatus['services']:
    rownum += 1
    service = hoststatus['services'][service]
    description = service['service_description']

    sendMessage  = '<img class="icon" onclick="sendMessage(\'%s\', \'%s\');"'
    sendMessage += ' src="images/comment.gif"'
    sendMessage += ' title="Send Message About %s on %s" />'
    sendMessage = sendMessage % (host, description, host, description)
    if service['notifications_enabled'] == '0':
        notifications = html.iconNotify('service', host, description, False)
    else:
        notifications = html.iconNotify('service', host, description, True)
    if service['current_state'] == '0':
        currentState = ('statusGood', 'OK')
    elif service['current_state'] == '1':
        currentState = ('statusWarn', 'WARNING')
    else:
        currentState = ('statusCrit', 'CRITICAL')
    lastTimeOK = nagios.relativeTime(int(service['last_time_ok']))
    pluginOutput = nagios.pluginOutput(description,service['plugin_output'])
    if 'comment' in service:
        for comment in service['comment']:
            if comment['comment_data'] != '':
                pluginOutput = '<h4>%s: %s</h4>%s (%s, %s)' % \
                  (comment['author'].split()[0], comment['comment_data'], 
                  pluginOutput, comment['type'], comment['source'])

    if rownum % 2 == 0:
	    bodytext.append('   <tr class="even">')
    else:
	    bodytext.append('   <tr class="odd">')
    tmpuri = '?host=%s&service=%s' % \
      (hoststatus['host_name'], urllib.quote(service['service_description']))
    bodytext.append('    <td class="host"><a href="%s">%s</a></td>' % (tmpuri, description))
    bodytext.append('    <td class="%s narrow">%s</td>' % currentState)
    bodytext.append('    <td class="timestamp"><p>%s</p></td>' % lastTimeOK)
    bodytext.append('    <td><p>%s</p></td>' % pluginOutput)
    bodytext.append('    <td class="nowrap">')
    if nagios.permUserWrite():
        bodytext.append('     ' + sendMessage)
    bodytext.append('     ' + notifications)
    bodytext.append('    </td>')
    bodytext.append('   </tr>')
bodytext.append('  </table>')

# Print the graph(s) associated with what the user clicked on
if nagios.showHostGraphs:
    tmpuri = ['rrdpage.cgi?type=host']
    # FIXME: Pull this from the ini files.
    for graphtype in ['01_load', '02_cpu', '03_mem', '04_process', '07_space', '08_apachestats', '09_nginxstats']:
        tmpuri.append('&host=%s&graph=%s' % (host, graphtype))
    tmpuri = ''.join(tmpuri)
    bodytext.append('  <h1>[<a href="%s">Show All Graphs</a>]</h1>' % tmpuri)
    printDefaultGraphs=True
    if printDefaultGraphs:
        bodytext.append('  <a href="rrdpage.cgi?type=host&host=%s&graph=01_load">' % (hoststatus['host_name']))
        bodytext.append('   <img src="hostrrd.cgi?host=%s&graph=01_load&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  </a>')
        bodytext.append('  <a href="rrdpage.cgi?type=host&host=%s&graph=02_cpu">' % (hoststatus['host_name']))
        bodytext.append('   <img src="hostrrd.cgi?host=%s&graph=02_cpu&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  </a>')
        bodytext.append('  <a href="rrdpage.cgi?type=host&host=%s&graph=03_mem">' % (hoststatus['host_name']))
        bodytext.append('   <img src="hostrrd.cgi?host=%s&graph=03_mem&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  </a>')
        bodytext.append('  <a href="rrdpage.cgi?type=host&host=%s&graph=04_process">' % (hoststatus['host_name']))
        bodytext.append('   <img src="hostrrd.cgi?host=%s&graph=04_process&width=300&height=100&graphlegend=false" />' % (hoststatus['host_name']))
        bodytext.append('  </a>')

# Render the page and send it to the user
print HTML % {'refresh': 300, 'body': '\n'.join(bodytext)}
