import asyncio
import os
import http
import websockets

CLIENTS = set()

async def process_request(*args, **kwargs):
    """
    Compatibile sia con websockets <12 (path, headers) 
    sia con websockets >=12 (connection, request)
    """
    if len(args) == 2:
        arg1, arg2 = args
        # Nuova firma: (connection, request)
        if hasattr(arg2, 'headers'):
            connection, request = arg1, arg2
            if request.headers.get("Upgrade", "").lower() != "websocket":
                return connection.respond(http.HTTPStatus.OK, "OK\n")
            return None
        # Vecchia firma: (path, headers)
        else:
            path, headers = arg1, arg2
            if headers.get("Upgrade", "").lower() != "websocket":
                return http.HTTPStatus.OK, [("Content-Type", "text/plain")], b"OK\n"
            return None
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
                        CLIENTS.discard(client)
    except Exception:
        pass
    finally:
        CLIENTS.discard(websocket)

async def main():
    port = int(os.environ.get("PORT", 10000))
    async with websockets.serve(relay_handler, "0.0.0.0", port, process_request=process_request):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
