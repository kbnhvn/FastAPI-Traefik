#!/bin/bash
# --------  Script de backup pouvant être lancé avec un CronJob  --------- #

# Création d'un sous-dossier daté
DATE=$(date +%F)
BACKUP_DIR="/home/ubuntu/backup/backup-$DATE"
mkdir -p "$BACKUP_DIR"

# Commande de backup k3s
sudo k3s etcd-snapshot save --etcd-snapshot-dir="$BACKUP_DIR"

# Copie du backup dans le bucket S3
sudo aws s3 cp "$BACKUP_DIR"/* s3://ec2-fastapi-traefik-backup/backup-"$DATE"