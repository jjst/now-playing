#!/bin/sh
set -e -u

mkdir -p /tmp/swagger-codegen
docker run \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -v "$(pwd)"/src/api/openapi:/openapi \
    -v "/tmp/swagger-codegen:/tmp" \
    swaggerapi/swagger-codegen-cli generate -l python-flask -i /openapi/spec.yaml -o /tmp/ -Dmodels -DpackageName=api
cp -R /tmp/swagger-codegen/* src/.
