#!/bin/sh
set -e -u

mkdir -p /tmp/swagger-codegen
docker run \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -v "$(pwd)"/api/swagger:/swagger \
    -v "/tmp/swagger-codegen:/tmp" \
    swaggerapi/swagger-codegen-cli generate -l python-flask -i /swagger/swagger.yaml -o /tmp/ -Dmodels -DpackageName=api
cp -R /tmp/swagger-codegen/* .
