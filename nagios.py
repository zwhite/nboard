#!/usr/bin/env python
"""Parse the nagios status.dat file to get the status of certain services."""

# FIXME: This should probably build an object that can be instaniated instead.
import ConfigParser, os, sys, time

# Set some variables
version = '0.7'
if __file__[0] == '/':
    basedir = os.path.dirname(__file__)
else:
    basedir = os.getcwd()
configfile = os.path.join(basedir + '/conf/config.ini')
statuses = ['statusGood', 'statusWarn', 'statusCrit', 'statusUnknown']
if 'REMOTE_USER' in os.environ:
    user = os.environ['REMOTE_USER']
else:
    user = 'guest'

# Initialize some dictionaries
commands = {}
contacts = {}
contactgroups = {}
hosts = {}
hostgroups = {}
hoststatus = {}
services = {}
servicegroups = {}
timeperiods = {}

# Parse our configuration
config = ConfigParser.SafeConfigParser()
config.read(configfile)
icons = {}
for group, list in config.items('icons'):
    list = list.replace('\n', '').strip()
    icons[group] = list
commandfile = config.get('general', 'commandfile')
defaultGroup = config.get('general', 'defaultgroup')
try:
    grouporder = config.get('general', 'grouporder')
    grouporder = grouporder.replace('\n', '').replace(' ', '').split(',')
except ConfigParser.NoOptionError:
    grouporder = []
hostGraphBaseUrl = config.get('general', 'hostGraphBaseUrl', True)
objectcache = config.get('general', 'objectcache')
showGraphs = config.getboolean('general', 'graphs')
showHostGraphs = config.getboolean('general', 'showHostGraphs')
statusfile = config.get('general', 'statusfile')
sms = None
if config.has_section('clickatell_sms'):
    sms = {
        'api_id': config.get('clickatell_sms', 'api_id'),
        'username': config.get('clickatell_sms', 'user'),
        'password': config.get('clickatell_sms', 'password')
    }

# Parse the nagios configuration
objectcache_f = open(objectcache, 'r').readlines()
for line in objectcache_f:
    line=line.strip()
    if line == '' or line[0] == '#':
        continue
    elif line[-1] == '{':
        # Start a new section
        keyword = line.replace('{', '').strip().split()
        if keyword[0] == 'define':
            if keyword[1] == 'command':
                currentsection = {'type': 'command'}
            elif keyword[1] == 'contact':
                currentsection = {'type': 'contact'}
            elif keyword[1] == 'contactgroup':
                currentsection = {'type': 'contactgroup'}
            elif keyword[1] == 'host':
                currentsection = {'type': 'host'}
            elif keyword[1] == 'hostgroup':
                currentsection = {'type': 'hostgroup'}
            elif keyword[1] == 'service':
                currentsection = {'type': 'service'}
            elif keyword[1] == 'servicegroup':
                currentsection = {'type': 'servicegroup'}
            elif keyword[1] == 'timeperiod':
                currentsection = {'type': 'timeperiod'}
            else:
                print 'WARNING: Unknown contact keyword:', keyword[1]
                currentsection = {'type': 'unknown'}
    elif line == '}':
        # End a section
        if currentsection['type'] == 'command':
            commands[currentsection['command_name']] = currentsection
        elif currentsection['type'] == 'contact':
            contacts[currentsection['contact_name']] = currentsection
        elif currentsection['type'] == 'contactgroup':
            contactgroups[currentsection['contactgroup_name']] = currentsection
        elif currentsection['type'] == 'host':
            # hrm, hosts here!
            hosts[currentsection['host_name']] = currentsection
        elif currentsection['type'] == 'hostgroup':
            hostgroups[currentsection['hostgroup_name']] = currentsection
        elif currentsection['type'] == 'service':
            services[currentsection['service_description']] = currentsection
        elif currentsection['type'] == 'servicegroup':
            servicegroups[currentsection['servicegroup_name']] = currentsection
        elif currentsection['type'] == 'timeperiod':
            timeperiods[currentsection['timeperiod_name']] = currentsection
    else:
        # Parse a value in the current section
        var, value = line.split(None, 1)
        if var == 'members':
            currentsection[var] = value.split(',')
        else:
            currentsection[var] = value


# Parse the nagios status
status_f = open(statusfile, 'r').readlines()
for line in status_f:
    line=line.strip()
    if len(line) == 0 or line[0] == '#':
        continue
    elif line[-1] == '{':
        # Start a new section
        if line[:-2] == 'hoststatus':
            currentsection = {'type': 'host'}
        elif line[:-2] == 'info':
            currentsection = {'type': 'info'}
        elif line[:-2] == 'contactstatus':
            currentsection = {'type': 'contactstatus'}
        elif line[:-2] == 'programstatus':
            currentsection = {'type': 'programstatus'}
        elif line[:-2] == 'hostcomment':
            currentsection = {'type': 'hostcomment'}
        elif line[:-2] == 'servicecomment':
            currentsection = {'type': 'servicecomment'}
        elif line[:-2] == 'servicestatus':
            currentsection = {'type': 'service'}
        else:
            print 'WARNING: Unknown section:', line[:-2]
            currentsection = {'type': 'unknown'}
    elif line == '}':
        # End the current section
        if currentsection['type'] == 'info':
            info = currentsection
        elif currentsection['type'] == 'contactstatus':
            contacts[currentsection['contact_name']]['status'] = currentsection
        elif currentsection['type'] == 'programstatus':
            programstatus = currentsection
        elif currentsection['type'] == 'host':
            host = currentsection['host_name']
            hoststatus[host] = currentsection
        elif currentsection['type'] == 'service':
            host = currentsection['host_name']
            description = currentsection['service_description']
            if not hoststatus[host].has_key('services'):
                hoststatus[host]['services'] = {}
            hoststatus[host]['services'][description] = currentsection
        elif currentsection['type'] == 'hostcomment':
            host = currentsection['host_name']
            if 'comment' not in hoststatus[host]:
                hoststatus[host]['comment'] = []
            hoststatus[host]['comment'].append(currentsection)
        elif currentsection['type'] == 'servicecomment':
            host = currentsection['host_name']
            description = currentsection['service_description']
            service = hoststatus[host]['services'][description]
            if 'comment' not in service:
                service['comment'] = []
            service['comment'].append(currentsection)
    else:
        # Parse a value in the current section
        var, value = line.split('=', 1)
        currentsection[var] = value


# Check over everything, make sure it looks sane
if grouporder == []:
    for group in hostgroups:
        if group[:6] != 'check_':
		grouporder.append(group)
    grouporder.sort()
# Massage the servicegroups into a sane format
for servicegroup in servicegroups:
    hostlist = servicegroups[servicegroup]['members'][::2]
    services = servicegroups[servicegroup]['members'][1::2]
    servicegroups[servicegroup]['members'] = {}
    for host, service in zip(hostlist, services):
        if host not in servicegroups[servicegroup]['members']:
            servicegroups[servicegroup]['members'][host] = []
        servicegroups[servicegroup]['members'][host].append(service)


# Useful functions
def allGroupStatus():
    status = {}
    for group in grouporder:
        status[group] = groupStatus(group)
    return status


def getGroupIcon(group):
    """Returns the icon URI for a group."""
    if group in icons:
        return icons[group]
    return 'images/nboard_24.png'


def getHostIcon(host):
    """Returns the icon URI for a host."""
    if 'icon_image' in hosts[host] and hosts[host]['icon_image'] != '':
        return 'images/%s' % hosts[host]['icon_image']
    return 'images/nboard_24.png'


def groupStatus(group):
    """Returns a tuple containing the aggregated status of a group and whether
    notifications are enabled for anything marked critical. 
    """
    notifications = False
    status = 0
    if 'members' not in hostgroups[group]:
        return (0, False)
    for host in hostgroups[group]['members']:
        if group == 'critical':
            currentStatus, hostNotifications = hostStatus(host, True)
        else:
            currentStatus, hostNotifications = hostStatus(host)
        if currentStatus == 2:
            if status < 2: status = 2
        elif currentStatus == 1:
            if status < 1: status = 1
        if currentStatus > 1 and hostNotifications:
            if not notifications: notifications = True
    return (status, notifications)


def hostStatus(host, criticalGroup=False):
    """Returns a tuple containing the aggregated status of the host and whether
    notifications are enabled.

    If criticalGroup is True it will only return warning or critical for 
    services with notifications enabled.
    """
    if hoststatus[host]['current_state'] == "1":
        # No need to check the services, host is down
        if criticalGroup and hoststatus[host]['notifications_enabled'] == "0":
            return (2, False)
        else:
            return (2, True)
    status = 0
    notifications = False
    for service in hoststatus[host]['services']:
        service = hoststatus[host]['services'][service]
        if service['current_state'] == "2":
            if status < 2: status = 2
            if service['notifications_enabled'] == "1":
                notifications = True
        elif service['current_state'] == "1":
            if status < 1: status = 1
    if status > 1 and notifications:
        if criticalGroup:
            return (0, True)
        return (status, True)
    else:
        return (status, False)


def inGroup(host, hostgroup):
    "Returns true if the supplied host is in the supplied hostgroup."
    if host in hostgroups[hostgroup]['members']:
        return True
    return False


def permUserWrite(user=user):
    "Returns true if the supplied user is allowed to perform write operations."
    if user in contacts:
        return True
    return False


def pluginOutput(service, output, separator='<br />'):
    """Returns a copy of output formatted for human readability."""
    if service == 'All Disks':
        disks = output.split(':')
        return separator.join(disks)
    elif service == 'MySQL':
        lines = output.split('  ')
        return separator.join(lines)
    else:
        lines = output.split(' - ')
        return separator.join(lines)


def relativeTime(timestamp):
    if timestamp < 315532800:
        # Anything before 1980 might as well have been never.
        return 'never'
    timeDiff = time.time() - timestamp
    minAgo = int(timeDiff / 60)
    if timeDiff < 3601:
        return '%d min ago' % minAgo
    elif timeDiff < 172801:
        hourAgo = minAgo / 60
        minAgo = minAgo % 60
        return '%d hr %d min ago' % (hourAgo, minAgo)
    elif timeDiff < 1209603:
        return '%d days ago' % int(timeDiff / 86400)
    return '%d weeks ago' % int(timeDiff / 604800)

if __name__ == '__main__':
    # Test section
    #print allGroupStatus()
    #print groupStatus('database')
    #print 'database:', groupStatus('database')
    #print 'publish.dev:', hostStatus('publish.dev')
    #for group in grouporder:
    #    print group
    #print hostgroups.keys()
    #print inGroup('web1.sv2', 'critical')
    #foo = programstatus.keys()
    #foo.sort()
    #for key in foo:
    #    print key+'='+programstatus[key]
    #print contacts['zwhite']['alias']
    #print commands
    #print contacts['zwhite']
    #print contactgroups
    #print hosts['cronos.sv2']['address']
    print hostgroups['web']
    #print hoststatus['cronos.sv2']['services'].keys()
    #print services
    #print servicegroups['notify_sms']
    #for host in servicegroups['notify_sms']['members']:
    #    print host
    #print timeperiods
    #print sms
    #for host in hosts:
    #    print hosts[host]['icon_image']
