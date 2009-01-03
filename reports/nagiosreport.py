#!/usr/bin/env python
"""Generate a daily email telling us what we need to know about nagios."""

import os, sys, time
if __file__[0] == '/':
    sys.path.append(os.path.join(os.path.dirname(__file__) + '/..'))
else:
    sys.path.append(os.path.join(os.getcwd() + '/..'))
import nagios

# Make sure that checks are happening actively.
starttime = time.localtime(int(nagios.programstatus['program_start']))
lastcheckts = int(nagios.info['created'])
lastcheck = time.localtime(lastcheckts)
if time.time() - lastcheckts > 600:
    print 'WARNING: Last check %s!' % nagios.relativeTime(lastcheckts)
print 'Running Since: %s' % time.strftime('%Y-%m-%d %H:%M:%S', starttime)
print 'Last Check:    %s' % time.strftime('%Y-%m-%d %H:%M:%S', lastcheck)
print '\n'

# Check some important settings
if nagios.programstatus['active_host_checks_enabled'] == '0':
    print 'WARNING: Active host checks are disabled!'
if nagios.programstatus['active_service_checks_enabled'] == '0':
    print 'WARNING: Active service checks are disabled!'
if nagios.programstatus['enable_notifications'] == '0':
    print 'WARNING: All notifications are disabled!'

print 'Current Known Problems'
print '----------------------'
for host in nagios.hoststatus:
    if nagios.hoststatus[host]['current_state'] == "1":
        # Host is Down
        print '%s: DOWN!\n' % host
    else:
        hasoutput = False
        for service in nagios.hoststatus[host]['services']:
            service = nagios.hoststatus[host]['services'][service]
            if service['current_state'] == "2":
                # Service is critical
                pluginoutput = service['plugin_output'].split()
                if service['check_command'] == 'check_nrpe!check_disk' and \
                  ' '.join(pluginoutput[:2]) == 'DISK CRITICAL':
                    print '%s: check_disk is:' % (host)
                    disks = service['plugin_output'].split(':')
                    for disk in disks:
                        print ' ', disk
                else:
                    print '%s: %s is:' % (host, service['check_command'])
                    print ' ', service['plugin_output']
                hasoutput = True
        if hasoutput:
            print
print

print 'Disabled Alerts'
print '---------------'
hosts = nagios.hoststatus.keys()
hosts.sort()
for host in hosts:
    hostprinted = False
    if nagios.hoststatus[host]['notifications_enabled'] == '0':
        print '%s: all services' % host
        hostprinted = True 
    for service in nagios.hoststatus[host]['services']:
        service = nagios.hoststatus[host]['services'][service]
        if service['notifications_enabled'] == '0':
            if not hostprinted:
                print '%s: %s' % (host, service['service_description'])
                hostprinted = True
            else:
                print '%s  %s' % (' '*len(host), service['service_description'])
print
