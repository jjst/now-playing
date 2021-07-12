import importlib
import functools
import logging

from base import config
from aggregators.models import * # noqa
from aggregators.models import Aggregator


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
