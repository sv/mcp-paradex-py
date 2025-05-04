import sys

from mcp.server.fastmcp.server import FastMCP
from workers import DurableObject

sys.path.insert(0, "/session/metadata/vendor")
sys.path.insert(0, "/session/metadata")


class FastMCPServer(DurableObject):
    def __init__(self, ctx, env, mcp: FastMCP):
        self.ctx = ctx
        self.env = env
        self.mcp = mcp
        app = mcp.sse_app()
        from exceptions import HTTPException, http_exception
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware

        app.add_exception_handler(HTTPException, http_exception)
        app.add_middleware(
            CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
        )
        self.app = app

    async def call(self, request):
        import asgi

        return await asgi.fetch(self.app, request, self.env, self.ctx)


async def on_fetch(request, env):
    id = env.ns.idFromName("example")
    obj = env.ns.get(id)
    return await obj.call(request)
