import logging.config
import os
from base.dynadynaconf import dynadynaconf, DEFAULT_CONFIG_PATH


settings = dynadynaconf()


def load_logging_config(path=DEFAULT_CONFIG_PATH):
    # Using print() since logging not set up yet
    print(f"Loading config from '{path}'")
    config_file = os.path.join(path, 'logging.ini')
    logging.config.fileConfig(config_file)


def load_stations():
    return settings.stations
