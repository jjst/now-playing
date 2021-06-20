#!/bin/sh

set -o errexit

if [ -n "${GIT_CONFIG_REPOSITORY+set}" ]; then
    readonly repo_local_path="/tmp/git-config"
    rm -rf $repo_local_path
    git clone --depth=1 $GIT_CONFIG_REPOSITORY $repo_local_path
    cd $repo_local_path
    if [ -n "${GIT_CONFIG_REPOSITORY_SUBFOLDER+set}" ]; then
        echo "Doing a sparse checkout of $GIT_CONFIG_REPOSITORY_SUBFOLDER"
        git sparse-checkout init --cone
        git sparse-checkout set $GIT_CONFIG_REPOSITORY_SUBFOLDER
    fi
    cd - > /dev/null
    export ROOT_PATH_FOR_DYNACONF="$repo_local_path/$GIT_CONFIG_REPOSITORY_SUBFOLDER"
    echo "Configured auto-configuration loading from git. Setting configuration root path to $ROOT_PATH_FOR_DYNACONF."
    current_dir=$(dirname "$0")
    $current_dir/git_tracker.sh $repo_local_path &
fi

cd src/
gunicorn --access-logfile=- --bind 0.0.0.0:8080 --worker-tmp-dir /dev/shm api:app
