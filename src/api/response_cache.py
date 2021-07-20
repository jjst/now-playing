import aioredis
import asyncio
import xxhash
import datetime
from typing import Optional, Tuple
from opentelemetry import trace

from base.utils import monkeypatch_method
from base.config import settings
from base.stations import RadioStationInfo

response_prefix = "response"
response_hash_prefix = "response-hash"

tracer = trace.get_tracer(__name__)


@monkeypatch_method(aioredis.Redis)
def set(self, name, value,
        ex=None, px=None, nx=False, xx=False, keepttl=False, get=False):
    """
    Monkey-patch redis-py's set() to add support for Redis 6.2's 'GET'
    parameter.
    """
    pieces = [name, value]
    if ex is not None:
        pieces.append('EX')
        if isinstance(ex, datetime.timedelta):
            ex = int(ex.total_seconds())
        pieces.append(ex)
    if px is not None:
        pieces.append('PX')
        if isinstance(px, datetime.timedelta):
            px = int(px.total_seconds() * 1000)
        pieces.append(px)

    if nx:
        pieces.append('NX')
    if xx:
        pieces.append('XX')

    if keepttl:
        pieces.append('KEEPTTL')

    if get:
        pieces.append('GET')

    return self.execute_command('SET', *pieces)


def key_for(station, prefix):
    return f"{prefix}:{station.station_id()}"


class CacheError(Exception):
    pass


class ResponseCache():
    def __init__(self, settings=settings):
        self.redis_client = aioredis.from_url(settings.redis.url, **settings.redis.args)
        self.default_ttl_seconds = settings.response_cache.default_ttl_seconds
        self.default_ttl_seconds_if_changed = settings.response_cache.default_ttl_seconds_if_changed

    async def get(self, station: RadioStationInfo) -> Optional[Tuple[str, int]]:
        with tracer.start_as_current_span("get_cached_response") as span:
            try:
                key = key_for(station, 'response')
                (response, ttl) = await asyncio.gather(
                    self.redis_client.get(key),
                    self.redis_client.ttl(key)
                )
            except aioredis.exceptions.ConnectionError as e:
                raise CacheError("Error connecting to Redis. Cannot get cached response.") from e
            else:
                span.set_attribute('cache_hit', (response is not None))
                span.set_attribute('ttl', ttl)
                return (response, ttl)

    async def set(self, station: RadioStationInfo, response: str,
                  expire_in: Optional[int] = None, expire_at: Optional[datetime.datetime] = None) -> int:
        with tracer.start_as_current_span("set_cached_response"):
            if expire_in and expire_at:
                raise ValueError("Only one of 'expire_in' or 'expire_at' should be provided as argument")
            current_span = trace.get_current_span()
            new_hashed_response = xxhash.xxh32_digest(response)
            try:
                old_hashed_response = await self.redis_client.set(
                    key_for(station, 'response-hash'),
                    new_hashed_response,
                    ex=self.default_ttl_seconds_if_changed,
                    get=True
                )
            except aioredis.exceptions.ConnectionError as e:
                raise CacheError("Error connecting to Redis. Cannot set cached response.") from e
            if expire_in:
                ttl_seconds = expire_in
            elif expire_at:
                ttl_seconds = max(self.default_ttl_seconds, int((expire_at - datetime.datetime.now()).total_seconds()))
            elif old_hashed_response and new_hashed_response != old_hashed_response:
                ttl_seconds = self.default_ttl_seconds_if_changed
            else:
                ttl_seconds = self.default_ttl_seconds
            current_span.add_event("determine_cached_response_ttl", attributes={'ttl_seconds': ttl_seconds})
            try:
                await self.redis_client.set(key_for(station, 'response'), response, ex=ttl_seconds)
            except aioredis.exceptions.ConnectionError as e:
                raise CacheError("Error connecting to Redis. Cannot set cached response.") from e
            return ttl_seconds
