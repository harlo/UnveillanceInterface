Dropzone.autoDiscover = false;
var dropzones = [];

function discoverDropzones(dz_profile, el, onSuccess, onError, onFileAdded) {
	if(!el) { el = "#content"; }
	
	file_zones = $(el).find("input:file");
	
	$.each(file_zones, function(idx, item) {
		var param_name = $(item).attr('name');
		var max_files = $(item).attr('rel');
	
		var dz_profile_ = _.clone(dz_profile);
		dz_profile_.paramName = param_name;
		dz_profile_.maxFiles = max_files ? max_files : 1;
		dz_profile.uploadMultiple = true;

		var dropzone_id = param_name.replace(/\./g, "_") + "_dropzone";
		var mandatory = $(item).hasClass('uv_mandatory');

		$($(item).parent()).append($(document.createElement('div'))
			.attr({ 'id' : dropzone_id, 'name' : param_name })
			.addClass('uv_dropzone_holder' + (mandatory ? ' uv_mandatory_dz' : "")));
		$(item).remove();

		dropzones.push(new UnveillanceDropzone(dropzone_id, dz_profile_, 
			onSuccess, onError, onFileAdded));
	});
}

var UnveillanceDropzone = Backbone.Model.extend({
	constructor: function(id, dz_profile, onSuccess, onError, onFileAdded) {		
		this.dropzone = new Dropzone("div#" + id, dz_profile);

		this.dropzone.on("success", onSuccess ? onSuccess : this.onSuccess);
		this.dropzone.on("error", onError ? onError : this.onError);
		this.dropzone.on("addedfile", onFileAdded ? onFileAdded : this.onFileAdded);
		this.dropzone.on("sending", this.onSending);
	},
	
	onSending: function(file, xhr, form_data) {
		console.info("renaming? " + file.name);
		form_data.append(file.name, file);
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
		console.info("added file:");
		console.info(file);
	}
});