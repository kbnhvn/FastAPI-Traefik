pipeline {
environment { // Declaration of environment variables
DOCKER_ID = "kbnhvn" // replace this with your docker-id
DOCKER_IMAGE_DATA = "datafetcher"
DOCKER_IMAGE_WEB_DEV = "web-dev"
DOCKER_IMAGE_WEB_PROD = "web-prod"
EXTERNAL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/qualite-de-lair-france/records?limit=-1"
DEV_HOSTNAME = "dev.fastapi-traefik.cloudns.ch"
PROD_HOSTNAME = "prod.fastapi-traefik.cloudns.ch"
DOCKER_TAG = "v.${BUILD_ID}.0" // we will tag our images with the current build in order to increment the value by 1 with each new build
}
agent any // Jenkins will be able to select all available agents
stages {
    stage(' Docker Build'){ // docker build images stage
        parallel {
            stage(' Build data Image') {
                steps {
                    script {
                        sh '''
                        docker rm -f $DOCKER_IMAGE_DATA || true
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE_DATA:$DOCKER_TAG ./datas
                        sleep 6
                        '''
                    }
                }
            }
            stage(' Build web-dev Image') {
                steps {
                    script {
                        sh '''
                        docker rm -f $DOCKER_IMAGE_WEB_DEV || true
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE_WEB_DEV:$DOCKER_TAG ./baseProject
                        sleep 6
                        '''
                    }
                }
            }
            stage(' Build web-prod Image') {
                steps {
                    script {
                        sh '''
                        docker rm -f $DOCKER_IMAGE_WEB_PROD || true
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:$DOCKER_TAG -f ./baseProject/Dockerfile.prod
                        sleep 6
                        '''
                    }
                }
            }
        }
    }
    stage(' Test environment deployment'){ // docker build DB images
        steps {
            script {
                sh '''
                # Suppression BDD
                docker container rm -f postgres || true
                docker container rm -f elasticsearch || true

                # Création reseaux
                docker network create pg_network || true
                docker network create es_network || true

                #Lancement d'un container postgres pour l'environnement de test des images web
                docker run -d \
                --name postgres --network pg_network\
                -v postgres_data:/var/lib/postgresql/data/ \
                -e POSTGRES_USER=fastapi_traefik \
                -e POSTGRES_PASSWORD=fastapi_traefik \
                -e POSTGRES_DB=fastapi_traefik \
                -p 5433:5432 \
                postgres:15-alpine

                #Lancement d'un container elasticsearch pour l'environnement de test de l'image datafetcher
                docker run -d \
                --name elsaticsearch --network es_network \
                -v elastic_data:/usr/share/elasticsearch/data \
                -e node.name=es \
                -e discovery.type=single-node \
                -p 9200:9200 \
                docker.elastic.co/elasticsearch/elasticsearch:7.5.2
                '''
                }
            }
    }
    stage('Docker run'){ // run containers from our builded images
        parallel {
            stage(' Run data Container') {
                steps {
                    script {
                        sh '''
                        docker run -d --name $DOCKER_IMAGE_DATA --network es_network\
                        -e DATABASE_URL=http://elasticsearch:9200 \
                        -e INDEX_NAME=qualite_air \
                        -e EXTERNAL_API_URL=$EXTERNAL_API_URL \
                        $DOCKER_ID/$DOCKER_IMAGE_DATA:$DOCKER_TAG \
                        sleep 10
                        '''
                    }
                }
            }
            stage(' Run web-dev Container') {
                steps {
                    script {
                        sh '''
                        docker run -d -p 8000:8000 --name $DOCKER_IMAGE_WEB_DEV --network pg_network\
                        -e DATABASE_URL=postgresql://fastapi_traefik:fastapi_traefik@postgres:5432/fastapi_traefik \
                        $DOCKER_ID/$DOCKER_IMAGE_WEB_DEV:$DOCKER_TAG \
                        bash -c 'while !</dev/tcp/db/5432; do sleep 1; done; uvicorn app.main:app --host 0.0.0.0'
                        sleep 10
                        '''
                    }
                }
            }
            stage(' Run web-prod Container') {
                steps {
                    script {
                        sh '''
                        docker run -d -p 8001:80 --name $DOCKER_IMAGE_WEB_PROD --network pg_network\
                        -e DATABASE_URL=postgresql://fastapi_traefik:fastapi_traefik@postgres:5432/fastapi_traefik \
                        $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:$DOCKER_TAG \
                        sleep 10
                        '''
                    }
                }
            }

        }
    }
    stage('Test Acceptance'){ // we launch the curl commands to validate that the containers responds to the request
        parallel {
            stage(' Test data Container') {
                steps {
                    script {
                        sh '''
                        # Test external API url
                        curl $EXTERNAL_API_URL

                        # Test récupération données et enregistrement dans BDD ES
                        curl -X GET http://localhost:9200/qualite_air/_search?pretty=true&size=10
                        '''
                    }
                }
            }
            stage(' Test web_dev Container') {
                steps {
                    script {
                        sh '''
                        curl localhost:8000
                        '''
                    }
                }
            }
            stage(' Test web_prod Container') {
                steps {
                    script {
                        sh '''
                        curl localhost:8001
                        '''
                    }
                }
            }

        }

    }
    stage('Docker Push'){ //we pass the built images to our docker hub account
        environment
        {
            DOCKER_PASS = credentials("DOCKER_HUB_PASS") // we retrieve  docker password from secret text called docker_hub_pass saved on jenkins
        }
        parallel {
            stage(' Push data Image') {
                steps {
                    script {
                        sh '''
                        docker login -u $DOCKER_ID -p $DOCKER_PASS
                        docker push $DOCKER_ID/$DOCKER_IMAGE_DATA:$DOCKER_TAG
                        '''
                    }
                }
            }
            stage(' Push web_dev Image') {
                steps {
                    script {
                        sh '''
                        docker login -u $DOCKER_ID -p $DOCKER_PASS
                        docker push $DOCKER_ID/$DOCKER_IMAGE_WEB_DEV:$DOCKER_TAG
                        '''
                    }
                }
            }
            stage(' Push web_prod Image') {
                steps {
                    script {
                        sh '''
                        docker login -u $DOCKER_ID -p $DOCKER_PASS
                        docker push $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:$DOCKER_TAG
                        '''
                    }
                }
            }

        }

    }

stage('Deploiement en dev'){
        when 
        {
        branch 'develop' // Cette condition s'assure que le stage ne s'exécute que sur la branche develop
        }
        environment
        {
        KUBECONFIG = credentials("config") // we retrieve  kubeconfig from secret file called config saved on jenkins
        NAMESPACE = "dev"
        }
            steps {
                script {
                sh '''
                # Configuration de l'environnement Kubernetes
                rm -Rf .kube
                mkdir .kube
                ls
                cat $KUBECONFIG > .kube/config

                # Préparation des valeurs
                cp fastapi-traefik/values.yaml values.yml
                cat values.yml

                # Modification du namespace
                sed -i "s+namespace.*+namespace: ${NAMESPACE}+g" values.yml

                # Modification du tag pour l'image datafetcher
                sed -i "s+data.tag.*+tag: ${DOCKER_TAG}+g" values.yml

                # Modification des valeurs pour l'image web
                sed -i "s+web.repository.*+repository: ${DOCKER_ID}/${DOCKER_IMAGE_WEB_DEV}+g" values.yml
                sed -i "s+web.tag.*+tag: ${DOCKER_TAG}+g" values.yml

                # Modification du ingress host
                sed -i "s+ingress.host.*+host: ${DEV_HOSTNAME}+g" values.yml

                helm upgrade --install app fastapi-traefik --values=values.yml --namespace $NAMESPACE
                '''
                }
            }

        }
stage('Deploiement en prod'){
        when 
        {
        branch 'master' // Cette condition s'assure que le stage ne s'exécute que sur la branche master
        }
        environment
        {
        KUBECONFIG = credentials("config") // we retrieve  kubeconfig from secret file called config saved on jenkins
        NAMESPACE = "prod"
        }
            steps {
            // Create an Approval Button with a timeout of 15minutes.
            // this require a manuel validation in order to deploy on production environment
                timeout(time: 15, unit: "MINUTES") {
                    input message: 'Do you want to deploy in production ?', ok: 'Yes'
                }

                script {
                sh '''
                # Configuration de l'environnement Kubernetes
                rm -Rf .kube
                mkdir .kube
                ls
                cat $KUBECONFIG > .kube/config

                # Préparation des valeurs
                cp fastapi-traefik/values.yaml values.yml
                cat values.yml

                # Modification du namespace
                sed -i "s+namespace.*+namespace: ${NAMESPACE}+g" values.yml

                # Modification du tag pour l'image datafetcher
                sed -i "s+data.tag.*+tag: ${DOCKER_TAG}+g" values.yml

                # Modification des valeurs pour l'image web
                sed -i "s+web.repository.*+repository: ${DOCKER_ID}/${DOCKER_IMAGE_WEB_PROD}+g" values.yml
                sed -i "s+web.tag.*+tag: ${DOCKER_TAG}+g" values.yml

                # Modification du ingress host
                sed -i "s+ingress.host.*+host: ${PROD_HOSTNAME}+g" values.yml

                # ------ Modifications relatives aux ENV de l'image PROD uniquement ----
                sed -i '/web.command/d' values.yml
                sed -i '/web.arg/d' values.yml
                sed -i "s+web.service.port.*+port: 80+g" values.yml
                sed -i "s+web.service.targetPort.*+targetPort: 80+g" values.yml
                sed -i "s+web.containerPort.*+containerPort: 80+g" values.yml
                
                helm upgrade --install app fastapi-traefik --values=values.yml --namespace $NAMESPACE
                '''
                }
            }

        }
}
}