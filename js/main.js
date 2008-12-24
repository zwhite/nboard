/* Used to show the comment box so that a service or host can be silenced.
 */

function showForm() {
	document.getElementById('commentEntryBox').style.display = 'block';
}

function changeForm(host, service, runmode, title) {
	var commentHost = document.getElementById('commentEntryHost');
	var commentService = document.getElementById('commentEntryService');
	var commentReason = document.getElementById('commentEntryReason');
	var commentRM = document.getElementById('rm');
	var titleNode = document.createTextNode(title);

	commentHost.setAttribute('value', host);
	commentService.setAttribute('value', service);
	commentRM.setAttribute('value', runmode);
	commentReason.removeChild(commentReason.childNodes[0]);
	commentReason.appendChild(titleNode);
}

function disableAlerts(host, service) {
	var title = 'Reason for silencing ' + service + ' on ' + host + ':';
	changeForm(host, service, 'silence', title);
	showForm();
}

function enableAlerts(host, service) {
	var commentForm = document.getElementById('commentEntryForm');
	var confirmation = 'Are you sure you wish to enable alerts for ' + service + ' on ' + host + '?\n\nThis action will also clear the status message!';

	changeForm(host, service, 'unsilence', '');
	if (confirm(confirmation)) {
		commentForm.submit();
	}
}

function sendMessage(host, service) {
	var title = 'Message to send about ' + service + ' on ' + host + ':';
	changeForm(host, service, 'message', title);
	showForm();
}

/* Quick-n-dirty javascript to do some xmlhttprequest magic. This could be
 * abstracted out better but it'd take more time. Quick hack FTW!
 *
 * This isn't currently being used in the dashboard.
 */

var liveUpdateReq;

if (window.XMLHttpRequest) {
        liveUpdateReq = new XMLHttpRequest();
}

function loadBodyText(url,target) {
        if (window.XMLHttpRequest) {
                // branch for IE/Windows ActiveX version
        } else if (window.ActiveXObject) {
                liveUpdateReq = new ActiveXObject("Microsoft.XMLHTTP");
        }

        liveUpdateReq.target = target;
        liveUpdateReq.onreadystatechange=showStatusForUpdatedField;
        liveUpdateReq.open("GET", url);
        liveUpdateReq.send(null);
}

function showStatusForUpdatedField() {
        if (liveUpdateReq.readyState == 4) {
                document.getElementById(liveUpdateReq.target).innerHTML = liveUpdateReq.responseText;
        }
}

function contentLoadingLoop() {
        loadBodyText('list.cgi','graphList');
        /* In 5 minutes, reload the table */
        setTimeout('contentLoadingLoop()', 5*60000);
}

/*window.onload = contentLoadingLoop;*/
