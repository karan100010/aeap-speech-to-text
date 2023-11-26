import asyncio
import websockets

async def websocket_listener(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")

start_server = websockets.serve(websocket_listener, 'localhost', 9099)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
