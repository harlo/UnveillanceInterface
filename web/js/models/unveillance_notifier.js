var UnveillanceNotifier = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);

		/* TODO: this sucks
		var task_channel = UV.TASK_CHANNEL_URL;
		
		if(UV.TASK_CHANNEL_URL.match(/127\.0\.0\.1|localhost/)) {
			// do we have a port on the end?  (if so, get rid of it)

			// recreate with protocol, host, port
			task_channel = task_channel.split(":");
			console.info(window.location.host);

			task_channel = UV.TASK_CHANNEL_URL.replace(/127\.0\.0\.1|localhost/gi, window.location.host).split(':');
			console.info(task_channel);

			task_channel.pop();

			task_channel[0] = window.location.protocol;
			task_channel = task_channel.join('');
		}
		*/

		var task_channel = UV.TASK_CHANNEL_URL;
		var web_socket = new SockJS(task_channel + "/annex_channel", null, { protocols_whitelist : ['websocket']});

		web_socket.onopen = this.onSocketOpen;
		web_socket.onclose = this.onSocketClose;
		web_socket.onmessage = _.bind(this.onSocketMessage, this);

		this.set('web_socket', web_socket);
		this.set('message_map', []);

		window.onbeforeunload = _.bind(this.disconnect, this);
	},
	connect: function() {
		try {
			this.onSocketConnect();
		} catch(err) { console.warn(err); }
	},
	disconnect: function() {
		console.info("DISCONNECTION!");
		this.get('web_socket').close();
	},
	onSocketOpen: function() {},
	onSocketClose: function() {},
	onSocketConnect: function() {},
	onSocketMessage: function(message) {
		_.each(this.get('message_map'), function(func) {			
			try {
				func = _.compose(func);
				func(message['data']);

			} catch(err) { console.warn(err); }	
		});
	}
});