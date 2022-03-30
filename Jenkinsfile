#!/usr/bin/env groovy

pipeline {
  agent any

  options {
    timeout(time: 15, unit: 'MINUTES')
  }

  environment {
    ssh_private_key_path = "/var/lib/jenkins/.ssh/id_ecdsa"
    application_name = "mq-to-ldap-service"
    version = "${env.BUILD_ID}"
    workspace = "${env.WORKSPACE}"
    destination_environment = "test"
    build_path = "${env.WORKSPACE}"
  }

  stages {

     stage("Test") {
      steps {
        echo "Running tests..."
        echo sh(returnStdout: true, script: "sh scripts/run-tests.sh").trim()
      }
    }

    stage("Build") {
      steps {
        echo "Building the application. Using ${version} as application version"
        echo sh(returnStdout: true, script: "python3 -m pip install --extra-index-url https://pypi.nmbu.no --user --upgrade nmbu-deploy-script 2>&1").trim()
        echo sh(returnStdout: true, script: "build --application=${application_name} --version=${version} --build-path=${build_path} --push-to-registry 2>&1").trim()
      }
    }

    stage('Deploy') {
      steps {
        echo "Run deployment to ${destination_environment}..."
        echo sh(returnStdout: true, script: "deploy --environment=${destination_environment} --application=${application_name} --version=${version} 2>&1").trim()
      }
    }
  }

  post {

    success {
      // notify users when the Pipeline finishes
      mail to: 'jon.dellnes@nmbu.no',
        subject: "Pipeline ${currentBuild.fullDisplayName} finished successfully",
          body: "The pipeline ${env.BUILD_URL} has finished"
    }
    failure {
      // notify users when the Pipeline fails
      mail to: 'jon.dellnes@nmbu.no',
          subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
          body: "Something is wrong with ${env.BUILD_URL}"
    }
  }

}
