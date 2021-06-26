import logging
from opentelemetry.launcher import configure_opentelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

import os


def configure_tracer(app):
    if 'LS_SERVICE_NAME' not in os.environ:
        logging.warning("'LS_SERVICE_NAME' undefined, cannot configure tracing")
        return
    if 'LS_ACCESS_TOKEN' not in os.environ:
        logging.warning("'LS_ACCESS_TOKEN' undefined, cannot configure tracing")
        return

    service_name = os.environ['LS_SERVICE_NAME']
    lightstep_access_token = os.environ['LS_ACCESS_TOKEN']
    configure_opentelemetry(
      service_name=service_name,
      access_token=lightstep_access_token,
    )
    add_instrumentation(app)
    logging.info("Tracing is enabled.")


def add_instrumentation(app):
    FlaskInstrumentor().instrument_app(app.app)
    RequestsInstrumentor().instrument(span_callback=set_cached_response_tag)
    URLLibInstrumentor().instrument()
    BotocoreInstrumentor().instrument()


def set_cached_response_tag(span, result):
    try:
        cached_response = result.from_cache
    except KeyError:
        cached_response = False
    span.set_attribute('http.cached_response', cached_response)
