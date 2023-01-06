#!/bin/bash

source prepare.sh

projectName="agent"
namespace="chp"

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    values.yaml
rm values.yaml.bak

sed -i.bak \
    -e "s/DB_USERNAME_VALUE/$DB_USERNAME/g;s/DB_PASSWORD_VALUE/$DB_PASSWORD/g" \
    -e "s/APP_DBUSERNAME_VALUE/$APP_DBUSERNAME/g;s/APP_DBPASSWORD_VALUE/$APP_DBPASSWORD/g" \
    values-ncats.yaml
rm values-ncats.yaml.bak

helm -n ${namespace} upgrade --install ${projectName} -f values-ncats.yaml ./
