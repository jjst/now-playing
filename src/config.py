import logging.config
import os
from dynaconf import Dynaconf


path = os.path.dirname(os.path.abspath(__file__))


DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(os.path.join(path, os.pardir), "conf"))

DEFAULT_STATION_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_PATH, "stations")


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    # settings_files=['logging.ini'], # FIXME: causes exception
    includes=['stations/*.yaml', 'stations/*/*.yaml'],
    root_path=DEFAULT_CONFIG_PATH,
    merge_enabled=True
)


def load_logging_config(path=DEFAULT_CONFIG_PATH):
    # Using print() since logging not set up yet
    print(f"Loading config from '{path}'")
    config_file = os.path.join(path, 'logging.ini')
    logging.config.fileConfig(config_file)


def load_stations(path=DEFAULT_STATION_CONFIG_PATH):
    return settings.stations
