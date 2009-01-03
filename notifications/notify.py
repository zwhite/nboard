#!/usr/bin/env python

# Wrapper script for sending notifications
import getopt, os, re, sys
if __file__[0] == '/':
    sys.path.append(os.path.join(os.path.dirname(__file__) + '/..'))
else:
    sys.path.append(os.path.join(os.getcwd() + '/..'))
import nagios

# Parse our commandline
options = ''
long_options = [
	'type=', 'host=', 'service=', 'state=', 'address=', 'serviceoutput=',
	'datetime=', 'notify=', 'comment=', 'author='
]
args, leftover = getopt.getopt(sys.argv[1:], options, long_options)
vars = {}
for arg in args:
    if arg[1] != '':
        vars[arg[0][2:]] = arg[1]

if 'service' in vars:
    vars['serviceoutput'] = nagios.pluginOutput(vars['service'], vars['serviceoutput'], '\\n')
if 'comment' not in vars:
    # For now, just call the same command nagios would in this situation
    if 'service' in vars:
        cmd = nagios.commands['notify-by-email']['command_line']
    else:
        cmd = nagios.commands['host-notify-by-email']['command_line']
    cmd = re.sub('\$CONTACTEMAIL\$', vars['notify'], cmd)
    cmd = re.sub('\$HOSTALIAS\$', vars['host'], cmd)
    cmd = re.sub('\$HOSTNAME\$', vars['host'], cmd)
    cmd = re.sub('\$HOSTSTATE\$', vars['state'], cmd)
    cmd = re.sub('\$HOSTADDRESS\$', vars['address'], cmd)
    cmd = re.sub('\$HOSTOUTPUT\$', vars['serviceoutput'], cmd)
    cmd = re.sub('\$LONGDATETIME\$', vars['datetime'], cmd)
    cmd = re.sub('\$NOTIFICATIONTYPE\$', vars['type'], cmd)
    cmd = re.sub('\$SERVICEDESC\$', vars['service'], cmd)
    cmd = re.sub('\$SERVICEOUTPUT\$', vars['serviceoutput'], cmd)
    cmd = re.sub('\$SERVICESTATE\$', vars['state'], cmd)
    os.system(cmd)
else:
    # Send an email with a comment about the service
    msg = ['***** Nagios *****']
    msg.append('')
    msg.append('Time: ' + vars['datetime'])
    msg.append('Host: ' + vars['host'])
    msg.append('Address: ' + vars['address'])
    if 'service' in vars:
        msg.append('Service: ' + vars['service'])
    msg.append('State: ' + vars['state'])
    msg.append('')
    msg.append('Comment by %s:' % (vars['author']))
    msg.append('')
    msg.append(vars['comment'])
    msg = '\\n'.join(msg)
    safestr = re.compile("'")
    msg = safestr.sub("\\'", msg)
    host = safestr.sub("\\'", vars['host'])
    author = safestr.sub("\\'", vars['author'])
    notify = safestr.sub("\\'", vars['notify'])
    cmd = """echo -e '%s' | mail -s 'Comment about %s from %s' '%s'""" % \
      (msg, host, author, notify)
    os.system(cmd)
