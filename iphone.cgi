#!/usr/bin/python

## Nag Small Screen   v1.04
## Ryan McDonald 2006    http://ryanmcdonald.net/nss
## This software is distributed under the GPL.
## Tested under Python 2.4.3 and Nagios 2.5
## Modified for iPhone 2008 Oct 23 by Zach White zach@box.net
## Tested under Python 2.4.3 and Nagios 3.0.3

import os.path, datetime, sys, re

class Nag:
    
    def __init__(self):

        self.hosts={}
	datfile="/usr/local/nagios/var/status.dat"

	print "Content-type: text/html"
	print 
	print """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>Nagios Status</title>
  <meta name="viewport" content="width=320; initial-scale=1.0;
   maximum-scale=1.0; user-scalable=0;" />
  <link rel="StyleSheet" href="iui/iui.css" type="text/css" media="screen" />
  <link rel="apple-touch-icon" href="images/nboard_57.png" />
  <script type="application/x-javascript" src="iui/iui.js"></script>
 </head>

 <body>
  <div class="toolbar">
  <h1 id="pageTitle"></h1>
  <a id="backButton" class="button" href="#"></a>
  </div>
"""
        if os.path.exists(datfile) == False:
	    print "<p>Nagios status file not found.  Check file path.</p>"
            return

        self.infile = open(datfile,"r")
        while 1:
            line = self.infile.readline()
            if line == "":
                break
            if line[:4] == "info":
                #self.info()
                pass
            if line[:4] == "host":
                self.host()
            if line[:7] == "service":
                self.service()
        # Generate the index page
        print '<ul id="hostList" title="Nagios Status" selected="true">' 
	print '<li>'+datetime.datetime.now().strftime("%c")+'</li>'
        for host in self.hosts:
            hostid = re.sub('[^a-zA-Z0-9]', '_', host)
            print '<li><a href="#host_%s">%s (%s)</a></li>' % (hostid, host, len(self.hosts[host]))
        print '</ul>'
        # Generate each host entry
        for host in self.hosts:
            hostid = re.sub('[^a-zA-Z0-9]', '_', host)
            print '<ul id="host_%s" title="%s">' % (hostid, host)
            for problem in self.hosts[host]:
                print '<li>'+problem+'</li>'
            print '</ul>'
        print '</body>\n</html>'

    def info(self):
        while 1:
            line = self.infile.readline()
            line = line.strip()
            if line == "}":
                break
            param = line.split("=")[0]
            if param == "created":
                t = long(line[8:])
                created = datetime.datetime.fromtimestamp(t).strftime("%m/%d/%Y %I:%M %p")

        print "<b>Last Nagios Check: </b><br>\n " + created + "<br>" 

    def host(self):
        while 1:
            line = self.infile.readline()
            line = line.strip()
            if line == "}":
                break
            param = line.split("=")[0]
            if param == "host_name":
                host_name = line.split("=")[1]
            if param == "current_state":
                current_state = line.split("=")[1]
            if param == "plugin_output":
                plugin_output = line.split("=")[1]
            if param == "last_state_change":
                t = long(line.split("=")[1])
                last_state_change = datetime.datetime.fromtimestamp(t).strftime("%m/%d/%Y %I:%M %p")
            if param == "problem_has_been_acknowledged":
                problem_has_been_acknowledged=line.split("=")[1]

        try:
            if current_state != "0" and problem_has_been_acknowledged == "0":
                if not self.hosts.has_key(host_name):
                    self.hosts[host_name]=[]
                self.hosts[host_name].append("Host Ping<br />\n"+last_state_change+"<br />\n" + plugin_output)
        except UnboundLocalError:
            pass
    
    def service(self):
        while 1:
            line = self.infile.readline()
            line = line.strip()
            if line == "}":
                break
            param = line.split("=")[0]
            if param == "host_name":
                host_name = line[10:]
            if param == "service_description":
                service_description = line[20:]
            if param == "current_state":
                current_state = line[14:]
            if param == "plugin_output":
                plugin_output = line[14:]
            if param == "last_state_change":
		t = long(line[18:])
                last_state_change = datetime.datetime.fromtimestamp(t).strftime("%m/%d/%Y %I:%M %p")
            if param == "problem_has_been_acknowledged":
                problem_has_been_acknowledged=line.split("=")[1]


        try:
            if current_state != "0" and problem_has_been_acknowledged == "0":
                if not self.hosts.has_key(host_name):
                    self.hosts[host_name]=[]
                self.hosts[host_name].append(service_description + "<br />\n" + last_state_change  + "<br />\n" + plugin_output)
        except UnboundLocalError:
            pass

app = Nag()
