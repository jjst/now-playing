# coding: utf-8
import aioredis
import connexion
import logging
import pytest

from api.response_cache import ResponseCache
from base import stations
from base.config import settings


def create_app(loop):
    logging.getLogger('connexion.operation').setLevel('ERROR')
    app = connexion.AioHttpApp(__name__, specification_dir='../openapi/')
    app.add_api('spec.yaml')
    return app.app


@pytest.fixture
async def redis_client():
    redis_client = aioredis.from_url(settings.redis.url, **settings.redis.args)
    await redis_client.flushall()
    return redis_client


async def test_get_station_by_station_id(test_client):
    client = await test_client(create_app)
    response = await client.get('/api/stations/{namespace}/{slug}'.format(namespace='fr', slug='radiomeuh'))
    assert response.status == 200


async def test_get_now_playing_by_station_id(test_client):
    client = await test_client(create_app)
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='radiomeuh'))
    assert response.status == 200


async def test_get_now_playing_by_station_id_uses_cache(test_client, redis_client):
    client = await test_client(create_app)
    await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='radiomeuh'))
    response_cache = ResponseCache()
    station = stations.get('fr', 'radiomeuh')
    cached_response = response_cache.get(station)
    assert cached_response is not None


async def test_get_now_playing_by_station_id_returns_cache_control_header_for_fresh_response(test_client, redis_client):
    client = await test_client(create_app)
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='fip'))
    assert 'Cache-Control' in response.headers


@pytest.mark.xfail(reason="not yet implemented")
async def test_get_now_playing_by_station_id_returns_cache_control_header_for_cached_response(test_client, redis_client):
    client = await test_client(create_app)
    _ = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='fip'))
    response = await client.get('/api/stations/{namespace}/{slug}/now-playing'.format(namespace='fr', slug='fip'))
    assert 'Cache-Control' in response.headers
