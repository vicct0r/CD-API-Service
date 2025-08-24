pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'CD-API-Service'
        VENV_DIR = "${env.WORKSPACE}/venv"
        PYTHON = "/usr/bin/python3"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/vicct0r/CD-API-Service.git'
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                script {
                    sh """
                    ${PYTHON} -m venv ${VENV_DIR}
                    ${VENV_DIR}/bin/pip install --upgrade pip
                    ${VENV_DIR}/bin/pip install -r requirements.txt
                    ${VENV_DIR}/bin/pip install pytest pytest-django
                    """
                }
            }
        }
        
        stage('Run Tests with Coverage') {
            steps {
                script {
                    sh """
                    # Configurar variáveis de ambiente do Django
                    export DJANGO_SETTINGS_MODULE=config.settings.local
                    
                    # Executar testes com pytest (gera relatório JUnit)
                    ${VENV_DIR}/bin/pytest --junitxml=test-results.xml --tb=short -v
                    
                    # Executar coverage (usando manage.py para compatibilidade com Django)
                    ${VENV_DIR}/bin/coverage run --source=. manage.py test
                    ${VENV_DIR}/bin/coverage xml -o coverage.xml
                    """
                }
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                script {
                    sh """
                    ${VENV_DIR}/bin/coverage report
                    ${VENV_DIR}/bin/coverage html
                    """
                }
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
        
        stage('SonarQube Analysis') {
            environment {
                SCANNER_HOME = tool 'SONAR6.2' 
            }
            steps {
                withSonarQubeEnv('sonarserver') {
                    script {
                        sh """
                        ${SCANNER_HOME}/bin/sonar-scanner
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}