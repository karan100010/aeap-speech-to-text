import json
import uuid

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
