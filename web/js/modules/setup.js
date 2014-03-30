var annex = null;
var num_views = null;

function initSetup() {
	// 1. get count of setup views
	var req = {
		req : "num_views",
		view_root : "setup"
	}

	doInnerAjax("frontend", "get", JSONtoURLString(req), function(res) {
		res = JSON.parse(res.responseText);
		
		if(res.result == 200) {			
			// 2. set "#uv_setup_step_num" value as count
			annex = new UnveillanceAnnex();			
			num_views = res.data;
			
			$("#uv_setup_step_num").html(num_views);
			setTimeout(loadSetupStep(1), 1000);
		}
	});
}

function setupAnnex() {
	if(!(annex.validate())) { return; }
			
	doInnerAjax(
		"init_annex", "post", JSON.stringify(annex.annex_bundle),
		function(json) {
			json = JSON.parse(json['responseText']);

			var tmpl = "init_annex_fail.html";
			var label = "Try Again?";
			var href = "/setup/";
			var m_data = json['data'] ? json['data'] : null;
			
			if(json['result'] == 200) { 
				tmpl = "init_annex_success.html"; 
				label = "OK!";
				href = "/";
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
}

function loadSetupStep(pos) {
	$("#uv_setup_save_or_advance").unbind("click");
	
	if(pos == 1 && num_views == null) {
		initSetup();
		return;
	}
	
	insertTemplate(
		("init_annex_step_" + pos + ".html"),	// tmpl
		null,									// mustache data
		"#uv_setup_view_holder",				// append_root
		function() {							// on_complete
			$("#uv_setup_current_step").html(pos);
			discoverDropzones(
				{ url: ("/post_batch/" + annex.batch_root + "/") },
				"#uv_setup_view_holder"
			);
			
			var label = (pos == num_views ? "Save" : "Next");
			var href = null;

			if(pos == num_views) { 
				href = "#save";
				$("#uv_setup_save_or_advance").click(setupAnnex);
			} else {
				$("#uv_setup_save_or_advance").click(function() {
					if(annex.build(Number(pos))) {
						href = ("#step-" + (Number(pos) + 1));
						$("#uv_setup_save_or_advance").attr('href', href);
					}
				});
			}
			
			$("#uv_setup_save_or_advance")
				.html(label)
				.attr('href', href);
		},
		"/web/layout/views/setup/"				// static_root
	);
}

(function($) {
	var setup_sammy = $.sammy(function() {
		this.get("#save", function(context) {
			$("#uv_setup_save_or_advance").unbind("click");
		});
		
		this.get('#step-:pos', function(context) {
			loadSetupStep(this.params['pos']);	// position in url
		});
	});
	
	$(function() {
		setup_sammy.run();
		window.location = "#step-1";
	});
})(jQuery);

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