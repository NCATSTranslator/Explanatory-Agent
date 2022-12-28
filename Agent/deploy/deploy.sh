#!/bin/bash

projectName="agent"
namespace="chp"

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    values.yaml
rm values.yaml.bak

sed -i.bak \
    -e "s/USERNAME_VALUE/${username}/g;s/PASSWORD_VALUE/${password}/g" \
    values-ncats.yaml
rm values-ncats.yaml.bak
sudo su -
helm -n ${namespace} upgrade --install ${projectName} -f values-ncats.yaml ./
