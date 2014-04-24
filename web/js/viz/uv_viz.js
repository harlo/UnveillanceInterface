var UnveillanceViz = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);

		this.root_el = this.get("root_el");
		this.unset("root_el");

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
	}
});