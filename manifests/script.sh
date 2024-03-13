#!/bin/bash

kubectl apply -f ./elasticsearch/elasticsearch-pvc.yaml -n standard
kubectl apply -f ./elasticsearch/elasticsearch-configmap.yaml -n standard
kubectl apply -f ./elasticsearch/elasticsearch-service.yaml -n standard
kubectl apply -f ./elasticsearch/elasticsearch-statefulset.yaml -n standard

kubectl apply -f ./kibana/kibana-service.yaml -n standard
kubectl apply -f ./kibana/kibana-deployment.yaml -n standard

kubectl apply -f ./data-air/data-air-cronjob.yaml -n standard