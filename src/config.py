import logging.config
import os
import yaml

path = os.path.dirname(os.path.abspath(__file__))


DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.join(path, os.pardir), "conf"))

DEFAULT_STATION_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_PATH, "stations")


def load_logging_config(path=DEFAULT_CONFIG_PATH):
    # Using print() since logging not set up yet
    print(f"Loading config from '{path}'")
    config_file = os.path.join(path, 'logging.ini')
    logging.config.fileConfig(config_file)


def load_stations(path=DEFAULT_STATION_CONFIG_PATH):
    print(f"Loading station config from '{path}'")
    if os.path.isfile(path):
        return _load_stations_file(path)
    else:
        all_stations = {}
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                loaded_conf = _load_stations_file(os.path.join(dirpath, filename))
                _merge_config(all_stations, loaded_conf)
        return all_stations


def _merge_config(orig, new):
    for namespace, stations in new.items():
        if namespace in orig:
            orig[namespace] |= stations
        else:
            orig[namespace] = stations
    return orig


def _load_stations_file(path):
    _, ext = os.path.splitext(path)
    if ext in ('.yaml', '.yml'):
        logging.info(f"Loading stations from file '{path}'")
        with open(path, 'r') as cfg:
            return yaml.safe_load(cfg)['stations']
