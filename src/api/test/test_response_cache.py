from api.response_cache import ResponseCache
from base import stations

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


def test_set_uses_expire_at_if_provided():
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.getset = MagicMock(return_value=None)
    expiry = datetime.now() + timedelta(seconds=20)
    response_cache.set(station, response, expire_at=expiry)
    # FIXME: recipe for a transient failure if test runs slowly...
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=19)


def test_set_uses_expire_in_if_provided():
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.getset = MagicMock(return_value=None)
    response_cache.set(station, response, expire_in=20)
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=20)


def test_set_raises_valueerror_if_expire_in_and_expire_at_provided():
    with pytest.raises(ValueError):
        response_cache.set(station, response, expire_in=20, expire_at=datetime.now())


def test_set_uses_default_ttl_if_no_response_hash():
    response_cache.redis_client = MagicMock()
    response_cache.redis_client.getset = MagicMock(return_value=None)
    response_cache.set(station, response)
    response_cache.redis_client.getset.assert_called_with('response-hash:fr/radiomeuh', xxhash.xxh32_digest(response))
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=1)


def test_set_uses_default_ttl_if_response_unchanged():
    response_cache.redis_client = MagicMock()
    hashed_response = xxhash.xxh32_digest(response)
    response_cache.redis_client.getset = MagicMock(return_value=hashed_response)
    response_cache.set(station, response)
    response_cache.redis_client.getset.assert_called_with('response-hash:fr/radiomeuh', xxhash.xxh32_digest(response))
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=1)


def test_set_uses_ttl_if_changed_if_response_changed():
    response_cache.redis_client = MagicMock()
    hashed_response = xxhash.xxh32_digest('old-response')
    response_cache.redis_client.getset = MagicMock(return_value=hashed_response)
    response_cache.set(station, response)
    response_cache.redis_client.getset.assert_called_with('response-hash:fr/radiomeuh', xxhash.xxh32_digest(response))
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=5)
