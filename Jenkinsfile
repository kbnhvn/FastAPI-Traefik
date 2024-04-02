pipeline {
environment { // Declaration of environment variables
DOCKER_ID = "kbnhvn" // replace this with your docker-id
DOCKER_IMAGE_DATA = "datafetcher"
DOCKER_IMAGE_WEB_DEV = "web-dev"
DOCKER_IMAGE_WEB_PROD = "web-prod"
DOCKER_IMAGE_WEBSERVER = "webserver"
EXTERNAL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/qualite-de-lair-france/records?limit=-1"
DEV_HOSTNAME = "dev.fastapi-traefik.cloudns.ch"
PROD_HOSTNAME = "prod.fastapi-traefik.cloudns.ch"
DOCKER_TAG = "v.${BUILD_ID}.0" // we will tag our images with the current build in order to increment the value by 1 with each new build

// SECRETS
SECRET_KEY = credentials("SECRET_KEY")
PGADMIN_CREDENTIALS = credentials("PGADMIN_CREDENTIALS")
DB_CREDENTIALS = credentials("DB_CREDENTIALS")
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
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:$DOCKER_TAG -f ./baseProject/Dockerfile.prod ./baseProject
                        sleep 6
                        '''
                    }
                }
            }
            stage(' Build webserver Image') {
                steps {
                    script {
                        sh '''
                        docker rm -f $DOCKER_IMAGE_WEBSERVER || true
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE_WEBSERVER:$DOCKER_TAG ./loginPage
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
                docker container rm -f db || true
                docker container rm -f elasticsearch || true

                # Création reseaux
                docker network create pg_network || true
                docker network create es_network || true

                #Lancement d'un container postgres pour l'environnement de test des images web
                docker run -d \
                --name db --network pg_network\
                -v postgres_data:/var/lib/postgresql/data/ \
                -e POSTGRES_USER=fastapi_traefik \
                -e POSTGRES_PASSWORD=fastapi_traefik \
                -e POSTGRES_DB=fastapi_traefik \
                -p 5433:5432 \
                postgres:15-alpine

                #Lancement d'un container elasticsearch pour l'environnement de test de l'image datafetcher
                docker run -d \
                --name elasticsearch --network es_network \
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
                        docker run -d --name $DOCKER_IMAGE_DATA --network es_network \
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
                        docker run -d -p 8005:8000 --name $DOCKER_IMAGE_WEB_DEV --network pg_network \
                        -e DATABASE_URL=postgresql://fastapi_traefik:fastapi_traefik@db:5432/fastapi_traefik \
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
                        docker run -d -p 8006:80 --name $DOCKER_IMAGE_WEB_PROD --network pg_network \
                        -e DATABASE_URL=postgresql://fastapi_traefik:fastapi_traefik@db:5432/fastapi_traefik \
                        $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:$DOCKER_TAG
                        sleep 10
                        '''
                    }
                }
            }
            stage(' Run webserver Container') {
                steps {
                    script {
                        sh '''
                        docker run -d -p 8003:80 --name $DOCKER_IMAGE_WEBSERVER \
                        $DOCKER_ID/$DOCKER_IMAGE_WEBSERVER:$DOCKER_TAG
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
                        curl localhost:8005/health
                        '''
                    }
                }
            }
            stage(' Test web_prod Container') {
                steps {
                    script {
                        sh '''
                        curl localhost:8006/health
                        '''
                    }
                }
            }
            stage(' Test webserver Container') {
                steps {
                    script {
                        sh '''
                        curl localhost:8003/
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
                        # Création du tag latest pour installation locale
                        docker tag $DOCKER_ID/$DOCKER_IMAGE_DATA:$DOCKER_TAG $DOCKER_ID/$DOCKER_IMAGE_DATA:latest
                        docker push $DOCKER_ID/$DOCKER_IMAGE_DATA:latest
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
                        # Création du tag latest pour installation locale
                        docker tag $DOCKER_ID/$DOCKER_IMAGE_WEB_DEV:$DOCKER_TAG $DOCKER_ID/$DOCKER_IMAGE_WEB_DEV:latest
                        docker push $DOCKER_ID/$DOCKER_IMAGE_WEB_DEV:latest
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
                        # Création du tag latest pour installation locale
                        docker tag $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:$DOCKER_TAG $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:latest
                        docker push $DOCKER_ID/$DOCKER_IMAGE_WEB_PROD:latest
                        '''
                    }
                }
            }
            stage(' Push webserver Image') {
                steps {
                    script {
                        sh '''
                        docker login -u $DOCKER_ID -p $DOCKER_PASS
                        docker push $DOCKER_ID/$DOCKER_IMAGE_WEBSERVER:$DOCKER_TAG
                        # Création du tag latest pour installation locale
                        docker tag $DOCKER_ID/$DOCKER_IMAGE_WEBSERVER:$DOCKER_TAG $DOCKER_ID/$DOCKER_IMAGE_WEBSERVER:latest
                        docker push $DOCKER_ID/$DOCKER_IMAGE_WEBSERVER:latest
                        '''
                    }
                }
            }

        }

    }

stage('Check branch'){
    steps {
        script {
            def branchName = sh(script: "git branch -a --contains HEAD | grep 'remotes/origin' | sed 's|remotes/origin/||' | head -n 1", returnStdout: true).trim()
            env.BRANCH_NAME = branchName
            echo "Branche actuelle: ${env.BRANCH_NAME}"
        }
    }
}

stage('Deploiement en dev'){
        environment
        {
        KUBECONFIG = credentials("config") // we retrieve  kubeconfig from secret file called config saved on jenkins
        FULL_REPOSITORY = "${env.DOCKER_ID}/${env.DOCKER_IMAGE_WEB_DEV}"
        NAMESPACE = "dev"
        ROLE_NAME = "traefik-role-dev"
        ROLE_BINDING_NAME = "traefik-role-binding-dev"
        }
        when 
        {
            branch "develop" // Cette condition s'assure que le stage ne s'exécute que sur la branche develop
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
                yq eval ".namespace = strenv(NAMESPACE)" -i values.yml

                # Modification des tags
                yq eval ".web.tag = strenv(DOCKER_TAG)" -i values.yml
                yq eval ".data.tag = strenv(DOCKER_TAG)" -i values.yml
                yq eval ".nginx.tag = strenv(DOCKER_TAG)" -i values.yml

                # Modification du repository pour l'image web
                yq eval ".web.repository = strenv(FULL_REPOSITORY)" -i values.yml

                # Modification du ingress host
                yq eval ".ingress.host = strenv(DEV_HOSTNAME)" -i values.yml

                # Modification du ClusterRole name
                yq eval ".role.name = strenv(ROLE_NAME)" -i values.yml
                yq eval ".roleBinding.name = strenv(ROLE_BINDING_NAME)" -i values.yml

                #Ajout des secrets
                yq eval ".secrets.web.secret_key = strenv(SECRET_KEY)" -i values.yml
                yq eval ".secrets.pgadmin.email = strenv(PGADMIN_CREDENTIALS_USR)" -i values.yml
                yq eval ".secrets.pgadmin.password = strenv(PGADMIN_CREDENTIALS_PSW)" -i values.yml
                yq eval ".secrets.db.user = strenv(DB_CREDENTIALS_USR)" -i values.yml
                yq eval ".secrets.db.password = strenv(DB_CREDENTIALS_PSW)" -i values.yml

                helm upgrade --install app fastapi-traefik --values=values.yml --namespace $NAMESPACE
                '''
                }
            }

        }
stage('Deploiement en prod'){
        environment
        {
        KUBECONFIG = credentials("config") // we retrieve  kubeconfig from secret file called config saved on jenkins
        FULL_REPOSITORY = "${env.DOCKER_ID}/${env.DOCKER_IMAGE_WEB_PROD}"
        NAMESPACE = "prod"
        ROLE_NAME = "traefik-role-prod"
        ROLE_BINDING_NAME = "traefik-role-binding-prod"
        }
        when 
        {
            branch "master" // Cette condition s'assure que le stage ne s'exécute que sur la branche master
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
                yq eval ".namespace = strenv(NAMESPACE)" -i values.yml

                # Modification des tags
                yq eval ".web.tag = strenv(DOCKER_TAG)" -i values.yml
                yq eval ".data.tag = strenv(DOCKER_TAG)" -i values.yml
                yq eval ".nginx.tag = strenv(DOCKER_TAG)" -i values.yml

                # Modification du repository pour l'image web
                yq eval ".web.repository = strenv(FULL_REPOSITORY)" -i values.yml

                # Modification du ingress host
                yq eval ".ingress.host = strenv(PROD_HOSTNAME)" -i values.yml

                # Modification du ClusterRole name
                yq eval ".role.name = strenv(ROLE_NAME)" -i values.yml
                yq eval ".roleBinding.name = strenv(ROLE_BINDING_NAME)" -i values.yml

                #Ajout des secrets
                yq eval ".secrets.web.secret_key = strenv(SECRET_KEY)" -i values.yml
                yq eval ".secrets.pgadmin.email = strenv(PGADMIN_CREDENTIALS_USR)" -i values.yml
                yq eval ".secrets.pgadmin.password = strenv(PGADMIN_CREDENTIALS_PSW)" -i values.yml
                yq eval ".secrets.db.user = strenv(DB_CREDENTIALS_USR)" -i values.yml
                yq eval ".secrets.db.password = strenv(DB_CREDENTIALS_PSW)" -i values.yml

                # ------ Modifications relatives aux ENV de l'image PROD uniquement ----
                yq eval 'del(.web.command)' -i values.yml
                yq eval 'del(.web.args)' -i values.yml
                
                helm upgrade --install app fastapi-traefik --values=values.yml --namespace $NAMESPACE
                '''
                }
            }
        }
}
}
