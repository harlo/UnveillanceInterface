$.ajax({
	url: "/web/conf.json",
	dataType: "json",
	complete: function(res) {
		console.info(res);
		if(res.status == 200) {
			UV = JSON.parse(res.responseText);
		}
	}
});