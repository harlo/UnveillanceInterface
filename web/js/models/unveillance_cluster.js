var UnveillanceCluster = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
		this.idAttribute = "_id";
		
		if(this.get("cluster").file_name) {
			// load data from csv
			var path = ".data/" + this.get("_id") + "/" + this.get("cluster").file_name;
			getFileContent(this, path, function(data) {
				if(data.status == 200) {
					this.set({ cluster_data : data.responseText });	
				}
			});
		}
	},
	build: function(root_el) {
		// build viz in d3
		if(this.get("cluster_data") == null) { return; }
		
		
	}
});