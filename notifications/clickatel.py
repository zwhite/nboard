"""Python module for sending sms via Clickatel."""

import sys, urllib2

class clickatel:
    baseurl  = 'https://api.clickatell.com'

    def __init__(self,api_id,username,password,destnumber=None,message=None):
        self.api_id = api_id
        self.username = username
        self.password = password
        self.destnumber = None
        if destnumber:
            self.destnumber = destnumber
        if destnumber and message:
            self.sendMsg(message)

    def sendMsg(self, message):
        """Send a message."""
        if self.destnumber:
            args = 'api_id=%s&user=%s&password=%s&to=%s&text=%s'
            args = args % (self.api_id, self.username, self.password, 
                           self.destnumber, message)
            req = urllib2.urlopen('%s/http/sendmsg' % self.baseurl, args)
            result, reason = req.read().split(': ', 1)
            if result == 'ID':
                return True
            else:
                return result, reason


if __name__ == '__main__':
    usage='Usage: %s <api_id> <username> <password> <destination> <message>'
    if len(sys.argv) < 6:
        print usage % sys.argv[0]
        sys.exit(1)
    api_id   = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    destnumber = sys.argv[4]
    message = ' '.join(sys.argv[5:])
    sms = clickatel(api_id, username, password, destnumber)
    result = sms.sendMsg(message)
    if result == True:
        sys.exit(0)
    else:
        print usage % sys.argv[0]
        print
        print '%s: %s' % (result[0], result[1])
        sys.exit(1)
