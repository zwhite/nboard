#!/usr/bin/env python

# Wrapper script for sending notifications
import getopt, os, re, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))+'/..'))
import clickatel, nagios

# Attempt to log our options for debugging purposes.
try:
    options = open('/tmp/notify_opts.txt', 'w')
    for arg in sys.argv:
        options.write("'%s' " % arg)
    options.write('\n')
    options.close()
except IOError:
    pass

# Helpful functions
def nagiosCmd(cmd):
    cmdline = nagios.commands[cmd]['command_line']
    email =  nagios.contacts[vars['notify']]['email']
    pager = nagios.contacts[vars['notify']]['pager']
    cmdline = re.sub('\$CONTACTEMAIL\$', email, cmdline)
    cmdline = re.sub('\$CONTACTPAGER\$', pager, cmdline)
    cmdline = re.sub('\$HOSTALIAS\$', vars['host'], cmdline)
    cmdline = re.sub('\$HOSTNAME\$', vars['host'], cmdline)
    cmdline = re.sub('\$HOSTSTATE\$', vars['state'], cmdline)
    cmdline = re.sub('\$HOSTADDRESS\$', vars['address'], cmdline)
    cmdline = re.sub('\$HOSTOUTPUT\$', vars['serviceoutput'], cmdline)
    cmdline = re.sub('\$LONGDATETIME\$', vars['datetime'], cmdline)
    cmdline = re.sub('\$NOTIFICATIONTYPE\$', vars['type'], cmdline)
    cmdline = re.sub('\$SERVICEDESC\$', vars['service'], cmdline)
    cmdline = re.sub('\$SERVICEOUTPUT\$', vars['serviceoutput'], cmdline)
    cmdline = re.sub('\$SERVICESTATE\$', vars['state'], cmdline)
    os.system(cmdline)


# Parse our commandline
options = ''
long_options = [
	'type=', 'host=', 'service=', 'state=', 'address=', 'serviceoutput=',
	'datetime=', 'notify=', 'comment=', 'author=', 'lasthoststate=',
	'lastservicestate='
]
args, leftover = getopt.getopt(sys.argv[1:], options, long_options)
vars = {}
for arg in args:
    if arg[1] != '':
        vars[arg[0][2:]] = arg[1]

# Determine whether or not we should send an SMS
sendSMS = False
if 'notify_sms' in nagios.servicegroups:
    if vars['state'] in ['DOWN', 'UP', 'CRITICAL', 'OK']:
        members = nagios.servicegroups['notify_sms']['members']
        if vars['host'] in members:
            if 'service' in vars:
                if 'CRITICAL' in [vars['lastservicestate'], vars['state']]:
                    if vars['service'] in members[vars['host']]:
                        sendSMS = True
            else:
                sendSMS = True

# Format the output
if 'service' in vars:
    vars['serviceoutput'] = nagios.pluginOutput(vars['service'], 
                                                vars['serviceoutput'], '\\n')

# Check to see if we treat this as a normal service notification or a comment.
if 'comment' not in vars:
    # Call the same command nagios would in this situation
    if 'service' in vars:
        if sendSMS:
            cmds = ['notify-by-email', 'notify-by-sms']
        else:
            cmds = ['notify-by-email']
    else:
        if sendSMS:
            cmds = ['host-notify-by-email', 'host-notify-by-sms']
        else:
            cmds = ['host-notify-by-email']
    for cmd in cmds:
        nagiosCmd(cmd)
else:
    # Send an email with a comment about the service
    msg = []
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
    email =  nagios.contacts[vars['notify']]['email']
    cmd = """echo -e '%s' | mail -s 'Comment about %s from %s' '%s'""" % \
      (msg, host, author, email)
    os.system(cmd)

    if sendSMS:
        pager = nagios.contacts[vars['notify']]['pager']
        sms = clickatel.clickatel(nagios.sms['api_id'], nagios.sms['username'],
                                  nagios.sms['password'], pager)
        msg='MSG from %s about %s: %s' % (vars['author'],vars['host'],vars['comment'])
        sms.sendMsg(msg)
