# coding: utf-8
import connexion
import logging

from api.response_cache import ResponseCache
from base import stations


def create_app(loop):
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.AioHttpApp(__name__, specification_dir='../openapi/')
    app.add_api('spec.yaml')
    return app.app


async def test_get_station_by_station_id(test_client):
    client = await test_client(create_app)
    response = await client.get('/api/stations/{namespace}/{slug}'.format(namespace='fr', slug='radiomeuh'))
    assert response.status == 200


async def test_get_now_playing_by_station_id(test_client):
    client = await test_client(create_app)
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='radiomeuh'))
    assert response.status == 200


async def test_get_now_playing_by_station_id_uses_cache(test_client):
    client = await test_client(create_app)
    await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='radiomeuh'))
    response_cache = ResponseCache()
    station = stations.get('fr', 'radiomeuh')
    cached_response = response_cache.get(station)
    assert cached_response is not None
