from dynaconf.default_settings import get
from dynaconf import Dynaconf
from base.config.watchedconf import WatchedConf
import os
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import tempfile

#FIXME: this becomes the git watcher code
# Separate module for:
# * General conf stuffs
# * File watcher
# * Git watcher


TEMP_DIR = tempfile.gettempdir()

CONFIG_REPOSITORY_PATH = os.path.join(TEMP_DIR, "git-config")


path = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CONFIG_PATH = os.path.abspath(os.path.join(path, "../../conf"))

DEFAULT_STATION_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_PATH, "stations")


def dynadynaconf():
    conf = WatchedConf(
        envvar_prefix="DYNACONF",
        # settings_files=['logging.ini'], # FIXME: causes exception
        includes=['stations/*.yaml', 'stations/*/*.yaml'],
        root_path=DEFAULT_CONFIG_PATH,
        merge_enabled=True
    )
    return conf


def clone_repo(repo, subfolder):
    print("Cloning repo")
    subprocess.run(["git", "clone", "--depth=1", repo, CONFIG_REPOSITORY_PATH], cwd=TEMP_DIR)
    if subfolder:
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=CONFIG_REPOSITORY_PATH)
        subprocess.run(["git", "sparse-checkout", "set", subfolder], cwd=CONFIG_REPOSITORY_PATH)


def schedule_pulls(repo, subfolder, frequency):
    print("Starting scheduled checks")
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(lambda: check_for_changes(repo, subfolder), 'interval', seconds=frequency)
    sched.start()


def check_for_changes(repo, subfolder):
    print("Checking repo for changes...")
    subprocess.run(["git", "fetch", "--depth=1"], cwd=CONFIG_REPOSITORY_PATH)
    if subfolder:
        extra_args = ["--", subfolder]
    else:
        extra_args = []
    changed = subprocess.check_output(["git", "diff", "--name-only", "main", "origin/main"] + extra_args, cwd=CONFIG_REPOSITORY_PATH)
    changed = changed.decode('utf-8').strip().split("\n")
    subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=CONFIG_REPOSITORY_PATH)
    print(changed)
