#!/bin/bash
source env/bin/activate
powerfulseal --inventory-kubernetes --kube-config ${HOME}/.kube/config --filter-name e2e-v1.7 --cloud-driver dind --interactive
