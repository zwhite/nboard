#!/usr/bin/env python
"""Parse the nagios status.dat file to get the status of certain services."""

# FIXME: This should probably build an object that can be instaniated instead.
import ConfigParser, sys, time

# Set some variables
configfile = 'conf/config.ini'
contacts = {}
contactgroups = {}
contactstatus = {}
hoststatus = {}
info = {}
nagiosstatus = {}
statuses = ['statusGood', 'statusWarn', 'statusCrit']

# Parse our configuration
config = ConfigParser.SafeConfigParser()
config.read(configfile)
hostlist = {}
grouplist = {}
for group, list in config.items('groups'):
    groupnumber, groupname = group.split('_')
    groupnumber = int(groupnumber)
    list = list.replace('\n', '').replace(' ', '').split(',')
    hostlist[groupname] = list
    grouplist[groupnumber] = groupname
icons = {}
for group, list in config.items('icons'):
    list = list.replace('\n', '').strip()
    icons[group] = list
statusfile = config.get('general', 'statusfile')
commandfile = config.get('general', 'commandfile')
contactsfile = config.get('general', 'contactsfile')
defaultGroup = config.get('general', 'defaultgroup')
showHostGraphs = config.getboolean('general', 'showHostGraphs')
hostGraphBaseUrl = config.get('general', 'hostGraphBaseUrl', True)

# Parse the contactsfile
contacts_f = open(contactsfile, 'r').readlines()
for line in contacts_f:
    line=line.strip()
    if line == '' or line[0] == '#':
        continue
    elif line[-1] == '{':
        # Start a new section
        keyword = line.replace('{', '').strip().split()
        if keyword[0] == 'define':
            if keyword[1] == 'contactgroup':
                currentsection = {'type': 'contactgroup'}
            elif keyword[1] == 'contact':
                currentsection = {'type': 'contact'}
            else:
                print 'WARNING: Unknown contact keyword:', keyword[1]
                currentsection = {'type': 'unknown'}
    elif line == '}':
        # End a section
        if currentsection['type'] == 'contactgroup':
            contactgroups[currentsection['contactgroup_name']] = currentsection
        elif currentsection['type'] == 'contact':
            contacts[currentsection['contact_name']] = currentsection
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
        elif currentsection['type'] == 'nagiosstatus':
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


# Useful functions
def allGroupStatus():
    status = {}
    for group in hostlist:
        status[group] = groupStatus(group)
    return status


def groupStatus(group):
    """Returns the aggregated status of a group. 
    """
    notifications = 1
    status = 0
    for host in hostlist[group]:
        if group == 'critical':
            currentStatus, hostNotifications = hostStatus(host, True)
        else:
            currentStatus, hostNotifications = hostStatus(host)
        if currentStatus == 2:
            if status < 2: status = 2
        elif currentStatus == 1:
            if status < 1: status = 1
        if currentStatus > 1 and hostNotifications:
            if notifications == 1: notifications = 0
    return (status, notifications)


def hostStatus(host, notifications=False):
    """Returns a tuple containing the aggregated status of the host and whether
    notifications are enabled.

    If notifications is True it will only return critical for services with
    notifications enabled.
    """
    if hoststatus[host]['current_state'] == "1":
        # No need to check the services, host is down
        if notifications and hoststatus[host]['notifications_enabled'] == "0":
            return (2, False)
        else:
            return (2, True)
    status = 0
    for service in hoststatus[host]['services']:
        service = hoststatus[host]['services'][service]
        if service['current_state'] == "2":
            if status < 2: status = 2
        elif service['current_state'] == "1":
            if status < 1: status = 1
    if service['notifications_enabled'] == "0":
        return (status, False)
    else:
        return (status, True)


def permUserWrite(user):
    "Returns true if the supplied user is allowed to perform write operations."
    if user in contacts:
        return True
    return False


def pluginOutput(service, output):
    """Returns a copy of output formatted for inclusion in an HTML document."""
    if service == 'All Disks':
        disks = output.split(':')
        return '<br />'.join(disks)
    elif service == 'MySQL':
        lines = output.split('  ')
        return '<br />'.join(lines)
    else:
        lines = output.split(' - ')
        return '<br />'.join(lines)


def relativeTime(timestamp):
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
    #print 'web:', groupStatus('web')
    print 'web7.sv2:', hostStatus('web7.sv2')
