var UnveillanceNotifier = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);

		var web_socket = new SockJS(
			(!UV.TASK_CHANNEL_URL.match(/127\.0\.0\.1|localhost/) ? UV.TASK_CHANNEL_URL : UV.TASK_CHANNEL_URL.replace(/127\.0\.0\.1|localhost/gi, window.location.host)) 
				+ "/annex_channel",
			null, { protocols_whitelist : ['websocket']});

		web_socket.onopen = this.onSocketOpen;
		web_socket.onclose = this.onSocketClose;
		web_socket.onmessage = this.onSocketMessage;

		this.set('web_socket', web_socket);
		window.onbeforeunload = _.bind(this.disconnect, this);
	},
	connect: function() {
		try {
			onSocketConnect();
		} catch(err) { console.warn(err); }
	},
	disconnect: function() {
		console.info("DISCONNECTION!");
		this.get('web_socket').close();
	},
	onSocketOpen: function() {
		try {
			onSocketOpen(arguments);
		} catch(err) { console.warn(err); }
	},
	onSocketClose: function() {
		try {
			onSocketClose(arguments);
		} catch(err) { console.warn(err); }
	},
	onSocketMessage: function(message) {
		try {
			onSocketMessage(arguments);
		} catch(err) { console.warn(err); }		
	}
});