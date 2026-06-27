pipeline {

    agent any

    environment {

        IMAGE_NAME = "sudeepkumarreddyeaga/valustride"
        IMAGE_TAG = "latest"

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

                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'

            }
        }

        stage('Push Docker Image') {

            steps {

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'

                    sh 'docker push $IMAGE_NAME:$IMAGE_TAG'

                }

            }

        }

        stage('Deploy to Kubernetes') {

            steps {

                sh '''
                export KUBECONFIG=/var/jenkins_home/.kube/config

                kubectl apply -f k8s/deployment.yaml
                kubectl apply -f k8s/service.yaml

                kubectl rollout restart deployment valustride-deployment
                '''

            }

        }

        stage('Verify Deployment') {

            steps {

                sh '''
                export KUBECONFIG=/var/jenkins_home/.kube/config

                kubectl get pods
                kubectl get svc
                '''

            }

        }

    }

    post {

        success {

            echo 'ValuStride CI/CD Pipeline Executed Successfully!'

        }

        failure {

            echo 'Pipeline Failed!'

        }

    }

}