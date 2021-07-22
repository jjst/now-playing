import asyncio
import json
import logging
from aiohttp.web import Response, json_response

from opentelemetry import trace


from api.models.radio_station_list import RadioStationList
from api.models.radio_station import RadioStation
from api.models.now_playing_item_list import NowPlayingItemList
from api.models.song import Song
from api.models.programme import Programme
from api.models.stream import Stream
from api.encoder import JSONEncoder
from api.response_cache import ResponseCache, CacheError
from api.result_saver import AggregationResultSaver

import aggregators
from base.stations import RadioStationInfo
from base.session import session
import base.stations as stations


tracer = trace.get_tracer(__name__)

response_cache = ResponseCache()

aggregation_result_saver = AggregationResultSaver()


def json_dumps(data):
    return json.dumps(data, cls=JSONEncoder)


async def get_stations():
    all_stations = stations.get_all()
    data = RadioStationList(items=[_build_station(s) for s in all_stations])
    return json_response(data=data, dumps=json_dumps)


async def get_stations_by_country_code(namespace):
    stations_by_country = stations.get_all(namespace=namespace)
    data = RadioStationList(items=[_build_station(s) for s in stations_by_country])
    return json_response(data=data, dumps=json_dumps)


async def get_now_playing_by_country_code_and_station_id(namespace, slug):
    logging.info(f"Getting now playing information for station id: '{namespace}/{slug}'")
    try:
        station = stations.get(namespace, slug)
    except KeyError:
        return json_response(data={'title': "Station not found"}, status=404)
    try:
        cached_response = response_cache.get(station)
    except CacheError as e:
        # Log error, but we can proceed without caching with degraded performance
        cached_response = None
        logging.exception(e)
    current_span = trace.get_current_span()
    if cached_response:
        logging.info(f"Returning cached respones for {station.station_id()}")
        if current_span:
            current_span.set_attribute('http.cached_response', True)
        return Response(body=cached_response, content_type='application/json')
    elif current_span:
        current_span.set_attribute('http.cached_response', False)
    try:
        aggregator = aggregators.aggregator_for_station(country_code=namespace, station_id=slug)
    except ModuleNotFoundError as e:
        # Couldnt get a valid aggregator
        logging.warn("Could not load station aggregator for station")
        logging.exception(e)
        return json_response(
            data={'title': f"No 'now-playing' information is available for station '{namespace}/{slug}'"},
            status=404
        )
    with tracer.start_as_current_span("call_aggregator") as span:
        span.set_attribute('aggregator.module_name', aggregator.module_name)
        for key, val in aggregator.params.items():
            span.set_attribute(f'aggregator.params.{key}', str(val))
        span.set_attribute('station_id', f'{namespace}/{slug}')
        span.set_attribute('namespace', namespace)
        span.set_attribute('slug', slug)
        aggregation_result = aggregator(session, 'now-playing')
        asyncio.create_task(
            aggregation_result_saver.save_aggregation_result(f"{namespace}/{slug}", aggregation_result)
        )
    playing_items_list = _build_now_playing_item_list(aggregation_result.items)
    if aggregation_result.items:
        cache_expiry = min(i.end_time for i in aggregation_result.items)
    else:
        cache_expiry = None
    response = json.dumps(playing_items_list, cls=JSONEncoder)
    actual_cache_expiry_seconds = None
    try:
        actual_cache_expiry_seconds = response_cache.set(station, response, expire_at=cache_expiry)
    except CacheError as e:
        # Log error, but we can proceed without caching with degraded performance
        logging.exception(e)
    headers = {}
    if actual_cache_expiry_seconds:
        headers['Cache-Control'] = f'max-age={actual_cache_expiry_seconds}'
    return Response(body=response, content_type='application/json', headers=headers)


async def get_station_by_country_code_and_station_id(namespace, slug):  # noqa: E501
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
        return json_response(data=_build_station(station_info), dumps=json_dumps)
    except KeyError:
        return json_response(data={'title': "Station not found"}, status=404)


async def search(query):  # noqa: E501
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
        logo_url=station_info.logo_url,
        streams=streams
    )
    return radio_station


def _build_now_playing_item_list(source_items):
    items = []
    for i in source_items:
        if i.type == 'song':
            items.append(Song(
                type='song',
                text=i.text,
                artist=i.artist,
                cover_art=i.cover_art,
                title=i.song_title,
                album=i.album,
                start_time=i.start_time,
                end_time=i.end_time,
            ))
        elif i.type == 'programme':
            items.append(Programme(
                type='programme',
                text=i.text,
                name=i.name,
                cover_art=i.cover_art,
                episode_title=i.episode_title,
                start_time=i.start_time,
                end_time=i.end_time,
            ))
    return NowPlayingItemList(items=items)
