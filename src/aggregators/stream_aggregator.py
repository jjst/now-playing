from aggregators import AggregationResult, PlayingItem, Song, Source

import chardet
import logging
from streamscrobbler import streamscrobbler
import re

SONG_RE_PATTERN = "(.+) - (.+)"

def fetch(session, request_type: str, stream_url: str, encoding: str = None):
    stationinfo = streamscrobbler.get_server_info(stream_url)
    items = []
    sources = []
    if stationinfo['metadata']:
        metadata = stationinfo['metadata']
        sources = [Source(type='stream_metadata', data=metadata)]
        try:
            song = metadata['song']
        except KeyError:
            pass
        else:
            # Looks like sometimes the library returns bytes instead of str...
            # If this is true we got ourselves a bytes/bytestring object
            if hasattr(song, 'decode'):
                if not encoding:
                    logging.warn("Encoding not specified, trying to guess charset...")
                    result = chardet.detect(song)
                    logging.info(f"Detected: {result}")
                    encoding = result['encoding']
                song = song.decode(encoding)
            artist, title = _extract_artist_and_title(song)
            items = [Song(artist=artist, song_title=title)]
    return AggregationResult(
        items=items,
        sources=sources
    )


def _extract_artist_and_title(song):
    """
    We get a single string with both artist and title, which isn't great.
    Try and extract artist and title out of it. It won't necessarily be super
    accurate.
    """
    match = re.search(SONG_RE_PATTERN, song)
    return (match.group(1), match.group(2))

