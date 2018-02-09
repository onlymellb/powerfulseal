#!/bin/bash
powerfulseal --inventory-kubernetes --kube-config ${HOME}/.kube/config --filter-name stability-v1.7 --cloud-driver dind --run-policy-file ./policy_config.yml
