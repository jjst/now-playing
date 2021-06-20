from dynaconf.default_settings import get
from dynaconf.base import LazySettings
from dynaconf.utils import ensure_a_list
from dynaconf import Dynaconf
import os
import logging
import subprocess
import tempfile
import watchdog
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class WatchedConf(Dynaconf, FileSystemEventHandler):
    def __init__(self, **kwargs):
        super(WatchedConf, self).__init__(**kwargs)
        self._observer = Observer()
        self._observer.schedule(self, self._root_path, recursive=True)
        self._observer.start()

    def on_modified(self, event):
        rel_event_path = os.path.relpath(event.src_path, self._root_path)
        includes = ensure_a_list(self.get("INCLUDES_FOR_DYNACONF"))
        for glob in includes:
            if fnmatch.fnmatch(rel_event_path, glob):
                logging.info(f"Detected change in configuration file '{rel_event_path}', reloading")
                self.load_file(rel_event_path)
