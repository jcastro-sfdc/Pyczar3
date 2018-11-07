#!groovy
@Library('sfci-pipeline-sharedlib@v0.14.19') _
import net.sfdc.dci.BuildUtils

def envDef = [ buildImage: 'ops0-artifactrepo1-0-prd.data.sfdc.net/mobile/sfci-python36:19697aa' ]
def BUILD_NUMBER=env.BUILD_NUMBER
def releaseParameters = {
    parameters([
        booleanParam( defaultValue: false,
                      description: 'Do you want to release?',
                      name: 'RELEASE')
    ])
}
env.RELEASE_BRANCHES = ['master']

executePipeline(envDef) {
    buildInit()

    stage('Checkout') {
        checkout scm
    }

    stage('Test') {
        withEnv(['HTTP_PROXY=http://public0-proxy1-0-prd.data.sfdc.net:8080',
                 'HTTPS_PROXY=http://public0-proxy1-0-prd.data.sfdc.net:8080',
                 'NO_PROXY=.force.com,.salesforce.com']) {
            ansiColor('xterm') {
                sh 'tox'
            }
        }
    }

    stage('Reports') {
        junit 'junit.xml'
        withEnv(['NO_PROXY=.slb.sfdc.net']) {
            ansiColor('xterm') {
                sh 'curl -s https://codecov.moe.prd-sam.prd.slb.sfdc.net/bash | bash -s - -Z -F unittests -f coverage.xml'
            }
        }
    }

    if (BuildUtils.isReleaseBuild(env) && params.RELEASE) {
      stage('Publish') {
        sh '/opt/sfdc/python36/bin/pip install --user --proxy http://public0-proxy1-0-prd.data.sfdc.net:8080 -U setuptools wheel twine'
        sh '/opt/sfdc/python36/bin/python3 setup.py sdist bdist_wheel'

        withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'sfci-docker', usernameVariable: 'TWINE_USERNAME', passwordVariable: 'TWINE_PASSWORD']]) {
            sh '~/.local/bin/twine upload --repository-url https://ops0-artifactrepo1-0-prd.data.sfdc.net/artifactory/api/pypi/python-dev dist/*'
        }
      }
    }

    stage('GUS Compliance'){
         git2gus()
    }
}
