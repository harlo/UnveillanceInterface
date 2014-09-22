var UnveillanceNotifier = Backbone.Model.extend({
	constructor: function() {
		Backbone.Model.apply(this, arguments);

		var web_socket = new SockJS("http://localhost:" + UV.API_PORT + "/", ['websocket']);
		web_socket.onopen = this.onSocketOpen;
		web_socket.onclose = this.onSocketClose;
		web_socket.onmessage = this.onSocketMessage;

		this.set('web_socket', web_socket);
	},
	connect: function() {

	},
	disconnect: function() {
		this.get('web_socket').close();
	},
	onSocketOpen: function() {
		console.info("ON SOCKET OPEN!");
		console.info(arguments);

		try {
			onSocketOpen(arguments);
		} catch(err) { console.warn(err); }
	},
	onSocketClose: function() {
		console.info("ON SOCKET CLOSE!");
		console.info(arguments);

		try {
			onSocketClose(arguments);
		} catch(err) { console.warn(err); }
	},
	onSocketMessage: function(message) {
		console.info("ON SOCKET MESSAGE!");
		console.info(arguments);

		try {
			onSocketMessage(arguments);
		} catch(err) { console.warn(err); }		
	}
});