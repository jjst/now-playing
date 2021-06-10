import logging
from opentelemetry.launcher import configure_opentelemetry
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
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
    FlaskInstrumentor().instrument_app(app.app)
    RequestsInstrumentor().instrument()
    logging.info("Tracing is enabled.")
