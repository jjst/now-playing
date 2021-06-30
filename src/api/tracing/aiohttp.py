from aiohttp.web import middleware
from opentelemetry import trace

USER_AGENT = 'User-Agent'


@middleware
async def middleware(request, handler):
    route = request.match_info.route
    if route.resource:
        span_name = f"{route.method} {route.resource.canonical}"
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute('span.kind', 'server')
            span.set_attribute('http.route', route.resource.canonical)
            span.set_attribute('http.host', request.host)
            span.set_attribute('http.method', route.method)
            span.set_attribute('http.target', request.rel_url)
            if USER_AGENT in request.headers:
                span.set_attribute('http.user_agent', request.headers[USER_AGENT])
            resp = await handler(request)
            span.set_attribute('http.status_code', resp.status)
        return resp
    else:
        return await handler(request)


def instrument_aiohttp_app(app):
    if middleware not in app.middlewares:
        app.middlewares.append(middleware)
