var UnveillanceAnnex = Backbone.Model.extend({
	constructor: function() {
		this.values_holder = "#uv_annex_values_holder";
		
		this.uuid = null;
		this.assets = [];
		this.buildSteps = [this.buildLocalRemote];
		
		var d = new Date();
		this.batch_root = MD5(UV.web.BATCH_SALT + d.getTime());
	},
	
	parseFields: function(annex_bundle) {
		var values = [];
		var tags = ["input", "select", "div.uv_mandatory_dz"];
		for(var v=0; v<tags.length; v++) {
			$.each($(this.values_holder).find(tags[v]), function(idx, item) {
				values.push(item);
			});
		}
		
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
			if(!$(field).hasClass('uv_mandatory_dz')) {
				annex_bundle[$(field).attr('name')] = $(field).val();
			}
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
	}
});