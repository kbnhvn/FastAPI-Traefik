import os
from datetime import datetime
from elasticsearch import AsyncElasticsearch
import httpx
import asyncio

# Configuration Elasticsearch
es = AsyncElasticsearch(
    hosts=[os.getenv('DATABASE_URL') ],
    http_auth=(os.getenv('DATABASE_USER'), os.getenv('DATABASE_PASSWORD')),
    use_ssl=True,
    verify_certs=True
)

# ----- Fonctions de validation/transformation/préparation des données ----- #

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S+00:00").isoformat()
    except ValueError:
        return None

def validate_data(data):
    validated_results = []
    for result in data["results"]:
        # Formatage date
        result["measurements_lastupdated"] = format_date(result["measurements_lastupdated"])
        if not result["measurements_lastupdated"]:
            continue 

        # Vérifiez la présence des champs essentiels
        if result["coordinates"]["lon"] is None or result["coordinates"]["lat"] is None:
            continue 

        validated_results.append(result)
    
    return validated_results

def prepare_for_elasticsearch(validated_results):
    for result in validated_results:
        # Formatage en 'geo_point' compatible avec Elasticsearch
        result["location"] = {
            "lat": result["coordinates"]["lat"],
            "lon": result["coordinates"]["lon"]
        }
        del result["coordinates"]
        
    return validated_results


# Récupération des données => Sera lancée via un cronjob kubernetes
async def fetch_data_and_index():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/qualite-de-lair-france")
            if response.status_code == 200:
                data = response.json()
            else:
                print(f"Erreur lors de la récupération des données : {response.status_code}")
                return
    except httpx.HTTPError as e:
        print(f"Erreur lors de la requête HTTP : {e}")
        return
    
    # Validation et formatage données
    validated_data = validate_data(data)
    documents_to_index = prepare_for_elasticsearch(validated_data)

    # Indexage des données dans Elasticsearch
    try:
        for document in documents_to_index:
            await es.index(index="qualite_air", document=document)
    except Exception as e:
        print(f"Erreur lors de l'indexation dans Elasticsearch : {e}")

# Pour lancer le script 
if __name__ == "__main__":
    asyncio.run(fetch_data_and_index())
