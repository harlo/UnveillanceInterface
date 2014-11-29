var document_browser, task_pipe;

function initDocumentBrowser() {
	var doc_id = _.filter(window.location.pathname.split("/"), function(segment) {
		return !_.contains(["", "unveil", "document"], segment)})[0];

	document_browser = new UnveillanceDocument(doInnerAjax(
		"documents", "post", { _id : doc_id }, null, false));

	if(document_browser.get('result') != 200) { return false; }

	document_browser.unset('result');
	task_pipe = new UnveillanceTaskPipe({
		context : document_browser,
		pipe_options : UV.MIME_TYPE_TASKS[document_browser.get('data').mime_type]
	});

	window.onSingleTaskRequested = _.bind(function(task_path) {
		this.onTaskPipeReady(null, task_path);
	}, task_pipe);

	window.onReindexRequested = _.bind(function() {
		this.onTaskPipeReady();
	}, task_pipe);

	window.onTaskPipeRequested = _.bind(function() {
		this.buildTaskPipeFrom($("#uv_reindex_custom"));
	}, task_pipe);

	return true;
}