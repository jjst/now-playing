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
    with open('config/stations.yaml', 'r') as cfg:
        stations_cfg = yaml.safe_load(cfg)['stations']
        for country_code, stations in stations_cfg.items():
            for station_id, station_config in stations.items():
                # FIXME only loading first configured aggregator rn
                aggregators[(country_code, station_id)] = station_config['aggregators'][0]['module']
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
