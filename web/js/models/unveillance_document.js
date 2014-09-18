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
	},
	refreshTags: function() {
		if(!current_user) { return; }
		this.set('tags', _.filter(
			current_user.getDirective('tags').tags,
			function(tag) {
				return _.contains(tag.documents, this.get('data')._id);
			}, this));

		try {
			onTagsRefreshed();
		} catch(err) { console.warn(err); }
	},
	addTag: function(tag_name) {
		if(!current_user) { return; }

		var tag = this.getTagByName(tag_name);
		if(!tag) {
			tag = new UnveillanceDocumentTag({ label : tag_name });
		}

		tag.addDocument(this.get('data')._id);
		this.refreshTags();
	},
	removeTag: function(tag_name) {
		if(!current_user) { return; }

		tag = this.getTagByName(tag_name);
		if(tag) {
			tag.removeDocument(this.get('data')._id);
			this.refreshTags();
		}
	},
	getTagByName: function(tag_name) {
		if(!current_user) { return; }

		var tag = _.findWhere(current_user.getDirective('tags').tags, { hash : MD5(tag_name) });
		if(tag) {
			return new UnveillanceDocumentTag(tag);
		}

		return;
	}
});

var UnveillanceDocumentTag = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);

		if(!this.get('hash')) {
			this.set('hash', MD5(this.get('label')));
		}

		this.idAttribute = "hash";
	},
	addDocument: function(doc_id) {
		if(!this.has('documents')) {
			this.set('documents', []);
		}

		if(!(_.contains(this.get('documents'), doc_id))) {
			this.get('documents').push(doc_id);
			this.update();
		}
	},
	removeDocument: function(doc_id) {
		if(!this.has('documents')) { return; }

		var updated = _.without(this.get('documents'), doc_id);

		this.set('documents', updated);
		this.update();
	},
	update: function() {
		var tags = current_user.getDirective('tags').tags;
		var self = _.findWhere(tags, { hash : this.get('hash') });

		if(self) {
			tags[_.indexOf(tags, self)] = this.toJSON();
		} else {
			tags.push(this.toJSON());
		}

		current_user.save();
	}
});