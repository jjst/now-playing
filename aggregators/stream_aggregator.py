from aggregators import PlayingItem
from streamscrobbler import streamscrobbler


def fetch(session, request_type: str, stream_url: str, encoding: str = 'utf-8'):
    stationinfo = streamscrobbler.get_server_info(stream_url)
    if stationinfo['metadata']:
        metadata = stationinfo['metadata']
        try:
            song = metadata['song']
            try:
                # Looks like sometimes the library returns bytes instead of str...
                song = song.decode(encoding)
            except AttributeError:
                pass
            return [PlayingItem(type='song', title=song)]
        except KeyError:
            return []
    return []
