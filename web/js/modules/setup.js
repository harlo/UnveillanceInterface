var annex = new UnveillanceAnnex();
var num_views = 0;

$(document).ready(function() {
	// 1. init sammy
	(function($) {
		var setup_sammy = $.sammy(function() {
			this.get("#save", function(context) {
				annex.build();
				doInnerAjax(
					"init_annex", "post", JSON.stringify(annex.annex_bundle),
					function(json) {
						console.info(json);

						var tmpl = "init_annex_fail.html";
						var label = "Try Again?";
						var href = "#step-1';
						var m_data = null;
						
						if(json['result'] == 200) { 
							tmpl = "init_annex_success.html"; 
							label = "OK!";
							href = "/";
							m_data = json['data'];
						}

						insertTemplate(
							tmpl, m_data, "#uv_setup_view_holder",
							function() {
								$("#uv_setup_save_or_advance")
									.html(label)
									.attr('href', href);	
							}
						);
					}
				);
			});
			
			this.get('#step-:pos', function(context) {
				var pos = this.params['pos'];				// position in url
				insertTemplate(
					("init_annex_step_" + pos + ".html"),	// tmpl
					null,									// mustache data
					"#uv_setup_view_holder",				// append_root
					function() {							// on_complete
						discoverDropzones(
							{ url: ("/post_batch/" + annex.batch_root + "/") },
							"#uv_setup_view_holder"
						);
						
						var label = (pos == num_views ? "Save" : "Next");
						var href = (pos == num_views ? "#save" : ("#step-" + (pos + 1)));

						$("#uv_setup_save_or_advance")
							.html(label)
							.attr('href', href);
					},
					"/web/layout/views/setup/"				// static_root
				);
			});
		});
		
		$(function() {
			setup_sammy.run();
		});
	})(jQuery);
	
	// 2. get count of setup views
	var req = {
		req : "num_views",
		view_root : "setup"
	}
	
	doInnerAjax("frontend", "post", toURLString(req), function(res) {
		if(res.result == 200) {
			num_views = res.data.num_views;
			
			// 3. set "#uv_wizard_step_num" value as count
			$("#uv_setup_step_num").html(num_views);
			
			// 4. loadView 0
			window.location = "#step-1";
		}
	});
});	


	/*
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
	*/