import logging
import redis
import xxhash
from datetime import datetime, timedelta
from typing import Optional

from base.config import settings
from base.stations import RadioStationInfo

response_prefix = "response"
response_hash_prefix = "response-hash"


def key_for(station, prefix):
    return f"{prefix}:{station.station_id()}"


class ResponseCache():
    def __init__(self, settings=settings):
        self.redis_client = redis.from_url(settings.redis.url, **settings.redis.args)
        self.default_ttl_seconds = settings.response_cache.default_ttl_seconds
        self.default_ttl_seconds_if_changed = settings.response_cache.default_ttl_seconds_if_changed

    def get(self, station: RadioStationInfo) -> Optional[str]:
        try:
            return self.redis_client.get(key_for(station, 'response'))
        except redis.exceptions.ConnectionError as e:
            logging.warning("Error connecting to Redis. Server cannot return cached response.")
            logging.exception(e)
            return None

    def set(self, station: RadioStationInfo, response: str, expire_in: Optional[int] = None, expire_at: Optional[datetime] = None):
        new_hashed_response = xxhash.xxh32_digest(response)
        old_hashed_response = self.redis_client.getset(key_for(station, 'response-hash'), new_hashed_response)
        if expire_in:
            ttl_seconds = expire_in
        elif expire_at:
            ttl_seconds = max(self.default_ttl_seconds, int((expire_at - datetime.now()).total_seconds()))
        elif old_hashed_response and new_hashed_response != old_hashed_response:
            ttl_seconds = self.default_ttl_seconds_if_changed
        else:
            ttl_seconds = self.default_ttl_seconds
        try:
            self.redis_client.set(key_for(station, 'response'), response, ex=ttl_seconds)
        except redis.exceptions.ConnectionError as e:
            logging.warning("Error connecting to Redis. Server cannot return cached response.")
            logging.exception(e)
