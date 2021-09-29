#!/bin/bash

export $(egrep -v '^#' .env)

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    -e "s/ARS_ALLOWED_HOSTS_VALUE/${ARS_ALLOWED_HOSTS}/g" \
    -e "s|DB_USER_VALUE|${DB_USER}|g" \
    -e "s|DB_PASSWORD_VALUE|${DB_PASSWORD}|g" \
    deployment.yaml
rm deployment.yaml.bak

sed -i.bak \
    -e "s/EA_HOSTNAME_VALUE/${EA_HOSTNAME}/g" \
    -e "s/ARS_ALB_TAG_VALUE/${ARS_ALB_TAG}/g" \
    -e "s/ARS_ALB_SG_VALUE/${ARS_ALB_SG}/g" \
    -e "s/ENVIRONMENT_TAG_VALUE/${ENVIRONMENT_TAG}/g" \
    ingress.yaml
rm ingress.yaml.bak

kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f services.yaml
kubectl apply -f ingress.yaml
