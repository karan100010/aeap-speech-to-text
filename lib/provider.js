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

const { Writable } = require('stream');
const speech = require('@google-cloud/speech');
const axios = require('axios');   

/*
 * For speech provider implementer.
 *
 * Basic Provider public interface:
 *
 * function setConfig(config) - sets configuration used by recognize stream
 * function start(config) - starts the recognize stream
 * function restart(config) - restarts the recognize stream
 * function end() - stops recognize and writable stream
 * function write(data) - writes data to the writable stream
 * event result(result) - triggered when a result is received from provider
 * field results[] - cache of received results (oldest to newest)
 *
 * Basic result object public interface:
 *
 *   result = {
 *     text: <the recognized string value>
 *     score: <percent based accuracy/confidence score>
 *   };
 */

/*
 * Google Speech API:
 *     https://googleapis.dev/nodejs/speech/latest/
 *
 * Google infinite streaming speech example:
 *    https://cloud.google.com/speech-to-text/docs/samples/speech-transcribe-infinite-streaming
 *
 * Nodejs stream API:
 *    https://nodejs.org/api/stream.html
 */
// const encoding = 'Encoding of the audio file, e.g. LINEAR16';
// const sampleRateHertz = 16000;
// const languageCode = 'BCP-47 language code with regional subtags, e.g. en-US';
// const limit = 10000; // ms - set to low number for demo purposes

const DEFAULT_ENCODING = "MULAW";
const DEFAULT_SAMPLE_RATE = 8000;
const DEFAULT_LANGUAGE = "en-US";
const DEFAULT_RESTART_TIME = 10; // in seconds
const DEFAULT_MAX_RESULTS = 100;

/**
 * @class GoogleProvider.
 *
 * Start, restart, and stop Google speech to text recognition. Results are
 * emitted via a "result" event that is passed the following object:
 *
 * result = {
 *   text: <the recognized string value>
 *   score: <percent based accuracy/confidence score>
 * };
 *
 * @extends Writable
 */
class GoogleProvider extends Writable {

	

	/**
	 * Creates an instance of a Google provider stream.
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
		// Initialize the client
		
		
	}

	_construct(callback) {
	
	}

	_write(chunk, encoding, callback) { 
		// create an array chunks to store the chunk
		if (!this.chunks) {
			this.chunks = [];
		}
		// push the chunk to the chunks array
		this.chunks.push(chunk);
	
				
			// close the client connection
			this.end();

	}
 _writev() {
	// set chunks for 7 seconds from when the first chunk is received
	// send the chunks to the provider
	// close the client connection
	 new Promise(resolve => setTimeout(resolve, 5000));
		// combine all buffers in chunks array into single buffer
		this.chunks = Buffer.concat(this.chunks);
		let req = { "data": this.chunks };
		// send chunks to provider
		const url2 = 'http://192.168.56.1:5000/convert';
		axios.post(url2, req)
			.then(response => {
				console.log(response.data);
				callback();
			});
		this.end();
	
		}
	_final(callback) {
		const url = 'http://localhost:5005/convert';
		
		//combine all buffers in chunks array into single buffer
		this.chunks = Buffer.concat(this.chunks);
		let req= {"data": this.chunks}

		axios.post(url, req)
			.then(response => {
				console.log(response.data);
				callback();
			})
			.catch(error => {
				// Handle error if needed
				callback(error);
			});
			//close client connection
			this.end();

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
			

			update.encodingencoding = "ulaw";
			update.sampleRateHertz = 8000;
		}

		

			update.languageCode = "en-US";
		

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

		const request = {
			config,
			interimResults: true,
		};

		// this.recognizeStream ={}

			
		// 			let result = {
		// 				text: "hello mr kara",
		// 				score: Math.round(100),
		// 			};

		// 			console.debug("GoogleProvider: result: " + JSON.stringify(result));
		// 			console.debug(result);
		// 			this.emit('result', result);

		// 			this.results.push(result);

					if (this.restartTimeout) {
						/*
						 * Google's speech engine may stop transcribing after a while,
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

		// if (!this.recognizeStream) {
		// 	return;
		// }

		// this.cork(); // Buffer any incoming data

		// this.recognizeStream.end();
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
	if (name == "google") {
		return new GoogleProvider(options);
	}

	throw new Error("Unsupported speech provider '" + name + "'");
}

module.exports = {
	getProvider,
}

