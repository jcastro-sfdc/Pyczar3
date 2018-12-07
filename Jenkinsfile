#!groovy
@Library('sfci-pipeline-sharedlib@v0.14.19') _
import net.sfdc.dci.BuildUtils
import net.sfdc.dci.GitHubUtils


def envDef = [ buildImage: 'ops0-artifactrepo1-0-prd.data.sfdc.net/mobile/sfci-python36:f3c3a84' ]
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
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'sonarlogin')]) {
        }
    }

    stage('Sonar') {
        // Scan code and send results to https://sonarqube.eng.sfdc.net/
        def sonarArgs = ''
        if (BuildUtils.isPullRequestBuild(env)) {
            def githubParams = GitHubUtils.getDefaultGithubParams(this)
            def pullRequestNumber = env.CHANGE_ID
            echo "CHANGE_ID is ${pullRequestNumber}"

            // we need to pull out:
            // baseRef - where you intend to (e.g. "master")
            // the head ref - the name of your branch (e.g. "myfeature")
            // pr number - an integer.
            def graphQL = """
                query {
                    repository(owner: "${githubParams.org}", name: "${githubParams.repo}") {
                        pullRequest(number: ${pullRequestNumber}){
                            baseRef { name }
                            headRef { name }
                            number
                        }
                    }
                }"""
            // GraphQL Query returns dictionary-like structure to mirror the response from Gitsoma.
            def response = GitHubUtils.executeGithubGraphQLQuery(this, graphQL).repository.pullRequest
            //pullrequest.branch: The name of your PR
            //Ex: sonar.pullrequest.branch=feature/my-new-feature

            //sonar.pullrequest.key
            // Unique identifier of your PR. Must correspond to the key of the PR in GitHub or TFS.
            //E.G.: sonar.pullrequest.key=5

            //sonar.pullrequest.base
            //The long-lived branch into which the PR will be merged.
            //Default: master
            //E.G.: sonar.pullrequest.base=master
            sonarArgs = "-Dsonar.pullrequest.branch=${response.headRef.name} -Dsonar.pullrequest.key=${response.number} -Dsonar.pullrequest.base=${response.baseRef.name} -Dsonar.pullrequest.provider=github"
        } else {
            def branchName = BuildUtils.getCurrentBranch(this)
            sonarArgs = "-Dsonar.branch.name=${branchName}"
        }
        
        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_LOGIN')]) {
            sh "sonar-scanner -Dsonar.host.url=https://sonarqube.eng.sfdc.net/ -Dsonar.login=${SONAR_LOGIN} ${sonarArgs}"
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
