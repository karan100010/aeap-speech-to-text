# FILEPATH: /c:/Users/karan/aeap-speech-to-text/lib/provider.py
# BEGIN: ed8c6549bwf9
DEFAULT_ENCODING = "MULAW"
DEFAULT_SAMPLE_RATE = 8000
DEFAULT_LANGUAGE = "en-US"
DEFAULT_RESTART_TIME = 10  # in seconds
DEFAULT_MAX_RESULTS = 100

class GoogleProvider:
	encodings = {
		"ulaw": "MULAW",
		"slin16": "LINEAR16",
		"opus": "OGG Opus"
	}

	languages = [
		"en-US"
	]

	def __init__(self, options=None):
		self.config = {
			"encoding": DEFAULT_ENCODING,
			"sampleRateHertz": DEFAULT_SAMPLE_RATE,
			"languageCode": DEFAULT_LANGUAGE
		}
		self.restartTimer = None
		self.restartTimeout = options.get("restartTime", DEFAULT_RESTART_TIME) if options else DEFAULT_RESTART_TIME
		self.maxResults = options.get("maxResults", DEFAULT_MAX_RESULTS) if options else DEFAULT_MAX_RESULTS
		self.results = []
		self.recognizeStream = None

	def _construct(self, callback):
		self.client = speech.SpeechClient()
		callback()

	def _write(self, chunk, encoding, callback):
		if self.recognizeStream:
			self.recognizeStream.write(chunk)
		callback()

	def _writev(self, chunks, callback):
		for chunk in chunks:
			self._write(chunk, None, callback)
		callback()

	def _final(self, callback):
		self.stop()
		self.client.close()
		callback()

	def setConfig(self, config):
		if not config:
			return

		update = {}

		if "codec" in config:
			if config["codec"]["name"] not in GoogleProvider.encodings:
				raise Exception("Codec '" + config["codec"]["name"] + "' not supported")
			update["encoding"] = GoogleProvider.encodings[config["codec"]["name"]]
			update["sampleRateHertz"] = config["codec"]["sampleRate"]

		if "language" in config:
			if config["language"] not in GoogleProvider.languages:
				raise Exception("Language '" + config["language"] + "' not supported")
			update["languageCode"] = config["language"]

		self.config.update(update)

	def start(self, config):
		if self.recognizeStream:
			return

		self.setConfig(config)
		config = self.config

		request = {
			"config": config,
			"interimResults": True
		}

		self.recognizeStream = self.client.streaming_recognize(request)
		self.recognizeStream.on("error", lambda e: print("GoogleProvider: " + str(e) + " - ending stream"))
		self.recognizeStream.on("data", lambda response: self._handle_response(response))

		if self.restartTimeout:
			self.restartTimer = Timer(self.restartTimeout, self.restart)
			self.restartTimer.start()

	def stop(self):
		if self.restartTimer:
			self.restartTimer.cancel()
			self.restartTimer = None

		if not self.recognizeStream:
			return

		self.recognizeStream.end()
		self.recognizeStream = None

	def restart(self, config):
		self.stop()
		self.start(config)

	def _handle_response(self, response):
		if response.results and response.results[0].alternatives:
			if response.results[0].alternatives[0].confidence == 0:
				return

			result = {
				"text": response.results[0].alternatives[0].transcript,
				"score": round(response.results[0].alternatives[0].confidence * 100)
			}

			print("GoogleProvider: result: " + str(result))
			self.results.append(result)

			if len(self.results) == self.maxResults:
				self.results.pop(0)

