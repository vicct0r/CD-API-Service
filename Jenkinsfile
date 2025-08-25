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
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Run Tests') {
            steps {
                echo 'Testing...'
                $VENV/bin/python manage.py test
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