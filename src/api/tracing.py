import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.launcher import configure_opentelemetry
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware


import os


def configure_console_tracer():
    provider = TracerProvider()
    processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


def configure_tracer(app):
    if 'LS_SERVICE_NAME' not in os.environ or 'LS_ACCESS_TOKEN' not in os.environ:
        if 'LS_SERVICE_NAME' not in os.environ:
            logging.warning("'LS_SERVICE_NAME' undefined, cannot configure lightstep")
        if 'LS_ACCESS_TOKEN' not in os.environ:
            logging.warning("'LS_ACCESS_TOKEN' undefined, cannot configure lightstep")
        logging.warning("Cannot configure lightstep, using console tracer provider")
        configure_console_tracer()
    else:
        service_name = os.environ['LS_SERVICE_NAME']
        lightstep_access_token = os.environ['LS_ACCESS_TOKEN']
        configure_opentelemetry(
          service_name=service_name,
          access_token=lightstep_access_token,
        )
    add_instrumentation(app)
    logging.info("Tracing is enabled.")


def add_instrumentation(app):
    # FIXME: doesn't work since aiohttp isn't ASGI-compatible
    # app.app = OpenTelemetryMiddleware(app.app)
    RequestsInstrumentor().instrument(span_callback=set_cached_response_tag)
    URLLibInstrumentor().instrument()
    BotocoreInstrumentor().instrument()
    return app


def set_cached_response_tag(span, result):
    try:
        cached_response = result.from_cache
    except KeyError:
        cached_response = False
    span.set_attribute('http.cached_response', cached_response)
