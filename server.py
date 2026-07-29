import asyncio
import os
import websockets

# Memorizza i client connessi
CLIENTS = set()

async def relay_handler(websocket):
    # Aggiunge il nuovo client alla lista
    CLIENTS.add(websocket)
    try:
        async for message in websocket:
            # Smista il messaggio cifrato a tutti gli altri client connessi
            for client in CLIENTS.copy():
                if client != websocket:
                    try:
                        await client.send(message)
                    except Exception:
                        CLIENTS.remove(client)
    except Exception:
        pass
    finally:
        CLIENTS.remove(websocket)

async def main():
    # Render assegna una porta dinamica tramite la variabile d'ambiente PORT
    port = int(os.environ.get("PORT", 10000))
    async with websockets.serve(relay_handler, "0.0.0.0", port):
        await asyncio.Future()  # Mantiene il server in ascolto perenne

if __name__ == "__main__":
    asyncio.run(main())