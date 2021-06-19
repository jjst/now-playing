import os
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import subprocess
import tempfile

#FIXME: this becomes the git watcher code
# Separate module for:
# * General conf stuffs
# * File watcher
# * Git watcher

TEMP_DIR = tempfile.gettempdir()
CONFIG_REPOSITORY_PATH = os.path.join(TEMP_DIR, "git-config")
DEFAULT_CHECK_FREQUENCY_SECONDS = 10

_scheduler = BackgroundScheduler(daemon=True)


class GitWatcher():
    def __init__(self, repo, subfolder, frequency=DEFAULT_CHECK_FREQUENCY_SECONDS):
        clone_repo(repo, subfolder)
        schedule_pulls(repo, subfolder, frequency)


def clone_repo(repo, subfolder):
    print("Cloning repo")
    subprocess.run(["git", "clone", "--depth=1", repo, CONFIG_REPOSITORY_PATH], cwd=TEMP_DIR)
    if subfolder:
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=CONFIG_REPOSITORY_PATH)
        subprocess.run(["git", "sparse-checkout", "set", subfolder], cwd=CONFIG_REPOSITORY_PATH)


def schedule_pulls(repo, subfolder, frequency):
    print("Starting scheduled checks")
    _scheduler.add_job(lambda: check_for_changes(repo, subfolder), 'interval', seconds=frequency)
    _scheduler.start()


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
    if changed:
        logging.info(changed)
