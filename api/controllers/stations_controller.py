import connexion
import six

from api.models.radio_station import RadioStation  # noqa: E501
from api.models.now_playing import NowPlaying  # noqa: E501

from aggregators import fip


stations = {
    'fr': {
        'fip-rock': "FIP Rock"
    }
}

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
        now_playing_items = fip.fetch_info()
        playing_item = next(i for i in now_playing_items if i.station_id == stationId)
        if playing_item:
            return RadioStation(
                id=stationId,
                country_code=countryCode,
                name="i dunno lol",
                now_playing=NowPlaying(type='song', title=playing_item.title)
            )
        else:
            return {'title': "No playing data for station"}, 404
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
