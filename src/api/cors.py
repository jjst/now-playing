from aiohttp.web import middleware
from aiohttp.web import json_response


@middleware
async def cors_middleware(request, handler):
    """
    FIXME: naive, insecure, allow-all implementation of CORS
    """
    route = request.match_info.route
    resp = json_response({"result": "ok"})
    if route and route.method == 'OPTIONS':
        try:
            resp.headers["Access-Control-Allow-Headers"] = request.headers["Access-Control-Request-Headers"]
        except KeyError:
            pass
        try:
            resp.headers["Access-Control-Allow-Methods"] = request.headers["Access-Control-Request-Method"]
        except KeyError:
            pass
        return resp
    else:
        resp = await handler(request)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp


def install_cors_middleware(app):
    if cors_middleware not in app.middlewares:
        app.middlewares.append(cors_middleware)
