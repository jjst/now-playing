#!/bin/sh
docker run -v "$(pwd)"/api/swagger:/swagger swaggerapi/swagger-codegen-cli generate -l python-flask -i /swagger/swagger.yaml -o /tmp -Dmodels -DpackageName=api
