
import sys

from codecs import Codec
from languags import Languages
from provider import getProvider
from sever import getServer
from dispatch import dispatch

argv = {
	"port": 9099
}

codecs = Codec(argv)
languages = Languages(argv)
server = getServer("ws", argv)

def on_connection(client):
	dispatch({
		"codecs": codecs,
		"languages": languages,
		"transport": client,
		"provider": getProvider("google", argv)
	})

server.on("connection", on_connection)

def on_sigint():
	server.close()
	sys.exit(0)

def on_sigterm():
	server.close()
	sys.exit(0)

signal.signal(signal.SIGINT, on_sigint)
signal.signal(signal.SIGTERM, on_sigterm)

server.start(argv["port"])



