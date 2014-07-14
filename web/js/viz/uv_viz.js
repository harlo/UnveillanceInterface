var UnveillanceViz = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);

		this.root_el = this.get("root_el");
		this.unset("root_el");
		$(this.root_el).css("clear", "both");
				
		if(!this.has('data') || !this.get('data') || this.get('data').length == 0) {
			$(this.root_el)
				.css('height','auto')
				.append($(document.createElement('p')).html("No data available"));
			
			this.invalid = true;
			return;
		}

		if($(document).find(this.root_el).length == 1) {
			this.setDOMElement();
		}
	},
	setDOMElement: function() {
		this.dims = {
			width: $(this.root_el).width(),
			height: $(this.root_el).height(),
			margin: {
				top: 10,
				right: 10,
				bottom: 10,
				left: 10
			}
		};

		this.svg = d3.select(this.root_el)
			.append("svg:svg")
			.attr({
				"width" : this.dims.width,
				"height" : this.dims.height,
				"class" : "uv_viz"
			});
	},
	
	buildLegend: function(legend_to_use) {
		if(!legend_to_use) { legend_to_use = this.get('legend'); }
		
		var legend = $(document.createElement('div'))
			.attr("class", "uv_legend")
			.css("top", -(this.dims.height));
		
		_.each(legend_to_use, function(l) {
			if(!l.color) { l.color = getRandomColor(); }
			
			var tmpl = _.template(
				'<span class="uv_legend_colorblock" style="background-color:<%= color %>">&nbsp;&nbsp;&nbsp;</span> <%= label %>', l);
			var legend_key = $(document.createElement('p'))
				.html(tmpl);
			
			$(legend).append(legend_key);
		});
		
		$(this.root_el).append(legend);
	},
});

function getRandomColor() {
	var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function drillToKey(obj, key) {
	var val = obj;
	var last_key = key;
	_.each(key.split("."), function(seg) {
		if(val instanceof Array) {
			val = _.each(val, function(v) {
				return v;
			});
		} else {
			val = val[seg];
		}
		last_key = seg;
		
	});
	return [val, last_key];
};