
const { randomUUID } = require('uuid');

function handleError(e, msg) {
	msg.error_msg = e.message;
}

function sendMessage(speech, msg) {
	speech.transport.send(JSON.stringify(msg), { binary: false });
}

function sendSetRequest(speech, params) {
	request = {
		request: "set",
		id: randomUUID.v4(),
		params,
	};

	sendMessage(speech, request);
}

function handleGetRequest(speech, request, response) {
	if (!request.params) {
		throw new Error("Missing request parameters");
	}

	let params = {};

	for (let p of request.params) {
		if (p === "codec") {
			params.codecs = speech.codecs.selected;
		} else if (p === "language") {
			params.language = speech.languages.selected;
		} else if (p === "results") {
			params.results = speech.provider.results.splice(0);
		} else {
			console.warn("Ignoring unsupported parameter '" + k + "' in '" +
				request.request + "' request");
		}
	}

	response.params = params;
}

function handleSetRequest(speech, request, response) {
	if (!request.codecs || !request.params) {
		throw new Error("Missing request parameters");
	}

	/*
	 * It's all or nothing for an incoming set request. So first validate
	 * all values, then set newly selected, and lastly set the response.
	 */
	let codec = null;
	let params = {};

	if (request.codecs) {
		codec = speech.codecs.first(request.codecs);
	}

	for (let [k, v] of Object.entries(request.params)) {
		if (k == "language") {
			params.language = speech.languages.first(v);
		} else {
			console.warn("Ignoring unsupported parameter '" + k + "' in '" +
				request.request + "' request");
		}
	}

	if (codec) {
		response.codecs = [speech.codecs.selected = codec];
	}

	if (Object.keys(params).length) {
		if (params.language) {
			speech.languages.selected = params.language;
		}

		response.params = params;
	}

	if (response.codecs || response.params) {
		// Start/Restart provider if any parameters were changed
		speech.provider.restart({
			codec: speech.codecs.selected,
			language: speech.languages.selected,
		});
	}
}

function handleRequest(speech, msg) {
	const handlers = {
		"get": handleGetRequest,
		"set": handleSetRequest,
		"setup": handleSetRequest,
	};

	let response = { response: msg.request, id: msg.id };

	try {
		handlers[msg.request](speech, msg, response);
	} catch (e) {
		handleError(e, response);
	}

	return response;
}

function handleResponse(speech, msg) {
	return null; // TODO
}

/**
 * Manages configuration, communication, messaging, and data between
 * a connected transport and speech provider.
 *
 * @param {Object} speech - speech object
 * @param {Object} speech.codecs - allowed codec(s)
 * @param {Object} speech.languages - allowed language(s)
 * @param {Object} speech.transport - remote connection
 * @param {Object} speech.provider - speech provider
 */
function dispatch(speech) {

	speech.transport.on("close", () => {
		speech.provider.end();
	});

	speech.transport.on("message", (data, isBinary) => {
		if (isBinary) {
			speech.provider.write(data);
			return;
		}

		console.debug("message: " + data);

		let msg = JSON.parse(data);

		if (msg.hasOwnProperty('request')) {
			msg = handleRequest(speech, msg);
		} else if (msg.hasOwnProperty('response')) {
			msg = handleResponse(speech, msg);
		} else {
			msg = null;
		}

		if (msg) {
			sendMessage(speech, msg);
		}
	});

	speech.provider.on("result", (result) => {
		sendSetRequest(speech, { results: [ result ] });
	});
}

module.exports = {
	dispatch,
}