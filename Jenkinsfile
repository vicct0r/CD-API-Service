pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'CD-API-Service'
        VENV_DIR = "${env.WORKSPACE}/venv"
        PYTHON = "/usr/bin/python3"  // Ajuste o caminho conforme necessário
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
                    """
                }
            }
        }
        
        stage('Run Tests with Coverage') {
            steps {
                script {
                    sh """
                    source ${VENV_DIR}/bin/activate
                    python manage.py test --testrunner=xmlrunner.extra.djangotestrunner.XMLTestRunner \
                                         --no-input --verbosity=2
                    coverage run manage.py test
                    coverage xml -o coverage.xml
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
                    source ${VENV_DIR}/bin/activate
                    coverage report
                    coverage html
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
                        source ${VENV_DIR}/bin/activate
                        ${SCANNER_HOME}/bin/sonar-scanner
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
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