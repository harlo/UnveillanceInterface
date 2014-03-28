var annex = new UnveillanceAnnex();
var num_views = 1;

function initSetup() {
	// 1. get count of setup views
	var req = {
		req : "num_views",
		view_root : "setup"
	}

	doInnerAjax("frontend", "get", JSONtoURLString(req), function(res) {
		res = JSON.parse(res.responseText);
		
		if(res.result == 200) {
			num_views = res.data;
			
			// 2. set "#uv_setup_step_num" value as count
			$("#uv_setup_step_num").html(num_views);
	
			// 3. loadView 1
			window.location = "#step-1";
		}
	});
}

function setupAnnex() {
	if(!(annex.build())) { return; }
			
	doInnerAjax(
		"init_annex", "post", JSON.stringify(annex.annex_bundle),
		function(json) {
			json = JSON.parse(json['responseText']);

			var tmpl = "init_annex_fail.html";
			var label = "Try Again?";
			var href = "#step-1";
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
			
			if(pos == num_views) { 
				$("#uv_setup_save_or_advance").click(setupAnnex);
			}
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
		initSetup();
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