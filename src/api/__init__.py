import connexion

from api import encoder
from api.tracing import configure_tracer


app = connexion.FlaskApp(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('spec.yaml', arguments={'title': 'Now Playing API'})

configure_tracer(app)
