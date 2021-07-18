from api.response_cache import ResponseCache, CacheError
from base import stations

import aioredis
from unittest.mock import Mock, MagicMock
import xxhash
from datetime import datetime, timedelta
import pytest

settings = Mock(
    redis=Mock(url='redis://localhost:6379/0', args={}),
    response_cache=Mock(default_ttl_seconds=1, default_ttl_seconds_if_changed=5)
)
response_cache = ResponseCache(settings)

response = 'test-response'

station = stations.get('fr', 'radiomeuh')


async def test_set_raises_cacheerror_if_cant_connect_to_redis():
    err = aioredis.exceptions.ConnectionError("Can't connect")
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.set = MagicMock(side_effect=err)
    with pytest.raises(CacheError):
        await response_cache.set(station, response)


async def test_get_raises_cacheerror_if_cant_connect_to_redis():
    err = aioredis.exceptions.ConnectionError("Can't connect")
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.get = MagicMock(side_effect=err)
    with pytest.raises(CacheError):
        await response_cache.get(station)


async def test_set_uses_expire_at_if_provided():
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.set = MagicMock(return_value=None)
    expiry = datetime.now() + timedelta(seconds=20)
    await response_cache.set(station, response, expire_at=expiry)
    # FIXME: recipe for a transient failure if test runs slowly...
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=19)


async def test_set_uses_expire_in_if_provided():
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.set = MagicMock(return_value=None)
    await response_cache.set(station, response, expire_in=20)
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=20)


async def test_set_raises_valueerror_if_expire_in_and_expire_at_provided():
    with pytest.raises(ValueError):
        await response_cache.set(station, response, expire_in=20, expire_at=datetime.now())


async def test_set_uses_default_ttl_if_no_response_hash():
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.set = MagicMock(return_value=None)
    await response_cache.set(station, response)
    response_cache.redis_client.set.assert_any_call(
        'response-hash:fr/radiomeuh', xxhash.xxh32_digest(response), ex=5, get=True
    )
    response_cache.redis_client.set.assert_any_call(
        'response:fr/radiomeuh', 'test-response', ex=1
    )


async def test_set_uses_default_ttl_if_response_unchanged():
    response_cache.redis_client = MagicMock()
    hashed_response = xxhash.xxh32_digest(response)
    response_cache.redis_client.set = MagicMock(return_value=hashed_response)
    await response_cache.set(station, response)
    response_cache.redis_client.set.assert_any_call(
        'response-hash:fr/radiomeuh', xxhash.xxh32_digest(response), ex=5, get=True
    )
    response_cache.redis_client.set.assert_any_call(
        'response:fr/radiomeuh', 'test-response', ex=1
    )


async def test_set_uses_ttl_if_changed_if_response_changed():
    response_cache.redis_client = MagicMock()
    hashed_response = xxhash.xxh32_digest('old-response')
    response_cache.redis_client.set = MagicMock(return_value=hashed_response)
    await response_cache.set(station, response)
    response_cache.redis_client.set.assert_any_call(
        'response-hash:fr/radiomeuh', xxhash.xxh32_digest(response), ex=5, get=True
    )
    response_cache.redis_client.set.assert_any_call(
        'response:fr/radiomeuh', 'test-response', ex=5
    )
