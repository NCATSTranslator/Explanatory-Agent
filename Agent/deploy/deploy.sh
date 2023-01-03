#!/bin/bash

projectName="agent"
namespace="chp"

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    values.yaml
rm values.yaml.bak

echo "Print out variables:"
echo $DB_USERNAME
echo $DB_PASSWORD
echo $APP_DB_USERNAME
echo $APP_DB_PASSWORD
cat values-ncats.yaml
helm -n ${namespace} upgrade --install ${projectName} -f values-ncats.yaml ./
