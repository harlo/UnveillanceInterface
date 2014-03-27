var UnveillanceAnnex = Backbone.Model.extend({
	constructor: function() {
		this.values_holder = "#uv_annex_values_holder";
		
		this.uuid = null;
		this.assets = [];
		
		var d = new Date();
		this.batch_root = MD5(BATCH_SALT + d.getTime());
	},
	
	initAnnex: function() {
		var values = $(this.values_holder).find("input");
		annex_bundle = { batch_root : this.batch_root };
		
		$.each(values, function(idx, item) {
			console.info($(item).attr('name') + " : " + $(item).attr('type'));
			if($(item).val() != "") {
				console.info($(item).val());
				
				annex_bundle[$(item).attr('name')] = $(item).val();
			}
		});
		
		doInnerAjax("init_annex", "post", JSON.stringify(annex_bundle), function(json) {
			console.info(json);
		});
	}
});