var tree, diagonal, uv_it;

var UVIndentedTree = UnveillanceViz.extend({
	constructor: function() {
		UnveillanceViz.prototype.constructor.apply(this, arguments);
		if(this.invalid) { return; }

		uv_it = this;
		this.dims.margin = {
			top : 10,
			right : 10,
			bottom : 10,
			left : 10
		};
		
		this.dims.tabs = {
			width : $(this.root_el).width() * 0.9,
			height: 20,
			count: 0
		};
		
		this.dims.duration = 400;
		
		this.set({'data' : this.buildDataTree()});
		this.dims.height = this.dims.tabs.height * this.dims.tabs.count;
		
		tree = d3.layout.tree().size([this.dims.height, this.dims.width/2]);
		diagonal = d3.svg.diagonal().projection(function(d) { return [d.y, d.x]; });
		
		this.svg.attr("height", this.dims.height);
		
		
		this.svg.append("svg:g")
			.attr({
				'transform' : "translate(" + this.dims.margin.top + 
					"," + this.dims.margin.left + ")"
			});
		
		update(this.root_d3 = {
			children : this.get('data'),
			node_name : "data_root",
			x0 : 0,
			y0 : 0
		});
		
		
	},
	buildDataTree: function(data) {
		var data_tree = [];
		if(!data) { data = this.get("data"); }
		
		for(var key in data) {
			var child_data = {};		
  		
  		    if (data[key] instanceof Array|| data[key] instanceof Object) {
				child_data.node_name = key;
				child_data.children = this.buildDataTree(data[key]);	
  			} else {
				if (data instanceof Array) {
					child_data.node_name =  data[key];
				} else {
					child_data.node_name = key + " : " + JSON.stringify(data[key]);
				} 			
  			}
  			
  			data_tree.push(child_data);
  			this.dims.tabs.count += 1;
  		}
  		
  		return data_tree;
	}
});

function getColor(d_point) {
	return d_point._children ? "#3182bd" : d_point.children ? "#c6dbef" : "#fd8d3c";
}

function toggleNode(d_point) {
	if(d_point.children) {
		d_point._children = d_point.children;
		d_point.children = null;
	} else {
		d_point.children = d_point._children;
		d_point._children = null;
	}
	
	update(d_point);
}

function update(source) {	
	var i = 0;
	
	// Compute the flattened node list. TODO use d3.layout.hierarchy.
	var nodes = tree.nodes(uv_it.root_d3);

	// Compute the "layout".
	nodes.forEach(function(n, i) {
		n.x = i * uv_it.dims.tabs.height;
	});

	// Update the nodes
	var node = uv_it.svg.selectAll("g.uv_it_node")
	  .data(nodes, function(d) { return d.id || (d.id = ++i); });

	var nodeEnter = node.enter().append("svg:g")
		.attr("class", "uv_it_node")
		.attr("transform", function(d) { 
			return "translate(" + source.y0 + "," + source.x0 + ")"; 
		})
		.style("opacity", 1e-6);

	// Enter any new nodes at the parent's previous position.
	nodeEnter.append("svg:rect")
		.attr("y", -uv_it.dims.tabs.height / 2)
		.attr("height", uv_it.dims.tabs.height)
		.attr("width", uv_it.dims.width * .5)
		.attr("rx", 6)
		.attr("ry", 6)
		.style("fill", getColor)
		.on("click", toggleNode);

	nodeEnter.append("svg:text")
		.attr("dy", 3.5)
		.attr("dx", 5.5)
		.text(function(d) { 
			return d.node_name;
		});

	// Transition nodes to their new position.
	nodeEnter.transition()
		.duration(uv_it.dims.duration)
		.attr("transform", function(d) { 
			return "translate(" + d.y + "," + d.x + ")"; 
		})
		.style("opacity", 1);

	node.transition()
	  	.duration(uv_it.dims.duration)
		.attr("transform", function(d) { 
			return "translate(" + d.y + "," + d.x + ")"; 
		})
		.style("opacity", 1)
		.select("rect").style("fill", getColor);

	// Transition exiting nodes to the parent's new position.
	node.exit().transition()
		.duration(uv_it.dims.duration)
		.attr("transform", function(d) {
			return "translate(" + source.y + "," + source.x + ")"; 
		})
		.style("opacity", 1e-6)
		.remove();

	var link = uv_it.svg.selectAll("path.uv_it_link")
		.data(tree.links(nodes), function(d) { return d.target.id; });

	// Enter any new links at the parent's previous position.
	link.enter().insert("svg:path", "g")
	  	.attr("class", "uv_it_link")
		.attr("d", function(d) {
			var o = {x: source.x0, y: source.y0};
			return diagonal({source: o, target: o});
		})
		.transition()
		.duration(uv_it.dims.duration)
		.attr("d", diagonal);

	// Transition links to their new position.
	link.transition()
		.duration(uv_it.dims.duration)
		.attr("d", diagonal);

	// Transition exiting nodes to the parent's new position.
	link.exit().transition()
		.duration(uv_it.dims.duration)
		.attr("d", function(d) {
			var o = {x: source.x, y: source.y};
			return diagonal({source: o, target: o});
		})
		.remove();

	nodes.forEach(function(d) {
		d.x0 = d.x;
		d.y0 = d.y;
	});
}