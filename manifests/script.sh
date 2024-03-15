#!/bin/bash

kubectl create namespace standard

kubectl apply -f ./elasticsearch/elasticsearch-pvc.yaml -n standard
kubectl apply -f ./elasticsearch/elasticsearch-configmap.yaml -n standard
kubectl apply -f ./elasticsearch/elasticsearch-service.yaml -n standard
kubectl apply -f ./elasticsearch/elasticsearch-statefulset.yaml -n standard

kubectl apply -f ./kibana/kibana-service.yaml -n standard
kubectl apply -f ./kibana/kibana-deployment.yaml -n standard

kubectl apply -f ./data-air/data-air-cronjob.yaml -n standard

kubectl apply -f ./db/db-pvc.yaml -n standard
kubectl apply -f ./db/db-configmap.yaml -n standard
kubectl apply -f ./db/db-secret.yaml -n standard
kubectl apply -f ./db/db-service.yaml -n standard
kubectl apply -f ./db/db-statefulset.yaml -n standard

kubectl apply -f ./web/web-service.yaml -n standard
kubectl apply -f ./web/web-deployment.yaml -n standard

kubectl apply -f ./pgAdmin/pgadmin-secret.yaml -n standard
kubectl apply -f ./pgAdmin/pgadmin-service.yaml -n standard
kubectl apply -f ./pgAdmin/pgadmin-deployment.yaml -n standard

kubectl apply -f ./ingress.yaml -n standard

kubectl get all -n standard