$.ajax({
	url: "/web/conf.json",
	dataType: "json",
	method: "get",
	complete: function(res) {	
		if(res.status == 200) {			
			UV = JSON.parse(res.responseText);
			UV.SEARCH_FACETS = [
				"Mime Type",
				"With Asset",
				"Date Created"
			];
			UV.FACET_VALUES = [
				{
					category : "Mime Type",
					values: _.map(UV.MIME_TYPES, function(mime_type) {
						return {
							value : mime_type,
							label: mime_type
						};
					})
				},
				{
					category: "With Asset",
					values: _.map(_.pairs(UV.ASSET_TAGS), function(asset_tag) {
						return {
							value: asset_tag[1],
							label: asset_tag[1]
						};
					})
				}
			];
			UV.SPLAT_PARAM_IGNORE = [
				"splat", "escapeHTML", 
				"h", "toHash", "toHTML", 
				"keys", "has", "join", "log", "toString"
			];
		
			try {
				
				$(document).trigger("onConfLoadedEvent");
			} catch(err) {
				console.info(err);
			}
		}
	}
});