# Récupération des données

Ce service permet de récupérer les données de mesure de qualité de l'air via une API externe et de les indexer dans une BDD Elasticsearch afin de les visualiser avec Kibana

Le docker-compose est présent dans le dossier test afin de tester le fonctionnement

Image pour le service de récupération des données : kbnhvn/datafetcher:latest
ENV :
    DATABASE_URL: *base de données elasticsearch*
    INDEX_NAME: *nom de l'index*
    EXTERNAL_API_URL: *url de l'API externe*


