var UVColoredCluster = UnveillanceViz.extend({
	constructor: function() {
		UnveillanceViz.prototype.constructor.apply(this, arguments);
		if(this.invalid) { return; }	
		
		
		
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