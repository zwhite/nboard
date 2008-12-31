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
        icon = 'images/ndisabled.gif'
    if nagios.permUserWrite():
        if type == 'contact':
            returnstr = imgstr % (icon, title, 'return false;')
        elif type == 'global':
            returnstr = imgstr % (icon, title, 'return false;')
        elif type == 'host':
            returnstr = imgstr % (icon, title, 'return false;')
        elif type == 'service':
            returnstr = imgstr % (icon, title, 'return false;')
    else:
        returnstr = imgstr % (icon, '', 'return false;')
    return returnstr
