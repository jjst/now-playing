from aggregators import AggregationResult, PlayingItem, Source

import chardet
import logging
from streamscrobbler import streamscrobbler


def fetch(session, request_type: str, stream_url: str, encoding: str = None):
    stationinfo = streamscrobbler.get_server_info(stream_url)
    items = []
    sources = []
    if stationinfo['metadata']:
        metadata = stationinfo['metadata']
        sources = [Source(type='stream_metadata', data=metadata)]
        try:
            song = metadata['song']
            # Looks like sometimes the library returns bytes instead of str...
            # If this is true we got ourselves a bytes/bytestring object
            if hasattr(song, 'decode'):
                if not encoding:
                    logging.warn("Encoding not specified, trying to guess charset...")
                    result = chardet.detect(song)
                    logging.info(f"Detected: {result}")
                    encoding = result['encoding']
                song = song.decode(encoding)
            items = [PlayingItem(type='song', title=song)]
        except KeyError:
            pass
    return AggregationResult(
        items=items,
        sources=sources
    )
