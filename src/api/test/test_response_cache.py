
from api.response_cache import ResponseCache
from base import stations
from unittest.mock import Mock, MagicMock
import xxhash

settings = Mock(
    redis=Mock(url='redis://localhost:6379/0', args={}),
    response_cache=Mock(default_ttl_seconds=1, default_ttl_seconds_if_changed=5)
)


def test_set_uses_default_ttl_if_response_unchanged():
    station = stations.get('fr', 'radiomeuh')
    response_cache = ResponseCache(settings)
    response_cache.redis_client = MagicMock()
    response = 'test-response'
    hashed_response = xxhash.xxh32_digest(response)
    response_cache.redis_client.getset = MagicMock(return_value=hashed_response)
    response_cache.set(station, response)
    response_cache.redis_client.getset.assert_called_with('response-hash:fr/radiomeuh', xxhash.xxh32_digest(response))
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=1)


def test_set_uses_ttl_if_changed_if_response_changed():
    station = stations.get('fr', 'radiomeuh')
    response_cache = ResponseCache(settings)
    response_cache.redis_client = MagicMock()
    response = 'test-response'
    hashed_response = xxhash.xxh32_digest('old-response')
    response_cache.redis_client.getset = MagicMock(return_value=hashed_response)
    response_cache.set(station, response)
    response_cache.redis_client.getset.assert_called_with('response-hash:fr/radiomeuh', xxhash.xxh32_digest(response))
    response_cache.redis_client.set.assert_called_with('response:fr/radiomeuh', 'test-response', ex=5)
