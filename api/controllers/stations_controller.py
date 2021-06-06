import connexion
import six

from api.models.radio_station import RadioStation  # noqa: E501
from api.models.search_result import SearchResult  # noqa: E501
from api import util


def get_station_by_country_code_and_station_id(countryCode, stationId):  # noqa: E501
    """Find pet by ID

    Returns a radio station # noqa: E501

    :param countryCode: Country code of a station
    :type countryCode: str
    :param stationId: ID of a station
    :type stationId: str

    :rtype: RadioStation
    """
    return 'do some magic!'


def search(query):  # noqa: E501
    """Finds a station by name

    Muliple tags can be provided with comma separated strings. Use         tag1, tag2, tag3 for testing. # noqa: E501

    :param query: Tags to filter by
    :type query: List[str]

    :rtype: List[SearchResult]
    """
    return 'do some magic!'
