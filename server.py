import os
from aiohttp import web

CLIENTS = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    CLIENTS.add(ws)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                for client in CLIENTS.copy():
                    if client != ws:
                        try:
                            await client.send_str(msg.data)
                        except Exception:
                            CLIENTS.discard(client)
    finally:
        CLIENTS.discard(ws)

    return ws

app = web.Application()

# add_get gestisce sia GET (WebSocket upgrade) sia HEAD (Render Health Check)
app.router.add_get('/', websocket_handler)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host='0.0.0.0', port=port)
