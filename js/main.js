function changeForm(host, service, runmode, title) {
	var commentBox = document.getElementById('commentEntryBox');
	var commentHost = document.getElementById('commentEntryHost');
	var commentService = document.getElementById('commentEntryService');
	var commentReason = document.getElementById('commentEntryReason');
	var commentText = document.getElementById('commentEntryText');
	var commentRM = document.getElementById('rm');
	var titleNode = document.createTextNode(title);

	commentHost.setAttribute('value', host);
	commentService.setAttribute('value', service);
	commentRM.setAttribute('value', runmode);
	commentReason.removeChild(commentReason.childNodes[0]);
	commentReason.appendChild(titleNode);
	commentBox.style.display = 'block';
	commentText.focus();
}

function disableAlerts(host, service) {
	var title = 'Reason for silencing ' + service + ' on ' + host + ':';
	changeForm(host, service, 'silence', title);
	showForm();
}

function enableAlerts(host, service) {
	var commentForm = document.getElementById('commentEntryForm');
	var confirmation = 'Are you sure you wish to enable alerts for ' + service + ' on ' + host + '?\n\nThis action will also clear the status message!';

	if (confirm(confirmation)) {
		changeForm(host, service, 'unsilence', '');
		commentForm.submit();
	}
}

function sendMessage(host, service) {
	var title = 'Message to send about ' + service + ' on ' + host + ':';
	changeForm(host, service, 'message', title);
	showForm();
}
