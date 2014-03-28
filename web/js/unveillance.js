function toURLString(json) {
	return encodeURIComponent(JSON.stringify(json));
}

function doInnerAjax(url, method, data, callback) {
	$.ajax({
		url: "/" + url + "/",
		dataType: "json",
		data: data,
		method: method,
		complete: callback
	});
}

function getTemplate(tmpl, on_complete, static_root) {
	if(!static_root) { static_root = "/web/layout/tmpl/"; }
	
	var a_obj = {
		url : (static_root + tmpl),
		method: "get",
		dataType: "html"
	};
	
	if(on_complete) { a_obj.complete = on_complete; }
	
	$.ajax(a_obj);
}

function insertTemplate(tmpl, data, append_root, on_complete, static_root) {
	if(data == null) { data = {}; }
	if(!static_root) { static_root = "/web/layout/tmpl/"; }
	
	var a_obj = {
		url : (static_root + tmpl),
		method: "get",
		dataType: "html",
		success: function(html) {
			$(append_root).html(Mustache.to_html(html, data));
		}
	};
	
	if(on_complete) { a_obj.complete = on_complete; }
	
	$.ajax(a_obj);
}

function removeEl() {
	console.info("removing a genereric element");
	console.info(this);
}

function doPost(endpoint, in_el, out_el) {
	if(in_el[0] != "#") {
		in_el = "#" + in_el;
	}
	
	if(out_el[0] != "#") {
		out_el = "#" + out_el;
	}
	
	console.info(endpoint);
	
	data = {}
	
	switch($(in_el).get(0).tagName.toLowerCase()) {
		case "textarea":
			data['input'] = $(in_el).val();
			break;
	}
	
	doInnerAjax(endpoint, "post", data, function(json) {
		console.info(json);
		console.info($(out_el));
		$(out_el).html(JSON.stringify(json));
	});
}