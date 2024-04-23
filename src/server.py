import asyncio
import websockets


connected_clients = set()

async def handle_client(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # message is {"key": "value"}
            pass
    finally:
        connected_clients.remove(websocket)

async def broadcast(message):
    # Send a message to all connected clients
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

async def start_server():
    async with websockets.serve(handle_client, "localhost", 8765):
        print("WebSocket server started.")
        await asyncio.Future()  # Keep the server running indefinitely

asyncio.run(start_server())