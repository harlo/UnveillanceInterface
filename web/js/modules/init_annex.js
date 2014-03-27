var annex = new UnveillanceAnnex();

$(document).ready(function() {
	discoverDropzones({ maxFiles: 5, url: ("/post_batch/" + annex.batch_root + "/") }, "#uv_form_dz_holder");
	discoverDropzones({ maxFiles: 1, url: ("/post_batch/" + annex.batch_root + "/") });
	
	$("#uv_sync_chooser").change(function(e) {
		var sync_type = $("#uv_sync_chooser").children("option:selected")[0];
		
		if($(sync_type).val() != "null") {
			insertTemplate($(sync_type).val() + "_creds.html", 
				null, "#uv_sync_cred_holder", function() {
					discoverDropzones({ 
						maxFiles: 1, 
						url: "/post_batch/" + annex.batch_root + "/" 
					}, "#uv_sync_cred_holder");
				}
			);
		}
	});
});