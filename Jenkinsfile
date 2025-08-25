pipeline {
    agent any
    environment {
        VENV = 'venv'
        DJANGO_SETTINGS_MODULE = 'config.settings.local'
        DATABASE_URL = 'sqlite:///db.sqlite3'
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/vicct0r/CD-API-Service.git'
            }
        }

        stage('Setup Environment') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    python3 -m venv $VENV
                    . $VENV/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Testing...'
                sh '''
                    $VENV/bin/python manage.py test
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Running SonarQube analysis...'
                withSonarQubeEnv('sonarserver') {
                    script {
                        def scannerHome = tool 'SONAR6.2'  // nome cadastrado em "Global Tool Configuration"
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=CD-API-Service \
                              -Dsonar.sources=. \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.login=$SONAR_AUTH_TOKEN
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'BUILD DONE.'
        }
        success {
            echo 'SUCCESS.'
        }
        failure {
            echo 'FAILED.'
        }
    }
}
