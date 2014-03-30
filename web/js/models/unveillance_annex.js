var UnveillanceAnnex = Backbone.Model.extend({
	constructor: function() {
		this.values_holder = "#uv_annex_values_holder";
		
		this.uuid = null;
		this.assets = [];
		this.buildSteps = [this.buildLocalRemote];
		
		var d = new Date();
		this.batch_root = MD5(BATCH_SALT + d.getTime());
	},
	
	parseFields: function(annex_bundle) {
		var values = $(this.values_holder).find("input");
		if(values.length == 0) { return false; }
		
		for(var a=0; a<values.length; a++) {
			var field = values[a];

			$($(field).siblings(".uv_error_msg")[0]).css('visibility','hidden');
			if($(field).hasClass('uv_invalid')) {
				$(field).removeClass('uv_invalid');
			}
		
			if(!(validateFormField($(field), $(this.values_holder)))) { return false; }
			if($(field).hasClass('uv_confirm')) { continue; }
		
			if(!annex_bundle) { annex_bundle = this.annex_bundle; }
			annex_bundle[$(field).attr('name')] = $(field).val();
		}
		
		return true;
	},
	
	buildLocalRemote: function() {
		var annex_bundle = { batch_root : this.batch_root };

		if(this.parseFields(annex_bundle)) {
			this.annex_bundle = annex_bundle;
			return true;
		}
		
		return false;
	},
	
	build: function(step) {
		console.info("ANNEX BUILD");		
		return this.buildSteps[step - 1].call(this);
	},
	
	validate: function() {
		return false;
	}
});