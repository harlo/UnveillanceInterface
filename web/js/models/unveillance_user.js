var UnveillanceUser = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
		
		try {
			this.set(JSON.parse(localStorage.getItem('user')));
		} catch(err) {
			console.warn(err);
		}
	},
	
	logIn: function(el) {
		var user = {
			username: $($(el).find("input[name=username]")[0]).val(),
			password: $($(el).find("input[name=password]")[0]).val()
		};
	
		doInnerAjax("login", "post", user, function(json) {
			console.info(json);
		
			try {
				json = JSON.parse(json.responseText);
			} catch(err) {
				alert("Could not log in!");
				return;
			}
		
			if(json.result == 200) {
				localStorage.setItem('user', JSON.stringify(json.data));
				window.location = "/";
			} else {
				alert("Could not log you in!");
			}
		});
	},
	
	logOut: function() {
		var user = {};
		
		if($("#uv_logout_with_data").css('display') != "none") {
			user = this.toJSON();
			user.password = $($("#uv_logout_with_data")
				.find("input[name=password]")[0]).val();
		}
	
		doInnerAjax("logout", "post", user, function(json) {
			console.info(json);
		
			try {
				json = JSON.parse(json.responseText);
			} catch(err) {
				alert("Could not log out!");
				return;
			}
		
			if(json.result == 200) {
				localStorage.clear();
				window.location = "/";
			} else {
				alert("Could not log you out!");
			}
		});
	}
});