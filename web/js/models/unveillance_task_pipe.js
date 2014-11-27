var UnveillanceTaskPipe = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
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
		var tasks = _.flatten(_.map(els, function(el) {
			return _.filter(_.map($(el).val().split(/\s/), function(e) {
				return e.replace(/,/gi, '');
			}), function(e) {
				return !_.isEmpty(e);
			})
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
					console.warn("task extras appear to be invalid");
				}
			}
		}

		_.each(docs, function(doc) {
			var pipe = { _id : doc.get('data')._id }
			_.extend(pipe, pipe_default);	
			
			this.onTaskPipeStarted(doInnerAjax("reindex", "post", pipe, null, false));
		}, this);
	}
});