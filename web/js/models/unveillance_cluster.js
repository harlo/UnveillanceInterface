var UnveillanceCluster = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
		this.idAttribute = "_id";
		
		if(this.get("cluster").file_name) {
			// load data from csv
			var path = ".data/" + this.get("_id") + "/" + this.get("cluster").file_name;
			getFileContent(this, path, function(data) {
				if(data.status == 200) {
					this.get('cluster').data = { raw : data.responseText };
					this.build();
				}
			});
		}
	},
	build: function() {		
		if(!this.get("cluster").data) { return; }
		
		this.get('cluster').data.max_clusters = 3;
		this.get('cluster').data.labels = ["thing_one", "thing_two", "thing_three"];
		this.get('cluster').data.matrix = [
			[1, 1, 0.34], [0.8, 1, 0.38], [0.04, 0.55, 0.89]
		];
		this.get('cluster').data.primary_key = this.has('primary_key') ?
			 this.get('primary_key') : this.get('cluster').data.labels[1];
			 
		this.set('viz', new UVColoredCluster(this));
	}
});