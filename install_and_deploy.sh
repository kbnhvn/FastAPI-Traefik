#!/bin/bash
# --------  Script d'installation et de déploiement  --------- #

# Préparation
sudo apt update && sudo apt install curl

# Installation de K3S
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

# Correction des droits
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# Création des namespaces
kubectl create namespace dev
kubectl create namespace prod

# Installation de helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
rm -f ./get_helm.sh

# Configuration de helm
mkdir .kube 
kubectl config view --raw > ~/.kube/config

# Déploiements
helm upgrade --install app fastapi-traefik --values=./fastapi-traefik/values.yaml -f ./fastapi-traefik/values-dev.yaml -f ./custom_values.yaml --namespace dev
helm upgrade --install app fastapi-traefik --values=./fastapi-traefik/values.yaml -f ./fastapi-traefik/values-prod.yaml -f ./custom_values.yaml --namespace prod