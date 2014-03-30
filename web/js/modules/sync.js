function initSync() {
	//	1. get user's synctasks
	synctask_holder = new UnveillanceSyncTaskHolder();
	
	//	2. add holder for a new task
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
	var synctask_stub = new UnveillanceSyncTask();
	synctask_stub.synctask_bundle.alias = file.name;
	synctask_stub.synctask_bundle.local_path = res.data.addedFiles[0][file.name];
	
	$("#uv_synctask_commit").click(function() { synctask_stub.build(); });
}

(function($) {
	var sync_sammy = $.sammy(function() {
		
	});
	
	$(function() {
		sync_sammy.run();
		initSync();
	});
})(jQuery);