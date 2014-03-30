var UnveillanceSyncTaskHolder = Backbone.Model.extend({
	constructor: function() {
		
		var d = new Date();
		this.batch_root = MD5(BATCH_SALT + d.getTime());
	}
});

var UnveillanceSyncTask = Backbone.Model.extend({
	constructor: function() {
		this.synctask_bundle = {};
	},
	
	build: function() {		
		var input_holder = $("#uv_synctask_add_holder");
		var values = [];
		_.each(["input", "select"], function(tag) {
			$.each(input_holder.find(tag), function(idx, item) { values.push(item); });
		});
		
		console.info(values);
		if(values.length == 0) { return false; }
		
		for(var a=0; a<values.length; a++) {
			var field = values[a];
			console.info($(field));
			
			$($(field).siblings(".uv_error_msg")[0]).css('visibility','hidden');
			if($(field).hasClass('uv_invalid')) {
				$(field).removeClass('uv_invalid');
			}
			
			if(!(validateFormField($(field), $("#uv_synctask_add_holder")))) { 
				return false; 
			}
			
			if($(field).hasClass('uv_confirm')) { continue; }
			
			this.synctask_bundle[$(field).attr('name')] = $(field).val();
		}
		
		this.commit();
		return true;
	},
	
	commit: function() {
		console.info(this.synctask_bundle);
		doInnerAjax(
			"init_synctask", "post", JSON.stringify(this.synctask_bundle),
			function(json) {
				json = JSON.parse(json['responseText']);
				
				if(json['result'] == 200) {
					// cleanup this
				}
			}
		);
	}
});