

/*
 * Copyright 2022 Sangoma Technologies Corporation
 * Kevin Harwell <kharwell@sangoma.com>
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


const { Codecs } = require("./lib/codecs");
const { Languages } = require("./lib/languages");

const { getProvider } = require("./lib/provider");
const { getServer } = require("./lib/server");
const { dispatch } = require("./lib/dispatcher");

const argv = require("yargs/yargs")(process.argv.slice(2))
	.command("$0 [options]", "Start a speech to text server", {
		port: {
			alias: "p",
			desc: "Port to listen on",
			default: 9099,
			type: "number",
			group: "Server",
		},
	})
	.strict()
	.argv;

const codecs = new Codecs(argv);
const languages = new Languages(argv);
const server = getServer("ws", argv);

server.on("connection", (client) => {
	dispatch({
		codecs: codecs,
		languages: languages,
		transport: client,
		provider: getProvider("google", argv),
	});
});

process.on("SIGINT", () => {
	server.close();
	process.exit(0);
});

process.on("SIGTERM", () => {
	server.close();
	process.exit(0);
});