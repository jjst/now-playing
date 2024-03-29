from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Union, Optional


OptionalTime = Union[datetime, int, None]


@dataclass
class PlayingItem():
    type: str
    text: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    cover_art: Optional[str]

    def __init__(self, type: str, text: str, cover_art: Optional[str] = None,
                 start_time: OptionalTime = None, end_time: OptionalTime = None):
        self.type = type
        self.text = text
        self.start_time = self._to_datetime(start_time)
        self.end_time = self._to_datetime(end_time)
        self.cover_art = cover_art

    def _to_datetime(self, o):
        if o:
            try:
                timestamp = int(o)
            except TypeError:
                return o
            else:
                return datetime.fromtimestamp(timestamp)

    def duration(self) -> Optional[timedelta]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@dataclass
class Song(PlayingItem):
    artist: str
    song_title: str
    album: Optional[str]

    def __init__(self, artist: str, song_title: str, album: Optional[str] = None, cover_art: Optional[str] = None,
                 start_time: OptionalTime = None, end_time: OptionalTime = None):
        text = f"{artist} - {song_title}"
        super().__init__(type='song', text=text, cover_art=cover_art, start_time=start_time, end_time=end_time)
        self.artist = artist
        self.song_title = song_title
        self.album = album


class Programme(PlayingItem):
    name: str
    episode_title: Optional[str]

    def __init__(self, name: str, episode_title: Optional[str], cover_art: Optional[str] = None,
                 start_time: OptionalTime = None, end_time: OptionalTime = None):
        if episode_title:
            text = f"{name} - {episode_title}"
        else:
            text = name
        super().__init__(type='programme', text=text, cover_art=cover_art, start_time=start_time, end_time=end_time)
        self.name = name
        self.episode_title = episode_title


@dataclass
class Source():
    type: str
    data: Union[dict, str, None]


@dataclass
class AggregationResult():
    items: list[PlayingItem]
    sources: list[Source]

    @staticmethod
    def empty(sources: list[Source]):
        return AggregationResult(items=[], sources=sources)


@dataclass
class Aggregator():
    module_name: str
    params: dict = field(default_factory=dict)
