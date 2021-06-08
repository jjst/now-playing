import importlib
import yaml
from dataclasses import dataclass, field


@dataclass
class PlayingItem():
    country_code: str
    station_id: str
    type: str
    title: str
    metadata: dict = field(default_factory=dict)


def load_aggregators():
    aggregators = dict()
    with open('config/aggregators.yaml', 'r') as cfg:
        aggregators_cfg = yaml.safe_load(cfg)['aggregators']
        for agg in aggregators_cfg:
            for station_full_id in agg['stations']:
                country, short_id = station_full_id.split('/')
                aggregators[(country, short_id)] = agg['module']
    return aggregators


aggregators = load_aggregators()


def aggregator_for_station(full_id=None, country_code=None, station_id=None):
    global aggregators
    if full_id:
        try:
            country_code, station_id = full_id.split('/')
        except ValueError:
            raise ModuleNotFoundError(f"Could not find aggregator for station id '{full_id}'")
    try:
        aggregator_name = aggregators[(country_code, station_id)]
    except KeyError:
        raise ModuleNotFoundError(f"Could not find aggregator for station '{country_code}/{station_id}'")
    return load(aggregator_name)


def load(aggregator_name):
    return importlib.import_module("aggregators." + aggregator_name)
