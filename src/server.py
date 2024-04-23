import asyncio
import websockets
import websocket
import threading


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
            await client.send(message)

    # message handler, simply relay the message to all clients
    async def handle_client(self, websocket, path):
        # Add the client to the set of connected clients
        self.clients.add(websocket)
        try:
            async for message in websocket:
                # broadcast the message to all clients
                await self.broadcast(message)
        finally:
            # Remove the client from the set of connected clients when they disconnect
            self.clients.remove(websocket)

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


class Multiplayer:
    def __init__(self):
        self.client = websocket.WebSocket()
        self.running = threading.Event()

    def connect(self):
        self.client.connect("ws://localhost:8765")
        self.running.set()

    def disconnect(self):
        self.running.clear()
        self.client.close()

    def update(self, message):
        self.client.send(message)

    def tick(self):
        print(self.client.recv())

    def process(self):
        while self.running.is_set():
            self.tick()


if __name__ == "__main__":
    server = Server()
    server.start()

    # connect to the server with a client
    conn = Multiplayer()
    conn.connect()

    # send a message to the server
    conn.update("Hello World!")
    conn.tick()

    server.stop()
