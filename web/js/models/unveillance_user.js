var UnveillanceUser = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);
		
		try {
			this.set(JSON.parse(localStorage.getItem('user')));
		} catch(err) {
			console.warn("COULD NOT LOAD USER DATA");
			console.warn(err);
		}
	},
	
	save: function() {
		try {
			localStorage.setItem('user', JSON.stringify(this.toJSON()));
			return true;
		} catch(err) {
			console.warn("COULD NOT SAVE USER DATA");
			console.warn(err);
		}

		return false;
	},
	commit: function() {
		if(this.save()) {
			// push self to server
			return true;
		}

		return false;
	},
	getDirective: function(d_name, create_if_none) {
		var directive;

		try {
			directive = _.filter(this.get('session_log'), function(d) {
				return _.keys(d)[0] == d_name;
			})[0];
		} catch(err) { console.warn(err); }

		if(!directive && (create_if_none && create_if_none !== false)) {
			directive = setDirective(d_name, create_if_none);
		}
		
		return directive;
	},
	setDirective: function(d_name, create_with) {
		if(!create_with) { create_with = []; }

		var directive;
		try {
			directive = _.indexOf(this.get('session_log'), this.getDirective(d_name, false));
		} catch(err) { console.warn(err); }

		if(directive >= 0) {
			console.info("directive replaced!");
			this.get('session_log')[directive][d_name] = create_with;
		} else {
			console.info("directive created!");
			this.get('session_log').push(_.object([d_name],[create_with]));
		}
		
		return this.getDirective(d_name, false);
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
		var user = { username : this.get('username') };
		
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
				window.history.back();
				window.location.reload();
			} else {
				alert("Could not log you out!");
			}
		});
	}
});