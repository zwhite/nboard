#!/usr/bin/env python
"""Performs certain actions on behalf of the user, most of them relating to
sending commands to nagios."""

import cgi, cgitb, time
import nagios
cgitb.enable(logdir="/tmp")

form = cgi.FieldStorage()

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
    print 'Location: hoststatus.cgi?host=%s&service=%s\n' % (host, service)
elif runMode == 'silence':
    if service == 'all services':
        print 'Content-Type: text/plain\n'
        print 'Silence all services'
    else:
        print 'Content-Type: text/plain\n'
        print 'Silence single service'
elif runMode == 'unsilence':
    if service == 'all services':
        print 'Content-Type: text/plain\n'
        print 'Unsilence all services'
    else:
        print 'Content-Type: text/plain\n'
        print 'Unsilence a single service'
else:
    print 'Status: 400 Unknown runmode'
    print 'Content-Type: text/plain\n'
    print 'Unknown runmode!'

print 'Note: This script needs to be implemented completely still.'
