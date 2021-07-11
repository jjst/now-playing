from datetime import datetime, timedelta
import importlib
import functools
import logging
from typing import Union, Optional
from dataclasses import dataclass, field

from base import config

OptionalTime = Union[datetime, int, None]


# TODO: Separate into subclasses for Programme and Song, with different attributes
# artist + title in one case, programme_title + episode_title in other
@dataclass
class PlayingItem():
    type: str
    title: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __init__(self, type: str, title: str, start_time: OptionalTime = None, end_time: OptionalTime = None):
        self.type = type
        self.title = title
        self.start_time = self._to_datetime(start_time)
        self.end_time = self._to_datetime(end_time)

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


def load_aggregators():
    stations_config = config.load_stations()
    aggregators = {}
    for country_code, stations in stations_config.items():
        for station_id, station_config in stations.items():
            # FIXME only loading first configured aggregator rn
            try:
                aggregator_config = station_config['aggregators']['now-playing'][0]
                module_name = aggregator_config['module']
                params = _with_default_params(aggregator_config.get('params', {}), country_code, station_id)
                aggregators[(country_code, station_id)] = Aggregator(module_name, params)
            except TypeError as e:
                logging.error(f"Failed to load aggregator for station '{country_code}/{station_id}'")
                logging.exception(e)
    return aggregators


def _with_default_params(params: dict, namespace: str, slug: str) -> dict:
    """
    Support for default parameters. Some aggregator parameters don't need to
    have a value specified, they indicate the aggregator wants to get existing
    information from the station it's aggregating data for.
    """
    # TODO: I'm not actually sure I want to keep this feature as-is.
    # Leaning towards always providing station info as a param to fetch() instead.
    if 'country_code' in params:
        # Legacy attr name
        params['country_code'] = namespace
    if 'namespace' in params:
        params['namespace'] = namespace
    if 'slug' in params:
        params['slug'] = slug
    if 'station_id' in params:
        params['station_id'] = f"{namespace}/{slug}"
    return params


_aggregators: dict = {}


def aggregator_for_station(full_id=None, country_code=None, station_id=None):
    global _aggregators
    if not _aggregators:
        _aggregators = load_aggregators()
    if full_id:
        try:
            country_code, station_id = full_id.split('/')
        except ValueError:
            raise ModuleNotFoundError(f"Could not find aggregator for station id '{full_id}'")
    try:
        aggregator = _aggregators[(country_code, station_id)]
    except KeyError:
        raise ModuleNotFoundError(f"Could not find aggregator for station '{country_code}/{station_id}'")
    return load(aggregator)


def load(aggregator):
    module = importlib.import_module("aggregators." + aggregator.module_name)
    fetch_func = module.fetch
    bound_function = functools.partial(fetch_func, **aggregator.params)
    bound_function.module_name = aggregator.module_name
    bound_function.params = aggregator.params
    return bound_function
