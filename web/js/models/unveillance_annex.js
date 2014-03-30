var UnveillanceAnnex = Backbone.Model.extend({
	constructor: function() {
		this.values_holder = "#uv_annex_values_holder";
		
		this.uuid = null;
		this.assets = [];
		this.buildSteps = [this.buildLocalRemote];
		
		var d = new Date();
		this.batch_root = MD5(BATCH_SALT + d.getTime());
	},
	
	buildLocalRemote: function() {
		var values = $(this.values_holder).find("input");
		if(values.length == 0) { return false; }
		
		var annex_bundle = { batch_root : this.batch_root };
			
		for(var a=0; a<values.length; a++) {
			var field = values[a];

			$($(field).siblings(".uv_error_msg")[0]).css('visibility','hidden');
			if($(field).hasClass('uv_invalid')) {
				$(field).removeClass('uv_invalid');
			}
		
			if(!(validateFormField($(field), $(this.values_holder)))) { return false; }
			if($(field).hasClass('uv_confirm')) { continue; }
		
			annex_bundle[$(field).attr('name')] = $(field).val();
		}
			
		this.annex_bundle = annex_bundle;
		return true;
	},
	
	build: function(step) {
		console.info("ANNEX BUILD");		
		return this.buildSteps[step - 1].call(this);
	},
	
	validate: function() {
		return false;
	}
});