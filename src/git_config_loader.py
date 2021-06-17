from dynaconf.default_settings import get
from dynaconf.loaders import yaml_loader
import os
import subprocess
import tempfile


TEMP_DIR = tempfile.gettempdir()

CONFIG_REPOSITORY_PATH = os.path.join(TEMP_DIR, "git-config")


def clone_and_watch_repo(repo, subfolder=None):
    subprocess.run(["git", "clone", "--no-checkout", "--depth=1", repo, CONFIG_REPOSITORY_PATH], cwd=TEMP_DIR)
    if subfolder:
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=CONFIG_REPOSITORY_PATH)
        subprocess.run(["git", "sparse-checkout", "set", subfolder], cwd=CONFIG_REPOSITORY_PATH)


def load(obj, env=None, silent=True, key=None, filename=None):
    """
    Reads and loads in to "obj" a single key or all keys from source
    :param obj: the settings instance
    :param env: settings current env (upper case) default='DEVELOPMENT'
    :param silent: if errors should raise
    :param key: if defined load a single key, else load all from `env`
    :param filename: Custom filename to load (useful for tests)
    :return: None
    """
    # Load data from your custom data source (file, database, memory etc)
    # use `obj.set(key, value)` or `obj.update(dict)` to load data
    # use `obj.find_file('filename.ext')` to find the file in search tree
    # Return nothing
    repo = get("GIT_REPO_FOR_DYNACONF")
    subfolder = get("GIT_REPO_SUBFOLDER_FOR_DYNACONF", None)
    if repo and not os.path.exists(CONFIG_REPOSITORY_PATH):
        clone_and_watch_repo(repo, subfolder)
