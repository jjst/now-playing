#!/bin/sh

set -o errexit

python3 -m healthcheck &

redis-server
