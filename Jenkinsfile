pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                ws('/home/rhel/helm/Prasad/test-project') {
                    echo 'Building Docker Image'
                    sh 'docker build -t myapp-test .'
                    sh 'docker stop myapp-test || true'
                    sh 'docker rm -f myapp-test || true'
                    sh 'docker run -d -p 5000:5000 --name myapp-test myapp-test'
                }
            }
        }
        stage('Helm deploying'){
            steps {
                ws('/home/rhel/helm/Prasad/test-project') {
                    echo 'Updating deployment'
                    sh '''
                        helm upgrade --install myapp "./Helm chart/DocBrief" \
                          --set image.repository=myapp-test \
                          --set image.tag=latest \
                          --set image.pullPolicy=IfNotPresent \
                          --set rolloutNonce=$(date +%s)
                    '''
                }
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}