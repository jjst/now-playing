import logging.config
import os
import yaml

path = os.path.dirname(os.path.abspath(__file__))


DEFAULT_CONFIG_PATH = os.path.join(path, 'stations')


def load_logging_config():
    config_file = os.path.join(os.getcwd(), 'logging.ini')
    logging.config.fileConfig(config_file)


def load_stations(path=DEFAULT_CONFIG_PATH):
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
