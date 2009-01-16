#!/usr/bin/env python
"""Performs certain actions on behalf of the user, most of them relating to
sending commands to nagios."""

import cgi, cgitb, time, sys
import nagios
cgitb.enable(logdir="/tmp")

form = cgi.FieldStorage()
HTML = open('templates/basic.html').read()

def nagiosCmd(cmd, cmdargs):
    """Send a command to nagios."""
    cmdFile = open(nagios.commandfile, 'a')
    ts = int(time.time())
    cmdFile.write('[%d] %s;%s\n' % (ts, cmd, cmdargs))


# Collect our CGI vars
runMode = form.getfirst('rm')
host = form.getfirst('commentEntryHost')
service = form.getfirst('commentEntryService')
commentText = form.getfirst('commentEntryText')

if runMode == 'message':
    if service == 'all services':
        nagiosCmd('SEND_CUSTOM_HOST_NOTIFICATION', '%s;2;%s;%s' % 
          (host, nagios.user, commentText))
    else:
        nagiosCmd('SEND_CUSTOM_SVC_NOTIFICATION', '%s;%s;2;%s;%s' % 
          (host, service, nagios.user, commentText))
elif runMode == 'silence':
    if service == 'all services':
        nagiosCmd('ADD_HOST_COMMENT', '%s;1;%s;%s' % 
          (host, nagios.contacts[nagios.user]['alias'], commentText))
        nagiosCmd('SEND_CUSTOM_HOST_NOTIFICATION', '%s;2;%s;%s' % 
          (host, nagios.user, 'Host alerts disabled: ' + commentText))
        nagiosCmd('DISABLE_HOST_SVC_NOTIFICATIONS', host)
        nagiosCmd('DISABLE_HOST_NOTIFICATIONS', host)
    else:
        nagiosCmd('ADD_SVC_COMMENT', '%s;%s;1;%s;%s' % 
          (host, service, nagios.contacts[nagios.user]['alias'], commentText))
        nagiosCmd('SEND_CUSTOM_SVC_NOTIFICATION', '%s;%s;2;%s;%s' % 
          (host, service, nagios.user, 'Service alerts disabled: '+commentText))
        nagiosCmd('DISABLE_SVC_NOTIFICATIONS', '%s;%s' % (host, service))
elif runMode == 'unsilence':
    if service == 'all services':
        nagiosCmd('SEND_CUSTOM_HOST_NOTIFICATION', '%s;2;%s;%s' % 
          (host, nagios.user, 'Host and Service alerts enabled.'))
        nagiosCmd('ENABLE_HOST_SVC_NOTIFICATIONS', host)
        nagiosCmd('ENABLE_HOST_NOTIFICATIONS', host)
        nagiosCmd('DEL_ALL_HOST_COMMENTS', '%s;%s' % (host, service))
    else:
        nagiosCmd('SEND_CUSTOM_SVC_NOTIFICATION', '%s;%s;2;%s;%s' % 
          (host, service, nagios.user, 'Service alerts enabled.'))
        nagiosCmd('ENABLE_SVC_NOTIFICATIONS', '%s;%s' % (host, service))
        nagiosCmd('DEL_ALL_SVC_COMMENTS', '%s;%s' % (host, service))
else:
    print 'Status: 400 Unknown runmode'
    print 'Content-Type: text/plain\n'
    print 'Unknown runmode!'
    sys.exit()

print 'Content-Type: text/html\n'
returnPage=['<h2>Command submitted. It may take a moment to be reflected.</h2>']
returnPage.append('<h4>Return to')
returnPage.append('<a href="hoststatus.cgi?host=%s">%s</a>.</h4>' % (host, host))
print HTML % {'refresh': 3000, 'body': '\n'.join(returnPage)}
