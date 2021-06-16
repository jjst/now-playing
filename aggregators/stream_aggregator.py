from aggregators import PlayingItem
from streamscrobbler import streamscrobbler


def fetch(session, request_type: str, stream_url: str):
    stationinfo = streamscrobbler.get_server_info(stream_url)
    if stationinfo['metadata']:
        metadata = stationinfo['metadata']
        try:
            song = metadata['song']
            return [PlayingItem(type='song', title=song)]
        except KeyError:
            return []
    return []
