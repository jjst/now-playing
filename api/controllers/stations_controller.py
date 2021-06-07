import connexion
import logging
import six
import yaml

from api.models.radio_station import RadioStation  # noqa: E501
from api.models.now_playing import NowPlaying  # noqa: E501

import aggregators


with open('config/stations.yaml', 'r') as cfg:
    stations = yaml.safe_load(cfg)['stations']


def get_stations_by_country_code(countryCode):  # noqa: E501
    return stations[countryCode]


def get_now_playing_by_country_code_and_station_id(countryCode, stationId):  # noqa: E501
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
        return {'title': "Could not load aggregator for station"}, 503
    try:
        now_playing_items = aggregator.fetch()
        playing_item = next(i for i in now_playing_items if i.station_id == stationId)
        return NowPlaying(type=playing_item.type, title=playing_item.title)
    except StopIteration:
        return {'title': "Could not fetch now playing information"}, 503


def get_station_by_country_code_and_station_id(countryCode, stationId):  # noqa: E501
    """Find pet by ID

    Returns a radio station # noqa: E501

    :param countryCode: Country code of a station
    :type countryCode: str
    :param stationId: ID of a station
    :type stationId: str

    :rtype: RadioStation
    """
    try:
        station = stations[countryCode][stationId]
        station_name = station['name']
        favicon = station.get('favicon')
        radio_station = RadioStation(
            id=stationId,
            country_code=countryCode,
            name=station_name,
            favicon=favicon
        )
        return radio_station

    except KeyError:
        return {'title': "Station not found"}, 404


def search(query):  # noqa: E501
    """Finds a station by name

    Muliple tags can be provided with comma separated strings. Use         tag1, tag2, tag3 for testing. # noqa: E501

    :param query: Tags to filter by
    :type query: List[str]

    :rtype: List[SearchResult]
    """
    return 'do some magic!'
