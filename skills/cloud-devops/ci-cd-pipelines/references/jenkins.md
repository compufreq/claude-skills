# Jenkins Reference

## Table of Contents
1. Declarative Pipeline
2. Scripted Pipeline
3. Shared Libraries
4. Parallel & Matrix
5. Docker Integration
6. Credentials & Secrets

---

## 1. Declarative Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'node:20-alpine'
            args '-v $HOME/.npm:/root/.npm'  // Cache npm
        }
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds(abortPrevious: true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        CI = 'true'
        REGISTRY = 'registry.example.com'
        IMAGE_NAME = "${REGISTRY}/myapp"
        APP_VERSION = sh(script: 'cat package.json | jq -r .version', returnStdout: true).trim()
    }

    stages {
        stage('Lint') {
            steps {
                sh 'npm ci'
                sh 'npm run lint'
            }
        }

        stage('Test') {
            steps {
                sh 'npm test -- --coverage'
            }
            post {
                always {
                    junit 'junit.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage/cobertura-coverage.xml')]
                }
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def image = docker.build("${IMAGE_NAME}:${env.GIT_COMMIT}")
                    docker.withRegistry("https://${REGISTRY}", 'registry-credentials') {
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }

        stage('Deploy Staging') {
            when {
                branch 'main'
            }
            steps {
                sh "./deploy.sh staging ${env.GIT_COMMIT}"
            }
        }

        stage('Deploy Production') {
            when {
                tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP'
            }
            input {
                message 'Deploy to production?'
                ok 'Deploy'
                submitter 'admin,lead-devs'
            }
            steps {
                sh "./deploy.sh production ${env.GIT_COMMIT}"
            }
        }
    }

    post {
        success {
            slackSend(channel: '#deployments', color: 'good',
                message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} succeeded")
        }
        failure {
            slackSend(channel: '#deployments', color: 'danger',
                message: "🔴 ${env.JOB_NAME} #${env.BUILD_NUMBER} failed")
        }
        always {
            cleanWs()
        }
    }
}
```

---

## 2. Scripted Pipeline

```groovy
// Jenkinsfile (scripted — more flexibility, less structure)
node('linux') {
    try {
        stage('Checkout') {
            checkout scm
        }

        stage('Build & Test') {
            docker.image('node:20').inside {
                sh 'npm ci'
                sh 'npm test'
                sh 'npm run build'
            }
        }

        if (env.BRANCH_NAME == 'main') {
            stage('Docker') {
                def image = docker.build("myapp:${env.GIT_COMMIT}")
                docker.withRegistry('https://registry.example.com', 'registry-creds') {
                    image.push()
                    image.push('latest')
                }
            }

            stage('Deploy') {
                withCredentials([string(credentialsId: 'deploy-token', variable: 'TOKEN')]) {
                    sh "DEPLOY_TOKEN=${TOKEN} ./deploy.sh staging"
                }
            }
        }
    } catch (e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        cleanWs()
    }
}
```

---

## 3. Shared Libraries

### Library Structure
```
vars/                           # Global variables (callable functions)
├── buildApp.groovy             # Call as: buildApp()
├── deployToK8s.groovy          # Call as: deployToK8s(env: 'staging')
└── notifySlack.groovy
src/                            # Groovy classes
├── com/example/pipeline/
│   ├── DockerHelper.groovy
│   └── DeploymentConfig.groovy
resources/                      # Static resources
└── templates/
    └── deployment.yaml
```

### Global Variable (vars/)
```groovy
// vars/buildApp.groovy
def call(Map config = [:]) {
    def nodeVersion = config.get('nodeVersion', '20')
    def testCmd = config.get('testCmd', 'npm test')

    pipeline {
        agent { docker { image "node:${nodeVersion}-alpine" } }
        stages {
            stage('Install') { steps { sh 'npm ci' } }
            stage('Lint') { steps { sh 'npm run lint' } }
            stage('Test') { steps { sh testCmd } }
            stage('Build') { steps { sh 'npm run build' } }
        }
    }
}
```

### Using Shared Library
```groovy
// Jenkinsfile
@Library('my-shared-lib@main') _

buildApp(nodeVersion: '20', testCmd: 'npm run test:ci')
```

### Configure in Jenkins
1. Jenkins → Manage Jenkins → Configure System → Global Pipeline Libraries
2. Name: `my-shared-lib`
3. Source: Git repo URL
4. Default version: `main`

---

## 4. Parallel & Matrix

### Parallel Stages
```groovy
stage('Tests') {
    parallel {
        stage('Unit Tests') {
            agent { docker { image 'node:20' } }
            steps { sh 'npm run test:unit' }
        }
        stage('Integration Tests') {
            agent { docker { image 'node:20' } }
            steps { sh 'npm run test:integration' }
        }
        stage('E2E Tests') {
            agent { label 'e2e-runner' }
            steps { sh 'npm run test:e2e' }
        }
    }
}
```

### Matrix (Jenkins 2.x)
```groovy
stage('Cross-Platform Test') {
    matrix {
        axes {
            axis {
                name 'PLATFORM'
                values 'linux', 'windows', 'mac'
            }
            axis {
                name 'NODE_VERSION'
                values '18', '20', '22'
            }
        }
        excludes {
            exclude {
                axis { name 'PLATFORM'; values 'mac' }
                axis { name 'NODE_VERSION'; values '18' }
            }
        }
        stages {
            stage('Test') {
                agent { label "${PLATFORM}" }
                steps {
                    sh "nvm use ${NODE_VERSION} && npm test"
                }
            }
        }
    }
}
```

---

## 5. Docker Integration

```groovy
// Build inside Docker
pipeline {
    agent {
        docker {
            image 'maven:3.9-eclipse-temurin-21'
            args '-v $HOME/.m2:/root/.m2'
        }
    }
    stages {
        stage('Build') { steps { sh 'mvn clean package' } }
    }
}

// Build Docker image
stage('Docker Build') {
    steps {
        script {
            def image = docker.build(
                "myapp:${env.BUILD_NUMBER}",
                "--build-arg APP_VERSION=${APP_VERSION} -f Dockerfile ."
            )
            docker.withRegistry('https://ghcr.io', 'ghcr-credentials') {
                image.push()
                image.push('latest')
            }
        }
    }
}

// Multi-stage agent
pipeline {
    agent none                  // No default agent
    stages {
        stage('Build') {
            agent { docker { image 'node:20' } }
            steps { sh 'npm ci && npm run build' }
        }
        stage('Deploy') {
            agent { label 'deploy-node' }
            steps { sh './deploy.sh' }
        }
    }
}
```

---

## 6. Credentials & Secrets

```groovy
// String credential
withCredentials([string(credentialsId: 'api-token', variable: 'TOKEN')]) {
    sh "curl -H 'Authorization: Bearer $TOKEN' https://api.example.com"
}

// Username/password
withCredentials([usernamePassword(
    credentialsId: 'docker-hub',
    usernameVariable: 'DOCKER_USER',
    passwordVariable: 'DOCKER_PASS'
)]) {
    sh "docker login -u $DOCKER_USER -p $DOCKER_PASS"
}

// SSH key
withCredentials([sshUserPrivateKey(
    credentialsId: 'deploy-ssh',
    keyFileVariable: 'SSH_KEY',
    usernameVariable: 'SSH_USER'
)]) {
    sh "ssh -i $SSH_KEY $SSH_USER@server ./deploy.sh"
}

// File credential
withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
    sh 'kubectl apply -f deployment.yaml'
}

// Multiple credentials
withCredentials([
    string(credentialsId: 'aws-key', variable: 'AWS_ACCESS_KEY_ID'),
    string(credentialsId: 'aws-secret', variable: 'AWS_SECRET_ACCESS_KEY'),
]) {
    sh 'aws s3 sync ./build s3://my-bucket/'
}
```

### Credential Types
- **Secret text**: API tokens, passwords
- **Username with password**: Docker Hub, registries
- **SSH Username with private key**: Server access
- **Certificate**: Client certificates
- **Secret file**: kubeconfig, service account JSON
- **AWS Credentials**: AWS access/secret keys



---
