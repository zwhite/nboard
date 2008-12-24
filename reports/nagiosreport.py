#!/usr/bin/env python
"""Generate a daily email telling us what we need to know about nagios."""

import time
import nagios

lastcheck = time.localtime(int(nagios.info['created']))
print 'Last Nagios Check: ', time.strftime('%Y-%m-%d %H:%M:%S', lastcheck), '\n'

for host in nagios.hoststatus:
	if nagios.hoststatus[host]['current_state'] == "1":
		# Host is Down
		print '%s is DOWN!\n' % host
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
