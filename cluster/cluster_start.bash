#!/bin/bash

# Start the cluster
#cd .

minikube start --cpus 4 --memory 2048

# Deployment
kubectl apply -f resources/titanic-deploy.yaml

# Secret
#kubectl apply -f resources/titanic-secrets.yaml

# Service
