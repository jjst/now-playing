from collections import namedtuple
import importlib


def load(aggregator_name):
    return importlib.import_module("aggregators." + aggregator_name)


PlayingItem = namedtuple('PlayingItem', ['country_code', 'station_id', 'type', 'title', 'metadata'])
