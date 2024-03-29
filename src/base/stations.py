from dataclasses import dataclass
import itertools
from typing import Any, Optional

from base.config import settings


@dataclass
class RadioStationInfo:
    namespace: str
    slug: str
    name: str
    favicon: Optional[str]
    logo_url: Optional[str]
    streams: list[Any]

    def station_id(self):
        return f'{self.namespace}/{self.slug}'


def get_all(namespace: Optional[str] = None) -> list[RadioStationInfo]:
    def stations_in_namespace(ns):
        items = []
        for station_id, data in settings.get("stations")[ns].items():
            items.append(_build_station_info(data, station_id, ns))
        return items
    if namespace:
        return stations_in_namespace(namespace)
    else:
        return itertools.chain.from_iterable(stations_in_namespace(ns) for ns in settings.get("stations"))


def get(namespace: str, id: str) -> RadioStationInfo:
    data = settings["stations"][namespace][id]
    return _build_station_info(data, id, namespace)


def _build_station_info(station, station_id, namespace):
    station_name = station['name']
    streams = [s for s in station.get('streams', [])]
    favicon = station.get('favicon')
    logo_url = station.get('logo_url')
    radio_station = RadioStationInfo(
        namespace=namespace,
        slug=station_id,
        name=station_name,
        favicon=favicon,
        logo_url=logo_url,
        streams=streams
    )
    return radio_station
