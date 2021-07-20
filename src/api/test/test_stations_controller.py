# coding: utf-8
import aioredis
import connexion
import logging
import pytest

from api.response_cache import ResponseCache
from base import stations
from base.config import settings


@pytest.fixture
def app():
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.AioHttpApp(__name__, specification_dir='../openapi/')
    app.add_api('spec.yaml')
    return app.app


@pytest.fixture
async def redis_client(loop):
    # huge hack
    # normally we should use the global app context to initialise and clean the redis connection
    # however, connexion routing doesn't let us access the request and app context.
    # in prod this doesn't currently cause issues, but in tests we use a different asyncio loop for each test
    # and so we leave dangling redis connections bound to old loops.
    import api.controllers.stations_controller as c
    await c.response_cache.redis_client.close()
    c.response_cache = ResponseCache()
    redis_client = aioredis.from_url(settings.redis.url, **settings.redis.args)
    await redis_client.flushall()
    return redis_client


async def test_get_station_by_station_id(loop, app, aiohttp_client):
    client = await aiohttp_client(app)
    response = await client.get('/api/stations/{namespace}/{slug}'.format(namespace='fr', slug='radiomeuh'))
    assert response.status == 200


async def test_get_now_playing_by_station_id(loop, app, aiohttp_client):
    client = await aiohttp_client(app)
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='radiomeuh'))
    assert response.status == 200


async def test_get_now_playing_by_station_id_uses_cache(loop, app, aiohttp_client, redis_client):
    client = await aiohttp_client(app)
    await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='radiomeuh'))
    response_cache = ResponseCache()
    station = stations.get('fr', 'radiomeuh')
    cached_response = await response_cache.get(station)
    assert cached_response is not None


async def test_get_now_playing_by_station_id_returns_cache_control_header_for_fresh_response(loop, app, aiohttp_client, redis_client):
    await redis_client.flushall()
    cache = ResponseCache()
    r = await cache.get(stations.get('fr', 'fip'))
    assert r is None
    client = await aiohttp_client(app)
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='fip'))
    assert 'Cache-Control' in response.headers


@pytest.mark.xfail(reason="not yet implemented")
async def test_get_now_playing_by_station_id_returns_cache_control_header_for_cached_response(loop, app, aiohttp_client, redis_client):
    client = await aiohttp_client(app)
    _ = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='fip'))
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='fip'))
    assert 'Cache-Control' in response.headers
