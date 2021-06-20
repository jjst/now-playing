#!/bin/sh
set -o errexit

readonly GIT_TRACKER_FREQUENCY=10
readonly CONFIG_REPOSITORY_PATH=$1

cd $CONFIG_REPOSITORY_PATH
branch=$(git branch --show-current)

while true; do
	sleep $GIT_TRACKER_FREQUENCY
	git fetch --depth=1 > /dev/null
  git diff --name-only $branch origin/$branch
	git reset --hard origin/$branch > /dev/null
done
