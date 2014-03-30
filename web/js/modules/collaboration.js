(function($) {
	var collab_sammy = $.sammy(function() {
		this.get("#init", function(context) {
			console.info("INITING GOOGLE FO SHO");
		});
	});
	
	$(function() {
		collab_sammy.run();
	});
})(jQuery);