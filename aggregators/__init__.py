import importlib
import functools
import logging
import yaml
from dataclasses import dataclass, field


@dataclass
class PlayingItem():
    type: str
    title: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Aggregator():
    module_name: str
    params: dict = field(default_factory=dict)


def load_aggregators():
    aggregators = dict()
    with open('config/stations.yaml', 'r') as cfg:
        stations_cfg = yaml.safe_load(cfg)['stations']
        for country_code, stations in stations_cfg.items():
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


def _with_default_params(params: dict, country_code: str, station_id: str) -> dict:
    if 'country_code' in params:
        params['country_code'] = country_code
    if 'station_id' in params:
        params['station_id'] = station_id
    return params


aggregators = load_aggregators()


def aggregator_for_station(full_id=None, country_code=None, station_id=None):
    global aggregators
    if full_id:
        try:
            country_code, station_id = full_id.split('/')
        except ValueError:
            raise ModuleNotFoundError(f"Could not find aggregator for station id '{full_id}'")
    try:
        aggregator = aggregators[(country_code, station_id)]
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
