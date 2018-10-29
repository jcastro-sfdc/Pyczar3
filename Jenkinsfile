#!groovy
@Library('sfci-pipeline-sharedlib@v0.14.19') _
import net.sfdc.dci.BuildUtils

def envDef = [ buildImage: 'ops0-artifactrepo1-0-prd.data.sfdc.net/mobile/sfci-python36:ca84abf' ]
def BUILD_NUMBER=env.BUILD_NUMBER

executePipeline(envDef) {
    buildInit()

    stage('checkout') {
        checkout scm
    }

    stage('install tools') {
        sh 'sudo /opt/sfdc/python36/bin/pip install --proxy http://public0-proxy1-0-prd.data.sfdc.net:8080 -U tox'
    }

    stage('test') {
        withEnv(['HTTP_PROXY=http://public0-proxy1-0-prd.data.sfdc.net:8080',
                 'HTTPS_PROXY=http://public0-proxy1-0-prd.data.sfdc.net:8080',
                 'NO_PROXY=.force.com,.salesforce.com']) {
            ansiColor('xterm') {
                sh 'tox'
            }
        }
    }

    stage('reports') {
        junit 'junit.xml'
        withEnv(['NO_PROXY=.slb.sfdc.net']) {
            sh 'curl -s --insecure https://codecov.moe.prd-sam.prd.slb.sfdc.net/bash | bash -s - -t 1e886856-66ac-4b26-ae79-9f1680987fe6 -s Mobile/Pyczar3 -v -Z -F unittests -f coverage.xml -U "--insecure"'
        }
    }

    if (!BuildUtils.isPullRequestBuild(env)) {
      stage('publish') {
        withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'sfci-nexus', usernameVariable: 'ARTIFACTORY_USERNAME', passwordVariable: 'ARTIFACTORY_TOKEN']]) {
            pypi_path = '~/.pypirc'
            sh """
                echo '[distutils]' > ${pypi_path}
                echo 'index-servers = python-dev' >> ${pypi_path}
                echo '' >> ${pypi_path}
                echo '[python-dev]' >> ${pypi_path}
                echo 'repository: https://ops0-artifactrepo1-0-prd.data.sfdc.net/artifactory/api/pypi/python-dev' >> ${pypi_path}
                echo 'username: ${ARTIFACTORY_USERNAME}' >> ${pypi_path}
                echo 'password: ${ARTIFACTORY_TOKEN}' >> ${pypi_path}
            """
        }
        sh 'python setup.py bdist_wheel upload -r python-dev'
      }
    }
}
