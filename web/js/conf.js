$.ajax({
	url: "/web/conf.json",
	dataType: "json",
	method: "get",
	complete: function(res) {	
		if(res.status == 200) {			
			UV = JSON.parse(res.responseText);
		
			try {
				$(document).on("confLoadedEvent", onConfLoadedEvent);
			} catch(err) {
				console.info(err);
			}
		}
	}
});