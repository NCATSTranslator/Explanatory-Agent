#!/bin/bash

projectName="agent"
namespace="chp"

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    values.yaml
rm values.yaml.bak

cat values-ncats.yaml
helm -n ${namespace} upgrade --install ${projectName} -f values-ncats.yaml ./
