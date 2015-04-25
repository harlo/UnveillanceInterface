var app = app || {};//global Backbone

jQuery(document).ready(function($) {

//http://stackoverflow.com/questions/6535948/nested-model-in-backbone-js-how-to-approach

/*
adding a row to collection triggers adding rowView to collectionView
when row model changes, rowView alerts collectionView to update rendering
*/
	app.TimestampDatasets = Backbone.Collection.extend();
	
	app.Datasets = Backbone.Collection.extend();
	
	app.DataSet = Backbone.Model.extend({
		initialize: function(options) {
			this.model_id = options.model_id;
			this.modelCount = 0;
			
			_.each(this.models, function(model) {
				model.set('id', this.get('model_id'));
				model.fetch();
			}, this);
			
			_.each(this.models, function(model) {
				//fire change event when all nested models have loaded
				this.listenTo(model, 'sync', function() {
					this.modelCount++;
					if (this.modelCount == _.size(this.models)) {
						this.set({ready: true});
						this.trigger('render');
					}
				});
			}, this);

		},
	});
	
	app.HeaderDataSet = app.DataSet.extend({
		initialize: function(options) {
			this.models = {
				documentWrapper: new app.InformaCamDocumentWrapper(),
				J3MHeader: new app.InformaCamJ3MHeader(),
			};
			app.DataSet.prototype.initialize.apply(this, arguments);
		},
		parseMe: function() {
			data = {};
			json = this.models.documentWrapper.toJSON().data;
			data.j3m_id = json.j3m_id;
			data.dateAddedFormatted = json.dateAddedFormatted;
			data.upload_attempts = json.upload_attempts;
			data.j3m_verified = json.j3m_verified;
			data.media_verified = json.media_verified;
			json = this.models.J3MHeader.toJSON().data;
			data.dateCreatedFormatted = json.dateCreatedFormatted;
			return data;
		}
	});
	
	app.TimestampDataSet = app.DataSet.extend({
		initialize: function(options) {
			this.models = {
				J3MTimeStampedData: new app.InformaCamJ3MTimeStampedData({
					urlRoot: '/GPSData',
				}),
			};
			app.DataSet.prototype.initialize.apply(this, arguments);
		},
		parseMe: function() {
			data = this.models.J3MTimeStampedData.get("values");
			return data;
		}
	});
	
	app.TableView = Backbone.View.extend({
		initialize: function(options) {
			this.template = getTemplate(options.template);
			this.views = [];
			this.listenTo(this.collection, "add", function(model) {
				this.views.push(new app.TableRowView({ model: model, parentView: this }));
			});
			this.listenTo(this.collection, "remove", function(model) {
				this.views = _.without(this.views, _.findWhere(this.views, {model: model, parentView: this}));
				this.render();
			});
		},
		render: function() {
			if (this.$el.attr('id') == 'ic_tsv_timestampdata') {
				app.timestampTablesView.render();
			} else {
				if (this.views.length) {
					var json = [];
					_.each(this.views, function(view) {
						if (view.model.get('ready')) {
							json.push(view.render());
						}
					}, this);
					$('#ic_tsv_download_view_holder').addClass("rendered");
					html = Mustache.to_html(this.template, json);
					this.$el.html(html);
					app.initColumnToggle();
				} else {
					$('#export_link').html('');
					this.$el.html('');
				}
			}
		},
	});

	app.TableRowView = Backbone.View.extend({
		initialize: function (options) {
			this.model.on("render", this.modelChanged, this);
			this.parentView = options.parentView;
		},
		render: function () {
			return this.model.parseMe();
		},
		modelChanged: function (model, changes) {
			this.parentView.render();
		},
	});
	
	app.TimestampTablesView = Backbone.View.extend({
		initialize: function (options) {
			this.views = [];
			this.listenTo(this.collection, "add", function(model) {
				tableView = new app.TableView({collection: new app.Datasets(), el: "#ic_tsv_timestampdata", template: "tsv_timestampdata_table.html", model_id: 2555});
				this.views.push(tableView);
				tableView.collection.add(new app.TimestampDataSet({model_id: model.get('model_id')}));
			});

			this.listenTo(this.collection, "remove", function(model) {
				var viewToRemove = _.filter(this.views, function(view) {
					return _.where(view.views[0].model, {model_id: model.model_id}).length > 0;
				});
				this.views = _.without(this.views, viewToRemove[0]);
				this.render();
			});
		},
		template: getTemplate("tsv_timestampdata_table.html"),
		el: "#ic_tsv_timestampdata",
		render: function () {
			var html = '';
			if (this.views.length) {
				$('#ic_tsv_download_view_holder').addClass("rendered");
				_.each(this.views, function(views) {
					_.each(views.views, function(view) {
						if (view.model.get('ready')) {
							json = view.render();
							if (json.length) {
								json.model_id = view.model.model_id;
								html += Mustache.to_html(this.template, json);
							}
						}
						this.$el.html(html);
						app.initColumnToggle();
					}, this);
				}, this);
				$('#export_link').html('<a class="export">download</a>');
				$(".export").on('click', function (event) {
					  app.exportTableToCSV.apply(this);
				});
			} else {
				this.$el.html(html);
			}
		},
	});
	
	app.initColumnToggle = function() {
		$('.tsv_export input[type=checkbox]').change(function() {
			var tables = $(this).parents('table');
			tables = tables.add(tables.siblings('table'));//git 'em all!
			var index = $(this).parent().index();
			var cells = tables.find('tr td:nth-child(' + (index + 1) + ')');
			cells = cells.add(tables.find('tr th:nth-child(' + (index + 1) + ')'));//all of them, I tell you!
			if ($(this).is(':checked')) {
				cells.removeClass('no_export');
			} else {
				cells.addClass('no_export');
			}
		});
	}
	
	
	
//maybe this? https://gist.github.com/geddski/1610397
	
	app.tsvHeaderTableView = new app.TableView({collection: new app.Datasets({model: app.HeaderDataSet}), el: "#ic_tsv_headerdata", template: "tsv_headerdata_table.html"});
	
	app.timestampTablesView = new app.TimestampTablesView({collection: new app.TimestampDatasets()});
	
	$('#export_tsv').click(function() {
		if ($('#ic_tsv_download_view_holder').hasClass("rendered")) {
			$('#ic_tsv_download_view_holder').removeClass("rendered");
		} else {
			if (!app.addDatasetToTSV(app.docid)) {
				$('#ic_tsv_download_view_holder').addClass("rendered");
			}
		}
	});
	
	app.addDatasetToTSV = function(hash) {
		if (app.tsvHeaderTableView.collection.findWhere({model_id: hash})) {
			return false;
		}
		app.tsvHeaderTableView.collection.add(new app.HeaderDataSet({model_id: hash}));

		app.timestampTablesView.collection.add(new app.TimestampDataSet({model_id: hash}));
		$('#export_link').html('LOADING');
	};

	app.removeDatasetFromTSV = function(hash) {
		app.tsvHeaderTableView.collection.remove(app.tsvHeaderTableView.collection.where({model_id: hash}));
		app.timestampTablesView.collection.remove(app.timestampTablesView.collection.where({model_id: hash}));
	};
	
	//http://jsfiddle.net/terryyounghk/KPEGU/
	app.exportTableToCSV = function() {
		$(this).unbind("click");
		var zip = new JSZip();

		_.each($('table.tsv_export'), function(table) {
			var rows = $(table).find('tr:has(td)'),

			colDelim = '\t',
			rowDelim = '\r\n',

			// Grab text from table into CSV formatted string
			csv = rows.map(function (i, row) {
				var $row = $(row),
					cols = $row.find('td:not(.no_export)');

				return cols.map(function (j, col) {

					return $(col).text();

				}).get().join(colDelim);

			}).get().join(rowDelim);
				
			if (hash = $(table).attr('data-id')) {
				var filename = "timestamp_data_" + hash + ".tsv";
			} else {
				var filename = "header_data.tsv";
			}

			zip.file("TSV/" + filename, csv);
		});
		csvData = "data:application/zip;base64," + zip.generate({type:"base64"});
			

		$(this)
			.attr({
			'download': 'Informacam_TSV.zip',
				'href': csvData,
		});

		window.setTimeout(function() {
			$(this).click();
			$(this).removeAttr('href');
			$(this).removeAttr('download');
			$(this).click(function() {
				app.exportTableToCSV.apply(this);
			}.bind($(this)));
		}, 300);

    };




});