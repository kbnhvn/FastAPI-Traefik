stage('Test environment deployment') {
    steps {
        script {
            // Supprimer les conteneurs existants s'ils existent
            sh 'docker container rm -f db-container || true'
            sh 'docker container rm -f elasticsearch-container || true'
            
            // Déployer le conteneur pour la base de données PostgreSQL
            sh '''
            docker run -d \
                --name db-container \
                -v postgres_data:/var/lib/postgresql/data/ \
                -e POSTGRES_USER=${DB_USER} \
                -e POSTGRES_PASSWORD=${DB_PASSWORD} \
                -e POSTGRES_DB=${DB_NAME} \
                -p 5432:5432 \
                postgres:${DB_TAG}
            '''
            
            // Déployer le conteneur pour Elasticsearch
            sh '''
            docker run -d \
                --name elasticsearch-container \
                -v elasticsearch_data:/usr/share/elasticsearch/data \
                -p 9200:9200 \
                -p 9300:9300 \
                ${ELASTICSEARCH_IMAGE}
            '''
        }
    }
}

stage('Docker run') {
    parallel {
        stage('Run DB Container') {
            steps {
                script {
                    // Exécute le conteneur pour la base de données PostgreSQL
                    sh '''
                    docker run -d --name db-container --network my_network \
                    -v postgres_data:/var/lib/postgresql/data/ \
                    -e POSTGRES_USER={{ .Values.db.credentials.user }} \
                    -e POSTGRES_PASSWORD={{ .Values.db.credentials.password }} \
                    -e POSTGRES_DB={{ .Values.db.config.db_name }} \
                    -p 5432:5432 \
                    {{ .Values.db.repository }}:{{ .Values.db.tag }}
                    sleep 10
                    '''
                }
            }
        }
        stage('Run Elasticsearch Container') {
            steps {
                script {
                    // Exécute le conteneur pour Elasticsearch
                    sh '''
                    docker run -d --name elasticsearch-container --network my_network \
                    -p 9200:9200 -p 9300:9300 \
                    {{ .Values.elasticsearch.repository }}:{{ .Values.elasticsearch.tag }}
                    sleep 10
                    '''
                }
            }
        }
    }
}

stage('Test Acceptance') {
    parallel {
        stage('Test DB Container') {
            steps {
                script {
                    // Test la disponibilité du conteneur de la base de données PostgreSQL
                    sh 'curl localhost:5432'
                }
            }
        }
        stage('Test Elasticsearch Container') {
            steps {
                script {
                    // Test l'endpoint d'Elasticsearch
                    sh 'curl localhost:9200'
                }
            }
        }
    }
}

stage('Docker Push') {
    environment {
        DOCKER_PASS = credentials("DOCKER_HUB_PASS")
    }
    parallel {
        stage('Push Elasticsearch Image') {
            steps {
                script {
                    // Connexion à Docker Hub et pousser l'image Elasticsearch
                    sh '''
                    docker login -u $DOCKER_ID -p $DOCKER_PASS
                    docker push $DOCKER_ID/$DOCKER_IMAGE_ELASTICSEARCH:$DOCKER_TAG
                    '''
                }
            }
        }
        stage('Push DB Image') {
            steps {
                script {
                    // Connexion à Docker Hub et pousser l'image de la base de données
                    sh '''
                    docker login -u $DOCKER_ID -p $DOCKER_PASS
                    docker push $DOCKER_ID/$DOCKER_IMAGE_DB:$DOCKER_TAG
                    '''
                }
            }
        }
    }
}

stage('Deploy') {
    environment {
        KUBECONFIG = credentials("config") // Récupération du kubeconfig depuis le fichier secret "config" de Jenkins
        NAMESPACE = "dev"
    }
    steps {
        script {
            // Configuration de l'environnement Kubernetes
            sh '''
                rm -Rf .kube
                mkdir .kube
                cat $KUBECONFIG > .kube/config
            '''
            
            // Préparation des valeurs YAML pour Helm
            sh 'cp helm/values.yaml values.yml'
            sh 'cat values.yml'
            
            // Remplacement de la valeur du namespace dans le fichier values.yaml
            sh 'sed -i "s+namespace.*+namespace: ${NAMESPACE}+g" values.yml'
            
            // Remplacement des tags d'image Docker pour les différents services
            sh 'sed -i "s+db.tag.*+tag: ${DOCKER_TAG}+g" values.yml'
            sh 'sed -i "s+elasticsearch.tag.*+tag: ${DOCKER_TAG}+g" values.yml'
            
            // Déploiement de l'application à l'aide de Helm
            sh 'helm upgrade --install app helm --values=values.yml --namespace dev'
        }
    }
}
