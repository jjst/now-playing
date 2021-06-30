from aiohttp.web import middleware
from opentelemetry import trace


@middleware
async def middleware(request, handler):
    route = request.match_info.route
    tracer = trace.get_tracer(__name__)
    span_name = f"{route.method} {route.resource.canonical}"
    with tracer.start_as_current_span(span_name) as span:
        resp = await handler(request)
    return resp


def instrument_aiohttp_app(app):
    if middleware not in app.middlewares:
        app.middlewares.append(middleware)
