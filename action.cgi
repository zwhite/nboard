#!/usr/bin/env python
"""Performs certain actions on behalf of the user, most of them relating to
send commands to nagios."""

import cgi, cgitb
cgitb.enable(logdir="/tmp")

form = cgi.FieldStorage()

runMode = form.getvalue('rm')
host = form.getvalue('commentEntryHost')
service = form.getvalue('commentEntryService')
commentText = form.getvalue('commentEntryText')

if runMode == 'message':
    print 'Content-Type: text/plain\n'
    print 'Send a message'
elif runMode == 'silence':
    if service != 'all alerts':
        print 'Content-Type: text/plain\n'
        print 'Silence single service'
    else:
        print 'Content-Type: text/plain\n'
        print 'Silence all services'
elif runMode == 'unsilence':
    if service != 'all alerts':
        print 'Content-Type: text/plain\n'
        print 'Unsilence a single service'
    else:
        print 'Content-Type: text/plain\n'
        print 'Unsilence all services'
else:
    print 'Status: 400 Unknown runmode'
    print 'Content-Type: text/plain\n'
    print 'Unknown runmode!'

print 'Note: This script needs to be implemented completely still.'
