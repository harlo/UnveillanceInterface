var UnveillanceTaskPipe = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
		this.set('task_clone_tmpl', getTemplate("task_clone_li.html"));
	},

	onDrag: function(evt) {
		var task_path = $($(evt.target).find('a')).html();
		evt.dataTransfer.setData("task_path", task_path);
	},

	onDrop: function(evt) {
		evt.preventDefault();

    	var task_path = evt.dataTransfer.getData("task_path");

    	if(task_path) {
    		var drop_clone = Mustache.to_html(this.get('task_clone_tmpl'), {
    			task_path : task_path,
    			task_path_hash : "task_path_" + MD5(task_path)
    		});

    		$(evt.target).append(drop_clone);
    	}    	
	},

	onDragOver: function(evt) {
		evt.preventDefault();
	},

	setOptions: function(el) {
		if(!this.has('pipe_options')) {
			console.info("no options for pipe");
			return;
		}

		var opt_li_tmpl = getTemplate("task_li.html");

		$(el).append(_.map(this.get('pipe_options'), function(opt) {
			return Mustache.to_html(opt_li_tmpl, {
				context : null,
				path : opt,
				description : opt
			});
		}, this));

	},
	onTaskPipeStarted: function(task) {
		console.info(task);
	},
	buildTaskPipeFrom : function(els, docs) {
		console.info(els);
		var tasks = _.flatten(_.map($(els).children('div.uv_task_pipe_path'), function(t) {
			var task_path = $($(t).find('span')).html();
			return task_path;
		}));

		this.onTaskPipeReady(docs, tasks);
	},
	onTaskPipeReady: function(docs, tasks) {
		if((_.isUndefined(docs) || _.isNull(docs)) && this.has('context')) {
			docs = [this.get('context')];
		} else if(!_.isArray(docs)) {
			docs = [docs];
		}

		if(_.isUndefined(docs) || _.size(docs) == 0) {
			console.err("No docs for pipe");
			return;
		}

		// is null? reindex entire doc
		// is string? do that task
		// is array? do pipe

		var pipe_default = {};
		if(_.isArray(tasks) || _.isString(tasks)) {
			if(_.isArray(tasks)) {
				_.extend(pipe_default, { task_queue : "[" + tasks.join(",") + "]" });
			} else if(_.isString(tasks)) {
				_.extend(pipe_default, { task_path : tasks });
			}

			if(this.has('task_extras')) {
				try {
					var task_extras = JSON.parse($(this.get('task_extras')).val());

					_.extend(pipe_default, task_extras);
					pipe_default.persist_keys = "[" + _.keys(task_extras).join(',') + "]";
				} catch(err) {
					console.warn(err);
					console.warn("task extras appear to be invalid");
				}
			}
		}

		_.each(docs, function(doc) {
			try {
				var pipe = { _id : doc.attributes ? doc.get('data')._id : doc._id };
			} catch(err) {
				console.warn(err);
				return;
			}

			_.extend(pipe, pipe_default);	
			
			this.onTaskPipeStarted(doInnerAjax("reindex", "post", pipe, null, false));
		}, this);
	}
});