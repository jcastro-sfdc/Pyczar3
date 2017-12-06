#!groovy
@Library('sfci-pipeline-sharedlib@v0.9.0') _
import net.sfdc.dci.BuildUtils

def envDef = [ buildImage: 'ops0-artifactrepo1-0-prd.data.sfdc.net/mobile/sfci-python36:ca84abf' ]
node {
    def BUILD_NUMBER=env.BUILD_NUMBER

    executePipeline(envDef) {

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
                sh 'tox'
            }
        }

        stage('reports') {
            junit 'junit.xml'
        }

    }
}
