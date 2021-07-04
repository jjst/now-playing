import logging
import redis
from typing import Optional

from base.config import settings
from base.stations import RadioStationInfo


class ResponseCache():
    def __init__(self, settings=settings):
        self.redis_client = redis.Redis(
            settings.redis.host,
            settings.redis.port,
            settings.redis.db,
            socket_timeout=settings.redis.socket_timeout,
            socket_connect_timeout=settings.redis.socket_connect_timeout,
        )
        self.default_ttl_seconds = settings.redis.ttl_seconds

    def get(self, station: RadioStationInfo) -> Optional[str]:
        try:
            return self.redis_client.get(station.station_id())
        except redis.exceptions.ConnectionError as e:
            logging.warning("Error connecting to Redis. Server cannot return cached response.")
            logging.exception(e)
            return None

    def set(self, station: RadioStationInfo, response: str, ttl_seconds: Optional[int] = None):
        if not ttl_seconds:
            ttl_seconds = self.default_ttl_seconds
        try:
            self.redis_client.set(station.station_id(), response, ex=ttl_seconds)
        except redis.exceptions.ConnectionError as e:
            logging.warning("Error connecting to Redis. Server cannot return cached response.")
            logging.exception(e)
