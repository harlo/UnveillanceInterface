var UnveillanceCSV = UnveillanceViz.extend({
	constructor: function() {
		UnveillanceViz.prototype.constructor.apply(this, arguments);
		if(this.invalid) { return; }
		
		$(this.svg[0]).remove();
		delete this.svg;
		
		$(this.root_el).css({
			'width' : this.dims.width,
			'height' : '60%'
		});
		
		var csv_idx = 0;
		_.each(this.get('data'), function(csv) {
			var lines = csv.match(/[^\r\n]+/g);
			console.info(lines);
			for(var l in lines) {
				if(l != 0 || csv_idx == 0) {
					$(this.root_el).append($(document.createElement('p')).html(lines[l]));
				}
			}
			
			csv_idx++;
		}, this);
	}
});