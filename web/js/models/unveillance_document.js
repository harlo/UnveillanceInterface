var UnveillanceDocument = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
		this.idAttribute = "_id";
	},
	getAssetsByTagName: function(tag) {
		var tagged_assets = [];
		if(this.has("assets")) {
			_.each(this.get("assets"), function(asset) {
				if(asset.tags && asset.tags.indexOf(tag) != -1) {
					tagged_assets.push(asset);
				}
			});
		}
		
		return tagged_assets;
	},
	reindex: function(callback, req, task_path) {
		if(task_path) { _.extend(req, { task_path : task_path }); }

		return doInnerAjax("reindex", "post", req, callback, false);
	},
	setInPanel: function(asset, panel) {
		var callback;

		if(!panel) {
			panel = $(document.createElement('div'))
				.attr('id',  "uv_document_view_panel");

			$('body').append(panel);
		}

		switch(asset) {
			case "reindexer":
				var ctx = this.get('data');
				
				callback = function() {
					$("#uv_reindex_list").html(Mustache.to_html(getTemplate("task_li.html"),
						_.map(UV.MIME_TYPE_TASKS[ctx.mime_type], function(task) {							
							return { path : task, desc: task };
						})
					));
				}

				break;
		}

		insertTemplate(asset + ".html", this.toJSON().data,
			panel, callback, "/web/layout/views/unveil/");
	}
});