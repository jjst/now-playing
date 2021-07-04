from dynaconf.default_settings import get
import logging.config
import os

from base.config.watchedconf import WatchedConf


path = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(path, "../../../conf"))

ROOT_PATH_FOR_DYNACONF = get("ROOT_PATH_FOR_DYNACONF", DEFAULT_CONFIG_PATH)

print(f"Using config path {ROOT_PATH_FOR_DYNACONF}")

settings = WatchedConf(
    envvar_prefix=False,
    settings_files=['config.yaml'],
    includes=['stations/*.yaml', 'stations/*/*.yaml'],
    root_path=ROOT_PATH_FOR_DYNACONF,
    merge_enabled=True
)


def load_logging_config(path=DEFAULT_CONFIG_PATH):
    # FIXME: should load using dynaconf/generic conf loading, but causes exception rn 🤷
    # Using print() since logging not set up yet
    # FIXME: should also convert to using YAML and `dictConfig` instead of legacy `fileConfig`
    print(f"Loading config from '{path}'")
    config_file = os.path.join(path, 'logging.ini')
    logging.config.fileConfig(config_file, disable_existing_loggers=False)


def load_stations():
    return settings.stations
