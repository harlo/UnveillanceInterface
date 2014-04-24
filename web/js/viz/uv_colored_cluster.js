var UVColoredCluster = Backbone.Model.extend({
	constructor: function(ctx) {		
		this.dims = {
			width : $(ctx.get('root_el')).width(),
			height: $(ctx.get('root_el')).height(),
			max_clusters : ctx.get('cluster').data.matrix.length,
			duration : 750,
			cluster_padding : 6
		};
		
		this.svg = d3.select(ctx.get('root_el')).append("svg:svg")
			.attr({
				'width' : this.dims.width,
				'height' : this.dims.height
			});
		
		this.clusters = this.svg.selectAll("circle")
			.data(ctx.get('cluster').data.matrix)
			.enter()
				.append("svg:circle")
					.attr({
						"cy" : 90,
						"cx" : 160,
						"r" : 30
					});
			
		this.dims.colors = d3.scale.category10().domain(d3.range(this.dims.max_clusters));
		
		console.info(this.clusters);
		
	}
});

function draw() {
	
	/*
	var nodes = d3.range(uv_cc.get('data').matrix.length).map(function() {
		var i = 0;	// should be index
		var r = 14;	// should pass an r value
		var o = Math.cos(i / uv_cc.dims.max_clusters * 2 * Math.PI) * 300;
		var d  = {
			cluster: i,
			radius: r,
			x: o + uv_cc.dims.width / 2 + Math.random(),
			y: o + uv_cc.dims.height / 2 + Math.random()
		};
		
		if(!uv_cc.clusters[i] || (r > uv_cc.clusters[i].radius)) {
			uv_cc.clusters[i] = d;
		}
		
		return d;
	});
	
	var force = d3.layout.force()
		.nodes(nodes)
		.size([uv_cc.dims.width, uv_cc.dims.height])
		.gravity(0.02)
		.charge(0)
		.on("tick", tick)
		.start();
	
	var node = uv_cc.svg.selectAll("circle").data(nodes);
	node.enter().append("svg:circle")
		.style("fill", function(d_point) { return uv_cc.color(d_point.cluster); })
	
	node.transition()
		.duration(uv_cc.dims.duration)
		.delay(function(d, i) { return i * 5; })
		.attrTween("r", function(d) {
			var i = d3.interpolate(0, d.radius);
			return function(t) { return d.radius = i(t); };
		});	
	*/	
}