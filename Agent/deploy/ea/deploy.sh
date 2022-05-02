#!/bin/bash

projectName="agent"
namespace="chp"

export $(egrep -v '^#' .env)

sed -i.bak \
    -e "s|DB_USERNAME_VALUE|${DB_USERNAME}|g" \
    -e "s|DB_PASSWORD_VALUE|${DB_PASSWORD}|g" \
    -e "s|DB_SCHEMA_VALUE|${DB_SCHEMA}|g" \
    templates/secret.yaml
rm templates/secret.yaml.bak

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    values-ci.yaml
rm values-ci.yaml.bak

helm -n ${namespace} upgrade --install ${projectName} -f values-ci.yaml ./
