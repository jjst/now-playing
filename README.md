# Now Playing!

Find what's currently playing on any radio station.

## API

This server was generated by the [swagger-codegen](https://github.com/swagger-api/swagger-codegen) project. By using the
[OpenAPI-Spec](https://github.com/swagger-api/swagger-core/wiki) from a remote server, you can easily generate a server stub.  This
is an example of building a swagger-enabled Flask server.

This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Python 3.9+

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m api
```

and open your browser to here:

```
http://localhost:8080/api/ui/
```

To launch in dev mode with auto-reload enabled:
```
FLASK_ENV=development python -m api
```

To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

The tests are ran using pytest inside tox. [Pytest-specific test runner
arguments](https://docs.pytest.org/en/6.2.x/usage.html) can be passed as extra positional arguments after `--`. For
example, to run only the tests in the `aggregators` submodule matching the `france-bleu` radio station, run:

```
tox -- aggregators -k france-bleu
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t now-playing .

# starting up a container
docker run -p 8080:8080 now-playing
```
