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
				callback = window.onReindexerInvoked || function() {
					$('#uv_pipe_builder').html(getTemplate("pipe_builder.html"));
					if(task_pipe) {
						task_pipe.setOptions($("#uv_reindex_list"));
						task_pipe.set('task_extras',  $("#uv_reindex_custom_extras"));
					}
				}

				break;
			case "assets":
				callback = window.onAssetsInvoked || null;
				break;
			case "info":
				callback = window.onInfoInvoked || null;
				break;
		}

		insertTemplate(asset + ".html", this.toJSON().data,
			panel, callback, "/web/layout/views/unveil/");
	},
	refreshTags: function() {
		if(!window.current_user) { return; }

		try {
			this.set('tags', _.filter(
				current_user.getDirective('tags').tags,
				function(tag) {
					return _.contains(tag.documents, this.get('data')._id);
				}, this));
		} catch(err) {
			console.info(err);
			this.set('tags', []);
		}


		try {
			onTagsRefreshed();
		} catch(err) { console.warn(err); }
	},
	addTag: function(tag_name) {
		if(!window.current_user) { return; }

		var tag = this.getTagByName(tag_name);
		if(!tag) {
			tag = new UnveillanceDocumentTag({ label : tag_name });
		}

		tag.addDocument(this.get('data')._id);
		this.refreshTags();
	},
	removeTag: function(tag_name) {
		if(!window.current_user) { return; }

		var tag = this.getTagByName(tag_name);
		if(tag) {
			tag.removeDocument(this.get('data')._id);
			this.refreshTags();
		}
	},
	getTagByName: function(tag_name) {
		if(!window.current_user) { return; }

		var tag = _.findWhere(current_user.getDirective('tags').tags, { hash : MD5(tag_name) });
		if(tag) {
			return new UnveillanceDocumentTag(tag);
		}

		return;
	},
	getChildAsset: function(_id, doc_type) {
		return doInnerAjax("documents", "post", {
			doc_type : doc_type,
			_id : _id,
			media_id : this.get('data')._id
		}, null, false).data;
	},
	updateTaskMessage: function(message) {
		console.info(message);
		
		if(message.doc_id && message.doc_id == this.get('data')._id) {
			var message_li = $(document.createElement('li')).html(JSON.stringify(message));
			
			$($("#uv_default_task_update").children('ul')[0]).append(message_li);

			window.setTimeout(function() { $(message_li).remove(); }, 15000);
		}
	}
});

var UnveillanceDirectiveItem = Backbone.Model.extend({
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
		var items = current_user.getDirective(this.get('d_name'))[this.get('d_name')];
		var self = _.findWhere(items, { hash : this.get('hash') });

		if(self) {
			items[_.indexOf(items, self)] = this.toJSON();
		} else {
			items.push(this.toJSON());
		}

		current_user.save();
	},
	remove: function() {
		var items = current_user.getDirective(this.get('d_name'))[this.get('d_name')];
		var self = _.findWhere(items, { hash : this.get('hash') });

		if(self) {
			items.splice(_.indexOf(items, self), 1);
			current_user.save();
		}
	}
});

var UnveillanceDocumentTag = UnveillanceDirectiveItem.extend({
	constructor: function() {
		UnveillanceDirectiveItem.prototype.constructor.apply(this, arguments);

		this.set('d_name', "tags");
	}
});