import connexion

from api import encoder


app = connexion.FlaskApp(__name__, specification_dir='./swagger/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'Now Playing API'})
