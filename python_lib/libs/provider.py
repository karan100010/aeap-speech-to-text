import speech_recognition as sr

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

		self.recognizeStream = sr.Recognizer()
		self.recognizeStream.pause_threshold = 0.5
		self.recognizeStream.phrase_threshold = 0.3
		self.recognizeStream.non_speaking_duration = 0.2

		self.recognizeStream.on("error", lambda e: print("GoogleProvider: " + str(e) + " - ending stream"))

		with sr.Microphone() as source:
			print("Listening...")
			audio = self.recognizeStream.listen(source)

		try:
			text = self.recognizeStream.recognize_google(audio, language=config["languageCode"])
			print("GoogleProvider: result: " + text)
			result = {
				"text": text,
				"score": 100
			}
			self.results.append(result)

			if len(self.results) == self.maxResults:
				self.results.pop(0)

		except sr.UnknownValueError:
			print("GoogleProvider: Unable to recognize speech")

	def stop(self):
		if self.recognizeStream:
			self.recognizeStream.stop()
			self.recognizeStream = None

	def restart(self, config):
		self.stop()
		self.start(config)

	def _handle_response(self, response):
		pass
