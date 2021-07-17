import logging
from requests.exceptions import HTTPError

from aggregators import AggregationResult, Song, Source
from aggregators.utils import extract_artist_and_title

url = "https://prod.radio-api.net/stations/now-playing"


def fetch(session, request_type: str, radio_dot_net_id: str):
    response = session.get(
        url=url,
        params={'stationIds': radio_dot_net_id}
    )
    try:
        response.raise_for_status()
    except HTTPError as e:
        logging.error(e)
        return AggregationResult(items=[], sources=[])
    data = response.json()
    sources = [Source(type='json', data=data)]
    try:
        artist, title = extract_artist_and_title(data[0]['title'])
    except ValueError:
        items = []
    else:
        items = [Song(artist=artist, song_title=title)]
    return AggregationResult(sources=sources, items=items)
