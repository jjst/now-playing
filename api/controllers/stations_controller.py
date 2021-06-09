import connexion
import logging
import os
import requests_cache
import six
import yaml

from api.models.radio_station_list import RadioStationList
from api.models.radio_station import RadioStation
from api.models.now_playing import NowPlaying
from api.models.stream import Stream

import aggregators


with open('config/stations.yaml', 'r') as cfg:
    stations = yaml.safe_load(cfg)['stations']

cache_ttl = int(os.environ.get("REQUEST_CACHE_TTL_SECONDS", "3"))
session = requests_cache.CachedSession(backend='memory', expire_after=cache_ttl)


def get_stations_by_country_code(countryCode):
    items = []
    for station_id, data in stations[countryCode].items():
        items.append(_build_station(data, station_id, countryCode))
    return RadioStationList(items=items)


def get_now_playing_by_country_code_and_station_id(countryCode, stationId):
    logging.info(f"Getting now playing information for station id: '{countryCode}/{stationId}'")
    try:
        _ = stations[countryCode][stationId]
    except KeyError:
        return {'title': "Station not found"}, 404
    try:
        aggregator = aggregators.aggregator_for_station(country_code=countryCode, station_id=stationId)
    except ModuleNotFoundError as e:
        # Couldnt get a valid aggregator
        logging.warn("Could not load station aggregator for station")
        logging.exception(e)
        return {'title': f"No 'now-playing' information is available for station '{countryCode}/{stationId}'"}, 404
    try:
        now_playing_items = aggregator.fetch(session, 'now-playing', countryCode, stationId)
        playing_item = next(iter(now_playing_items))
        return NowPlaying(type=playing_item.type, title=playing_item.title)
    except StopIteration:
        return {'title': "Could not fetch now playing information"}, 500


def get_station_by_country_code_and_station_id(countryCode, stationId):  # noqa: E501
    """
    Returns a radio station

    :param countryCode: Country code of a station
    :type countryCode: str
    :param stationId: ID of a station
    :type stationId: str

    :rtype: RadioStation
    """
    try:
        station = stations[countryCode][stationId]
        return _build_station(station, stationId, countryCode)
    except KeyError:
        return {'title': "Station not found"}, 404


def search(query):  # noqa: E501
    """Finds a station by name

    :param query: Search query

    :rtype: List[SearchResult]
    """
    return []


def _build_station(station, station_id, country_code):
    station_name = station['name']
    streams = [Stream(**s) for s in station.get('streams', [])]
    favicon = station.get('favicon')
    radio_station = RadioStation(
        id=station_id,
        country_code=country_code,
        name=station_name,
        favicon=favicon,
        streams=streams
    )
    return radio_station
