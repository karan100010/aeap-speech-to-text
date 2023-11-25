import json
import uuid
/*
 *  Copyright 2022 Sangoma Technologies Corporation
 *  Kevin Harwell <kharwell@sangoma.com>
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

const { randomUUID } = require('crypto');

function handleError(e, msg) {
	msg.error_msg = e.message;
}

function sendMessage(speech, msg) {
	speech.transport.send(JSON.stringify(msg), { binary: false });
}

function sendSetRequest(speech, params) {
	request = {
		request: "set",
		id: randomUUID(),
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
# FILEPATH: /c:/Users/karan/aeap-speech-to-text/lib/dispatcher.py
# BEGIN: ed8c6549bwf9

def handle_error(e, msg):
	msg["error_msg"] = str(e)

def send_message(speech, msg):
	speech["transport"].send(json.dumps(msg))

def send_set_request(speech, params):
	request = {
		"request": "set",
		"id": str(uuid.uuid4()),
		"params": params
	}
	send_message(speech, request)

def handle_get_request(speech, request, response):
	if "params" not in request:
		raise ValueError("Missing request parameters")

	params = {}

	for p in request["params"]:
		if p == "codec":
			params["codecs"] = speech["codecs"]["selected"]
		elif p == "language":
			params["language"] = speech["languages"]["selected"]
		elif p == "results":
			params["results"] = speech["provider"]["results"][:]
		else:
			print(f"Ignoring unsupported parameter '{p}' in '{request['request']}' request")

	response["params"] = params

def handle_set_request(speech, request, response):
	if "codecs" not in request or "params" not in request:
		raise ValueError("Missing request parameters")

	codec = None
	params = {}

	if "codecs" in request:
		codec = speech["codecs"]["first"](request["codecs"])

	for k, v in request["params"].items():
		if k == "language":
			params["language"] = speech["languages"]["first"](v)
		else:
			print(f"Ignoring unsupported parameter '{k}' in '{request['request']}' request")

	if codec:
		response["codecs"] = [speech["codecs"]["selected"] := codec]

	if params:
		if "language" in params:
			speech["languages"]["selected"] = params["language"]

		response["params"] = params

	if response["codecs"] or response["params"]:
		# Start/Restart provider if any parameters were changed
		speech["provider"]["restart"]({
			"codec": speech["codecs"]["selected"],
			"language": speech["languages"]["selected"]
		})

def handle_request(speech, msg):
	handlers = {
		"get": handle_get_request,
		"set": handle_set_request,
		"setup": handle_set_request
	}

	response = {"response": msg["request"], "id": msg["id"]}

	try:
		handlers[msg["request"]](speech, msg, response)
	except Exception as e:
		handle_error(e, response)

	return response

def handle_response(speech, msg):
	return None  # TODO

def dispatch(speech):
	def on_close():
		speech["provider"]["end"]()

	def on_message(data, is_binary):
		if is_binary:
			speech["provider"]["write"](data)
			return

		print("message: " + data)

		msg = json.loads(data)

		if "request" in msg:
			msg = handle_request(speech, msg)
		elif "response" in msg:
			msg = handle_response(speech, msg)
		else:
			msg = None

		if msg:
			send_message(speech, msg)

	speech["transport"]["on"]("close", on_close)
	speech["transport"]["on"]("message", on_message)

	def on_result(result):
		send_set_request(speech, {"results": [result]})

	speech["provider"]["on"]("result", on_result)

# Usage example:
speech = {
	"codecs": {
		"selected": None,
		"first": lambda codecs: codecs[0]
	},
	"languages": {
		"selected": None,
		"first": lambda languages: languages[0]
	},
	"transport": None,
	"provider": None
}

dispatch(speech)
# END: ed8c6549bwf9
