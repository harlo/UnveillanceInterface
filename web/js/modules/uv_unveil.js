var document_browser, task_pipe;

function onAssetsInvoked() {
	var a_tmpl = getTemplate("asset_download.html");

	_.each($("#uv_document_asset_list").find('li'), function(li) {
		var file_name = $($(li).children('a')[0]).html();
		var download = $(Mustache.to_html(a_tmpl, { file_name : file_name }))
			.click(function() {
				onDownloadRequested(file_name, this);
			});

		$(li).append(download);
	}, this);
}

function onDownloadRequested(file_name, el) {
	$(el).unbind("click");

	var data = getFileContent(this,
		[".data", document_browser.get('data')._id, file_name].join('/'), null);

	var is_valid = true;
		
	if(_.isNull(data)) {
		is_valid = false;
	} else {
		try {
			if(JSON.parse(data).result == 404) {
				is_valid = false;
			}
		} catch(err) {}
	}

	if(!is_valid) {
		alert("Could not dowload file");
		return;
	}

	//141264

	data_array = new Uint8Array(data.length);
	console.info(data.length);
	for(var i=0; i < data.length; i++) {
		data_array[i] = data.charCodeAt(i);
	}

	console.info(data_array.length);

	var download_url = window.URL.createObjectURL(new Blob([data_array.buffer]));
	$(el).attr({
		'href' : download_url,
		'download' : [document_browser.get('data')._id, file_name].join('_')
	});
	
	window.setTimeout(function() {
		$(el).click();
		$(el).removeAttr('href');
		$(el).removeAttr('download');
		$(el).click(function() {
			onDownloadRequested(file_name, this);
		});
		window.URL.revokeObjectURL(download_url);
	}, 300);
}

function initDocumentBrowser() {
	var doc_id = _.filter(window.location.pathname.split("/"), function(segment) {
		return !_.contains(["", "unveil", "document"], segment)})[0];

	document_browser = new UnveillanceDocument(doInnerAjax(
		"documents", "post", { _id : doc_id }, null, false));

	if(document_browser.get('result') != 200) { return false; }

	document_browser.unset('result');
	task_pipe = new UnveillanceTaskPipe({
		context : document_browser,
		pipe_options : UV.MIME_TYPE_TASKS[document_browser.get('data').mime_type],
		task_extras: $("#uv_reindex_custom_extras")
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