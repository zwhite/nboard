"""Helper module for printing common HTML snippets."""

import nagios

def iconNotify(type, target, title='', enabled=True):
    """Returns an <img> suitable for displaying the notify icon.

    Possible types: contact, global, host, service
    """
    imgstr = '<img class="icon" src="%s" title="%s" onclick="%s" />'
    if enabled:
        icon = 'images/notify.gif'
    else:
        icon = 'images/icon_noalert.png'
    if nagios.permUserWrite():
        if type == 'contact':
            if enabled:
                js = "disableContactAlerts('%s');" % (target)
                title = 'Disable alerts for %s' % (target)
            else:
                js = "enableContactAlerts('%s');" % (target)
                title = 'Enable alerts for %s' % (target)
            returnstr = imgstr % (icon, title, js)
        elif type == 'global':
            if enabled:
                js = "disableContactAlerts('nagios');"
                title = 'Disable ALL alerts'
            else:
                js = "enableContactAlerts('nagios');"
                title = 'Enable ALL alerts'
            returnstr = imgstr % (icon, title, js)
        elif type == 'service':
            if enabled:
                js = "disableAlerts('%s', '%s');" % (target, title)
                title = 'Disable alerts for %s on %s' % (title, target)
            else:
                js = "enableAlerts('%s', '%s');" % (target, title)
                title = 'Enable alerts for %s on %s' % (title, target)
            returnstr = imgstr % (icon, title, js)
    else:
        returnstr = imgstr % (icon, '', 'return false;')
    return returnstr
