var document_browser;

function initAnnexChannel() {
	if(!annex_channel) {
		return;
	}

	annex_channel.get('message_map').push({
		unveil : _.bind(document_browser.updateTaskMessage, document_browser)
	});
}

function initDocumentBrowser() {
	var doc_id = _.filter(window.location.pathname.split("/"), function(segment) {
		return !_.contains(["", "unveil", "document"], segment)})[0];

	document_browser = new UnveillanceDocument(doInnerAjax(
		"documents", "post", { _id : doc_id }, null, false));

	if(document_browser.get('result') != 200) { return false; }

	document_browser.unset('result');
	initAnnexChannel();
	return true;
}