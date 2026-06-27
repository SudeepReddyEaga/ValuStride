pipeline {

    agent any

    environment {
        IMAGE_NAME = "sudeepkumarreddyeaga/valustride"
        IMAGE_TAG  = "latest"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/SudeepReddyEaga/ValuStride.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -e
                    docker build -t $IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    sh '''
                        set -e

                        echo "Docker User = $DOCKER_USER"

                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        docker push $IMAGE_NAME:$IMAGE_TAG

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    set -e

                    export KUBECONFIG=/var/jenkins_home/.kube/config

                    kubectl apply -f k8s/deployment.yml
                    kubectl apply -f k8s/service.yml

                    kubectl rollout restart deployment valustride-deployment
                    kubectl rollout status deployment/valustride-deployment
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    export KUBECONFIG=/var/jenkins_home/.kube/config

                    echo "===== Pods ====="
                    kubectl get pods -o wide

                    echo "===== Services ====="
                    kubectl get svc

                    echo "===== Deployments ====="
                    kubectl get deployments
                '''
            }
        }
    }

    post {

        success {
            echo '✅ ValuStride CI/CD Pipeline Executed Successfully!'
        }

        failure {
            echo '❌ Pipeline Failed!'
        }

        always {
            cleanWs()
        }
    }
}