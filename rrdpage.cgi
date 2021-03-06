#!/usr/bin/python
"""Display a page for one or more RRD images."""

import cgi, cgitb, os, re, sys, time, urllib
cgitb.enable(logdir="/tmp")

print 'Content-Type: text/html\n'

HTML = open('templates/basic.html').read()

form = cgi.FieldStorage()
bodytext = []

# Figure out start and end times
if 'start' in form:
    startTime=int(form.getfirst('start'))
    endTime=startTime + 86400
else:
    endTime=int(time.time())
    startTime=endTime - 86400
if 'end' in form:   
    endTime=int(form.getfirst('end'))
timePeriod=(endTime - startTime)
backStartTime=(startTime - timePeriod)
backEndTime=(endTime - timePeriod)
smBackStartTime=(startTime - (timePeriod / 2))
smBackEndTime=(endTime - (timePeriod / 2))
fwdStartTime=(startTime + timePeriod)
fwdEndTime=(endTime + timePeriod)
smFwdStartTime=(startTime + (timePeriod / 2))
smFwdEndTime=(endTime + (timePeriod / 2))
startTime_s=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
endTime_s=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTime))

# Figure out which graphs to show
rrdtype = form.getfirst('type')
imguris = []
pageuris = []
if rrdtype == 'host':
    hosts = form.getlist('host')
    graphs = form.getlist('graph')
    for (index, host) in enumerate(hosts):
        if len(graphs) < index:
            break
        imguri = 'hostrrd.cgi?host=%s&graph=%s&width=600&height=200'
        imguri += '&start=%s&end=%s'
        imguris.append(imguri % (host, graphs[index], startTime, endTime))
        pageuri = '?type=host&host=%s&graph=%s'
        pageuris.append(pageuri % (host, graphs[index]))
elif rrdtype == 'datasource':
    datasources = form.getlist('datasource')
    for datasource in datasources:
        imguri = 'rrdimg.cgi?width=600&height=200&datasource=%s&start=%s&end=%s'
        imguris.append(imguri % (datasource, startTime, endTime))
        pageuri = '?type=datasource&datasource=%s'
        pageuris.append(pageuri % datasource)
else:
    bodytext.append('<h1>Error: Unknown type: %s</h1>' % rrdtype)

# Figure out our current URL
thisurl = '&'+os.environ['QUERY_STRING']
if not re.search(r'&start=', thisurl):
    thisurl = '%s&start=%d' % (thisurl, startTime)
if not re.search(r'&end=', thisurl):
    thisurl = '%s&end=%d' % (thisurl, endTime)

# Figure out URI's for next and previous pages
backurl = re.sub(r'&start=\d*', '&start=%d' % backStartTime, thisurl)
backurl = re.sub(r'&end=\d*', '&end=%d' % backEndTime, backurl)
fwdurl = re.sub(r'&start=\d*', '&start=%d' % fwdStartTime, thisurl)
fwdurl = re.sub(r'&end=\d*', '&end=%d' % fwdEndTime, fwdurl)
smbackurl = re.sub(r'&start=\d*', '&start=%d' % smBackStartTime, thisurl)
smbackurl = re.sub(r'&end=\d*', '&end=%d' % smBackEndTime, smbackurl)
smfwdurl = re.sub(r'&start=\d*', '&start=%d' % smFwdStartTime, thisurl)
smfwdurl = re.sub(r'&end=\d*', '&end=%d' % smFwdEndTime, smfwdurl)

# Make sure our URI's are in the proper format
smbackurl = '?'+smbackurl[1:]
smfwdurl = '?'+smfwdurl[1:]
backurl = '?'+backurl[1:]
fwdurl = '?'+fwdurl[1:]
thisurl = '?'+thisurl[1:]

# Build the page
bodytext.append('<p><a href="%s">link to this page</a></p>' % thisurl)
bodytext.append('<table id="graphTable">')
for (index, uri) in enumerate(imguris):
    bodytext.append(' <tr>')
    bodytext.append('  <th>')
    bodytext.append('   <h5>')
    bodytext.append('    <a href="%s">[&lt;&lt;]</a>' % backurl)
    bodytext.append('    <a href="%s">[&lt;]</a>' % smbackurl)
    bodytext.append('   </h5>')
    bodytext.append('  </th>')
    bodytext.append('  <th>')
    bodytext.append('   %s &mdash; %s' % (startTime_s, endTime_s))
    bodytext.append('  </th>')
    bodytext.append('  <th>')
    bodytext.append('   <h5>')
    bodytext.append('    <a href="%s">[&gt;]</a>' % smfwdurl)
    bodytext.append('    <a href="%s">[&gt;&gt;]</a>' % fwdurl)
    bodytext.append('   </h5>')
    bodytext.append(' </tr>')
    bodytext.append(' <tr>')
    bodytext.append('  <td>')
    bodytext.append('   <h3>Time Period</h3>')
    bodytext.append('   <ul>')
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 31536000), thisurl)
    bodytext.append('    <li><a href="%s">1 year</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 15768000), thisurl)
    bodytext.append('    <li><a href="%s">6 months</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 7257600), thisurl)
    bodytext.append('    <li><a href="%s">12 weeks</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 2419200), thisurl)
    bodytext.append('    <li><a href="%s">4 weeks</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 604800), thisurl)
    bodytext.append('    <li><a href="%s">1 week</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 432000), thisurl)
    bodytext.append('    <li><a href="%s">5 days</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 259200), thisurl)
    bodytext.append('    <li><a href="%s">3 days</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 86400), thisurl)
    bodytext.append('    <li><a href="%s">1 day</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 43200), thisurl)
    bodytext.append('    <li><a href="%s">12 hours</li>' % tmpurl)
    tmpurl = re.sub(r'&start=\d*', '&start=%d' % (endTime - 21600), thisurl)
    bodytext.append('    <li><a href="%s">6 hours</li>' % tmpurl)
    bodytext.append('   </ul>')
    bodytext.append('  </td>')
    bodytext.append('  <td>')
    bodytext.append('   <a href="%s">' % pageuris[index])
    img = '    <img src="%s" style="display: block; margin: auto;" />' % uri
    bodytext.append(img)
    bodytext.append('   </a>')
    bodytext.append('  </td>')
    bodytext.append('  <td>')
    tmpurl = re.sub(r'&end=\d*', '', thisurl)
    tmpurl = re.sub(r'&start=\d*', '', tmpurl)
    bodytext.append('   <h3><a href="%s">Now</h3>' % tmpurl)
    curtime = int(time.time())
    for offset in [86400, 172800, 259200, 345600, 432000, 518400, 604800,
                   1209600, 2419200, 4838400, 7257600, 9676800]:
        thisDate = curtime - offset
        tmpurl = re.sub(r'&end=\d*', '&end=%d' % thisDate, thisurl)
        tmpurl = re.sub(r'&start=\d*', '&start=%d' % (thisDate-timePeriod), 
                        tmpurl)
        thisDateStr = time.strftime('%Y-%m-%d', time.localtime(thisDate))
        bodytext.append('   <h5><a href="%s">%s</h5>' % (tmpurl,thisDateStr))
    bodytext.append('  </td>')
    bodytext.append(' </tr>')
bodytext.append('</table>')

# Return the page
print HTML % {'refresh': 600, 'body': '\n'.join(bodytext)}
