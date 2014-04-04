Dropzone.autoDiscover = false;
var dropzones = [];

function discoverDropzones(dz_profile, el, onSuccess, onError) {
	if(!el) { el = "#content"; }
	
	file_zones = $(el).find("input:file");
	
	$.each(file_zones, function(idx, item) {
		var param_name = $(item).attr('name');
		var max_files = $(item).attr('rel');
	
		var dz_profile_ = _.clone(dz_profile);
		dz_profile_.paramName = param_name;
		dz_profile_.maxFiles = max_files ? max_files : 1;

		var dropzone_id = param_name.replace(/\./g, "_") + "_dropzone";

		$($(item).parent()).append($(document.createElement('div'))
			.attr('id', dropzone_id)
			.addClass('uv_dropzone_holder'));
		$(item).remove();

		dropzones.push(new UnveillanceDropzone(dropzone_id, dz_profile_, 
			onSuccess, onError));
	});
}

var UnveillanceDropzone = Backbone.Model.extend({
	constructor: function(id, dz_profile, onSuccess, onError) {		
		this.dropzone = new Dropzone("div#" + id, dz_profile);		
		this.dropzone.on("success", onSuccess ? onSuccess : this.onSuccess);
		this.dropzone.on("error", onError ? onError : this.onError);
		this.dropzone.on("addedfile", this.onFileAdded);
	},
	
	onSuccess: function(file, res) {
		console.info("alright!");
		console.info(file);
		console.info(res);
	},
	
	onError: function(files, err, xhr) {
		console.info("error...")
		console.info(err);	
	},
	
	onFileAdded: function(file) {
		console.info("added file: " + file);
	}
});