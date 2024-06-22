import asyncio
import json

import websockets
import websocket
import threading

"""
A classe multiplayer ainda não está funcional. 
A ideia é que o servidor possa receber mensagens de vários clientes eventualmente.
"""


class Server:
    def __init__(self):
        self.clients = set()
        self.server = None
        self.loop = asyncio.get_event_loop()
        self._thread = None
        self.running = asyncio.Event()

    async def register(self, ws):
        self.clients.add(ws)

    async def unregister(self, ws):
        self.clients.remove(ws)

    async def broadcast(self, message, exclude=None):
        for client in self.clients - {exclude}:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                await self.unregister(client)

    # message handler, simply relay the message to all clients
    async def handle_client(self, websocket, path):
        # Add the client to the set of connected clients
        await self.register(websocket)
        await self.broadcast({"new_player": str(websocket.id)})
        try:
            async for message in websocket:
                # broadcast the message to all clients
                await self.broadcast(message)
        finally:
            # Remove the client from the set of connected clients
            if websocket in self.clients:
                await self.unregister(websocket)

    async def _serve(self):
        self.server = await websockets.serve(self.handle_client, "localhost", 8765)
        self.running.set()

        try:
            while self.running.is_set():
                await asyncio.sleep(1)
        except (asyncio.CancelledError, KeyboardInterrupt):
            pass

    def start(self):
        # run in thread
        self._thread = threading.Thread(target=self.loop.run_until_complete, args=(self._serve(),))
        self._thread.start()

        while not self.running.is_set():
            pass
        print("Server started")

    def stop(self):
        self.server.close()
        self.running.clear()
        self._thread.join()

    def new_id(self):
        if not self.clients:
            return 0
        return len(self.clients)


class Multiplayer:
    def __init__(self, host="localhost", port=8765):
        self.client = websocket.WebSocket()
        self.host = host
        self.port = port
        self.player_id = None

    def connect(self):
        self.client.connect(f"ws://{self.host}:{self.port}")
        msg = self.client.recv()
        response = json.loads(msg)
        self.player_id = response["new_player"]
        return self.player_id

    def reconnect(self):
        self.client.connect(f"ws://{self.host}:{self.port}")

    def disconnect(self):
        self.client.close()

    @property
    def connected(self):
        return self.client.connected

    def update(self, message):
        try:
            self.client.send(json.dumps(message))
        except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError):
            self.reconnect()
            self.update(message)


if __name__ == "__main__":
    server = Server()
    server.start()

    # connect to the server with a client
    conn = Multiplayer()
    player_id = conn.connect()
    print(player_id)

    # send a message to the server
    conn.update("Hello World!")
    conn.disconnect()

    server.stop()
