import asyncio
# BEGIN: ed8c6549bwf9
from typing import Dict, Any, Optional
import websockets

"""
For server accepting clients implementer.

Basic server public interface:

def close() -> None: - shutdowns the server
event connection(client: Any) - triggered when a client connects

Basic client public interface:

def send(data: Any, binary: bool = False) -> None: - sends data to client
event close() - triggered when a client closes
event message(data: Any, isBinary: bool) - triggered when data is received
"""

DEFAULT_PORT = 9099

class WSServer:
	def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
		self.port = options.get("port", DEFAULT_PORT) if options else DEFAULT_PORT
		self.clients = set()

	async def handle_client(self, websocket: Any, path: str) -> None:
		self.clients.add(websocket)
		print(f"Server on port '{self.port}': client connected")

		try:
			async for message in websocket:
				# Trigger message event
				self.on_message(message, False)
		finally:
			self.clients.remove(websocket)
			print(f"Server on port '{self.port}': client disconnected")

	def on_message(self, message: Any, is_binary: bool) -> None:
		# Trigger message event
		asyncio.ensure_future(self.message(message, is_binary))
		
		pass


	def send(self, data: Any, binary: bool = False) -> None:
		for client in self.clients:
			asyncio.ensure_future(client.send(data))

	def close(self) -> None:
		for client in self.clients:
			client.close()

	async def start(self) -> None:
		async with websockets.serve(self.handle_client, "localhost", self.port):
			print(f"Server on port '{self.port}': started listening")
			await asyncio.Future()  # Keep the server running

def get_server(name: str, options: Optional[Dict[str, Any]] = None) -> Any:
	if name == "ws":
		return WSServer(options)
	raise ValueError(f"Unsupported server type '{name}'")


