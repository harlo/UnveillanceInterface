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
		var tmpl = "<% _.each(cells, function(val) { %> <td><%= val %></td> <% }); %>";
		
		_.each(this.get('data'), function(csv) {
			var lines = csv.match(/[^\r\n]+/g);
			for(var l in lines) {
				if(l != 0 || csv_idx == 0) {
					var row = _.template(tmpl, { cells : lines[l].split(",").slice(1) });
					$($(this.root_el).children('table')[0]).append(
						$(document.createElement('tr')).html(row)
					);
				}
			}
			
			csv_idx++;
		}, this);
	}
});