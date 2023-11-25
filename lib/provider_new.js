const axios = require('axios');

/**
 * @class DockerProvider.
 *
 * Start, restart, and stop Docker speech to text recognition. Results are
 * emitted via a "result" event that is passed the following object:
 *
 * result = {
 *   text: <the recognized string value>
 *   score: <percent based accuracy/confidence score>
 * };
 *
 * @extends Writable
 */
class DockerProvider extends Writable {

	/* Mapped encodings supported by Docker */
	static encodings = {
		ulaw: "MULAW",
		slin16: "LINEAR16",
		opus: "OGG Opus",
	};

	/* Languages this provider supports  */
	static languages = [
		"en-US",
	];

	/**
	 * Creates an instance of a Docker provider stream.
	 *
	 * @param {Object} [options] - provider specific options
	 * @param {Object} [options.restartTime=10] - If specified auto-restart
	 *     recognition stream after a given interval (in seconds)
	 * @param {Object} [options.maxResults=100] - The maximum number of results
	 *     to cache before results are dropped (oldest dropped first)
	 */
	constructor(options) {
		super();

		this.config = {
			encoding: DEFAULT_ENCODING,
			sampleRateHertz: DEFAULT_SAMPLE_RATE,
			languageCode: DEFAULT_LANGUAGE,
		};

		this.restartTimer = null;
		this.restartTimeout = options && options.restartTime || DEFAULT_RESTART_TIME;
		this.maxResults = options && options.maxResults || DEFAULT_MAX_RESULTS;

		this.results = [];
		this.recognizeStream = null;
	}

	_construct(callback) {
		callback();
	}

	_write(chunk, encoding, callback) {
		if (this.recognizeStream) {
			// Send audio chunk to the Docker container running on port 5000
			axios.post('http://localhost:5000/recognize', chunk)
				.then(response => {
					const result = response.data;
					console.debug("DockerProvider: result: " + JSON.stringify(result));
					this.emit('result', result);

					if (this.results.length == this.maxResults) {
						this.results.shift();
					}

					this.results.push(result);
				})
				.catch(error => {
					console.error("DockerProvider: " + error + " - ending stream");
					this.end();
				});
		}

		callback();
	}

	_writev(chunks, callback) {
		for (let chunk in chunks) {
			this._write(chunk, null, callback);
		}

		callback();
	}

	_final(callback) {
		this.stop();

		callback();
	}

	/**
	 * Sets the configuration to use on the recognition stream.
	 *
	 * @param {Object} [config] - configuration to set
	 * @param {Object} [config.codec] - the codec to map to an encoding
	 * @param {string} [config.language] - the language to use
	 */
	setConfig(config) {
		if (!config) {
			return;
		}

		let update = {};

		if (config.codec) {
			if (!(config.codec.name in DockerProvider.encodings)) {
				throw new Error("Codec '" + config.codec.name + " 'not supported");
			}

			update.encodingencoding = DockerProvider.encodings[config.codec.name];
			update.sampleRateHertz = config.codec.sampleRate;
		}

		if (config.language) {
			if (!DockerProvider.languages.includes(config.language)) {
				throw new Error("Language '" + config.language + " 'not supported");
			}

			update.languageCode = config.language;
		}

		this.config = {...this.config, ...update};
	}

	/**
	 * Starts the recognition stream.
	 *
	 * @param {Object} [config] - configuration to use
	 * @param {Object} [config.codec] - the codec to map to an encoding
	 * @param {string} [config.language] - the language to use
	 */
	start(config) {
		if (this.recognizeStream) {
			return; // Already started
		}

		this.setConfig(config);
		config = this.config;

		this.recognizeStream = true;

		if (this.restartTimeout) {
			/*
			 * Docker container may stop transcribing after a while,
			 * so restart the recognize stream after a specified interval.
			 */
			this.restartTimer = setTimeout(() => this.restart(), this.restartTimeout * 1000);
		}

		while (this.writableCorked) {
			this.uncork();
		}
	}

	/**
	 * Stops the recognition stream.
	 */
	stop() {
		if (this.restartTimer) {
			clearInterval(this.restartTimer);
			this.restartTimer = null;
		}

		this.recognizeStream = null;
	}

	/**
	 * Restarts the recognition stream.
	 *
	 * @param {Object} [config] - configuration to use
	 * @param {Object} [config.codec] - the codec to map to an encoding
	 * @param {string} [config.language] - the language to use
	 */
	restart(config) {
		this.stop();
		this.start(config);
	}
}

/**
 * Gets a speech provider
 *
 * @param {string} name - A speech provider name
 * @param {Object} options - Provider specific options
 * @return A speech provider.
 */
function getProvider(name, options) {
	if (name == "docker") {
		return new DockerProvider(options);
	}}