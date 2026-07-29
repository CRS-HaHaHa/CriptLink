import asyncio
import os
import http
import websockets

CLIENTS = set()

# Intercetta i controlli di Render (Health Checks) e risponde 200 OK
async def process_request(path, request_headers):
    # Se arriva una richiesta HTTP normale (es. HEAD o GET di Render senza upgrade a WebSocket)
    if "Upgrade" not in request_headers or request_headers.get("Upgrade").lower() != "websocket":
        return http.HTTPStatus.OK, [("Content-Type", "text/plain")], b"OK\n"
    # Se è una richiesta WebSocket valida, lascia che websockets gestisca l'handshake
    return None

async def relay_handler(websocket):
    CLIENTS.add(websocket)
    try:
        async for message in websocket:
            for client in CLIENTS.copy():
                if client != websocket:
                    try:
                        await client.send(message)
                    except Exception:
                        CLIENTS.remove(client)
    except Exception:
        pass
    finally:
        CLIENTS.discard(websocket)

async def main():
    port = int(os.environ.get("PORT", 10000))
    # Passiamo process_request al server
    async with websockets.serve(relay_handler, "0.0.0.0", port, process_request=process_request):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
