#!/bin/bash
source env/bin/activate
nohup powerfulseal -vvv --inventory-kubernetes --kube-config ${HOME}/.kube/config --filter-name e2e-v1.7 --cloud-driver dind --run-policy-file ./stability_config.yml 1>powerfulseal.log 2>&1&
