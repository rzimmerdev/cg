import asyncio
import json
from typing import List, Dict

import glm
import websockets
import websocket
import threading

from OpenGL.GL.shaders import ShaderProgram

from src.object import Object, Model
from src.player import Player


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
            await client.send(json.dumps(message))

    # message handler, simply relay the message to all clients
    async def handle_client(self, websocket, path):
        # Add the client to the set of connected clients
        self.clients.add(websocket)
        await self.broadcast({"new_player": str(websocket.id)})
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

    def new_id(self):
        if not self.clients:
            return 0
        return len(self.clients)


class Multiplayer:
    def __init__(self):
        self.client = websocket.WebSocket()
        self.running = threading.Event()

        self.player_id = None

    def connect(self):
        self.client.connect("ws://localhost:8765")
        self.running.set()
        # wait for the server to send the player id
        msg = self.client.recv()
        response = json.loads(msg)
        self.player_id = response["new_player"]
        return self.player_id

    def reconnect(self):
        self.client.connect("ws://localhost:8765")
        self.running.set()

    def disconnect(self):
        self.running.clear()
        self.client.close()

    def update(self, message):
        try:
            self.client.send(json.dumps(message))
        except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError):
            self.running.clear()


class Engine:
    def __init__(self, shader_program: ShaderProgram):
        self.objects: List[Object] = []
        self.player_model = Model(shader_program, "models/monster/monster.obj", "models/monster/monster.jpg")
        self.players: Dict[int, Player] = {}

        self.running = threading.Event()

        self.conn = Multiplayer()

    def add_objects(self, obj):
        if isinstance(obj, list):
            self.objects.extend(obj)
        else:
            self.objects.append(obj)

    def draw(self):
        for obj in self.objects:
            obj.draw()
        for player in self.players.values():
            player.draw()

    def start(self):
        self.running.set()
        thread = threading.Thread(target=self._server_tick)
        thread.start()

    def _server_tick(self):
        # run tick multiplayer asynchronusly
        while self.running.is_set():
            asyncio.run(self.tick_multiplayer())

    async def tick_multiplayer(self):
        if not self.conn.running.is_set() or self.conn.player_id is None:
            return
        try:
            msg = self.conn.client.recv()
        except websocket.WebSocketConnectionClosedException:
            self.conn.reconnect()
            return
        try:
            response = json.loads(json.loads(msg))
        except json.JSONDecodeError:
            return

        for player_id, camera in response.items():
            if player_id not in self.players:
                player = Player(self.player_model)
                self.players[player_id] = player
            x, y, z = camera[:3]
            self.players[player_id].position = glm.vec3(x, y, z)


if __name__ == "__main__":
    server = Server()
    server.start()

    # connect to the server with a client
    conn = Multiplayer()
    conn.connect()

    # send a message to the server
    conn.update("Hello World!")
    server.stop()
