function initSync() {
	
	addNewTask();
}

function addNewTask() {
	insertTemplate(
		"new_synctask.html",
		null,
		"#uv_sync_new_holder",
		function() {
			discoverDropzones(
				{ url: ("/init_synctask/") },
				"#uv_sync_new_holder",
				onSynctaskFileSubmitted
			);
		}
	);
}

function onSynctaskFileSubmitted(file, res) {
	var synctask = new UnveillanceSyncTask();
	
	synctask.synctask_bundle['unveillance.uvscript.alias'] = file.name;
	synctask.synctask_bundle['unveillance.uvscript.local_path'] =
		res.data.addedFiles[0][file.name];
	
	$("#uv_synctask_commit").click(function() { synctask.build(); });
}

(function($) {
	var sync_sammy = $.sammy(function() {
		
	});
	
	$(function() {
		sync_sammy.run();
		initSync();
	});
})(jQuery);