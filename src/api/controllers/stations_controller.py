import logging
import os
import requests_cache

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


from api.models.radio_station_list import RadioStationList
from api.models.radio_station import RadioStation
from api.models.now_playing import NowPlaying
from api.models.stream import Stream

import aggregators
from base.stations import RadioStationInfo
import base.stations as stations

trace.set_tracer_provider(TracerProvider())


cache_ttl = int(os.environ.get("REQUEST_CACHE_TTL_SECONDS", "3"))
session = requests_cache.CachedSession(backend='memory', expire_after=cache_ttl, allowable_methods=('GET', 'POST'))


def get_stations():
    all_stations = stations.get_all()
    return RadioStationList(items=[_build_station(s) for s in all_stations])


def get_stations_by_country_code(namespace):
    stations_by_country = stations.get_all(namespace=namespace)
    return RadioStationList(items=[_build_station(s) for s in stations_by_country])


def get_now_playing_by_country_code_and_station_id(namespace, slug):
    tracer = trace.get_tracer(__name__)
    logging.info(f"Getting now playing information for station id: '{namespace}/{slug}'")
    try:
        _ = stations.get(namespace, slug)
    except KeyError:
        return {'title': "Station not found"}, 404
    try:
        aggregator = aggregators.aggregator_for_station(country_code=namespace, station_id=slug)
    except ModuleNotFoundError as e:
        # Couldnt get a valid aggregator
        logging.warn("Could not load station aggregator for station")
        logging.exception(e)
        return {'title': f"No 'now-playing' information is available for station '{namespace}/{slug}'"}, 404
    try:
        with tracer.start_as_current_span("call_aggregator") as span:
            span.set_attribute('aggregator.module_name', aggregator.module_name)
            for key, val in aggregator.params.items():
                span.set_attribute(f'aggregator.params.{key}', str(val))
            span.set_attribute('station_id', f'{namespace}/{slug}')
            span.set_attribute('namespace', namespace)
            span.set_attribute('slug', slug)
            aggregation_result = aggregator(session, 'now-playing')
        playing_item = next(iter(aggregation_result.items))
        return NowPlaying(type=playing_item.type, title=playing_item.title)
    except StopIteration:
        return {'title': "Could not fetch now playing information"}, 500


def get_station_by_country_code_and_station_id(namespace, slug):  # noqa: E501
    """
    Returns a radio station

    :param namespace: Country code of a station
    :type namespace: str
    :param slug: ID of a station
    :type slug: str

    :rtype: RadioStation
    """
    try:
        station_info = stations.get(namespace, slug)
        return _build_station(station_info)
    except KeyError:
        return {'title': "Station not found"}, 404


def search(query):  # noqa: E501
    """Finds a station by name

    :param query: Search query

    :rtype: List[SearchResult]
    """
    return []


def _build_station(station_info: RadioStationInfo):
    streams = [Stream(**s) for s in station_info.streams]
    radio_station = RadioStation(
        namespace=station_info.namespace,
        slug=station_info.slug,
        id=f"{station_info.namespace}/{station_info.slug}",
        name=station_info.name,
        favicon=station_info.favicon,
        streams=streams
    )
    return radio_station
