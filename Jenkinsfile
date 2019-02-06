project = "nexus-constructor"

// Set number of old artefacts to keep.
properties([
    buildDiscarder(
        logRotator(
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '5',
            daysToKeepStr: '',
            numToKeepStr: ''
        )
    )
])

centos = 'essdmscdm/centos7-build-node:3.1.0'

container_name = "${project}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
sh_cmd = "/usr/bin/scl enable rh-python35 -- /bin/bash -e"

def get_win10_pipeline() {
return {
    node('windows10') {
      // Use custom location to avoid Win32 path length issues
      ws('c:\\jenkins\\') {
      cleanWs()
      dir("${project}") {
        stage("win10: Checkout") {
          checkout scm
        }  // stage

	stage("win10: Setup") {
          bat """if exist _build rd /q /s _build
	    mkdir _build
	    python3 -m pip install -r requirements.txt
	    """
	} // stage
        stage("win10: Build Executable") {
          bat """cd _build
	    python3 ..\\setup.py build_exe"""
        }  // stage

      }  // dir
      }
} // node
} // return
} // def

def get_macos_pipeline() {
return {
node('macos') {

cleanWs()
dir("${project}/code") {

 stage('macOS: Checkout') {
 try {
    checkout scm
 } catch (e) {
    failure_function(e, 'MacOSX / Checkout failed')
 }
 }

 stage('macOS: Setup'){
    sh "python3 -m pip install -r requirements.txt"
 }

 stage('macOS: Build Executable') {
    sh "python3 setup.py build_exe"
 }
} // dir
} // node
} // return
} // def

def get_linux_pipeline() {
return {
node("docker") {
stage('Centos7: Build Executable'){
    sh "docker exec ${container_name} ${sh_cmd} -c \" cd ${project} && build_env/bin/python3 setup.py build_exe  \" "
}
} // node
} // return
} // def

node("docker") {
    cleanWs()
    dir("${project}") {
        stage("Checkout") {
            scm_vars = checkout scm
        }
    }
    try {
        image = docker.image(centos)
        container = image.run("\
            --name ${container_name} \
            --tty \
            --network=host \
            --env http_proxy=${env.http_proxy} \
            --env https_proxy=${env.https_proxy} \
        ")
        sh "docker cp ${project} ${container_name}:/home/jenkins/${project}"
        sh """docker exec --user root ${container_name} ${sh_cmd} -c \"
            chown -R jenkins.jenkins /home/jenkins/${project}
        \""""

        stage("Create virtualenv") {
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                python -m venv build_env
            \""""
        }

        stage("Install requirements") {
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/pip --proxy ${https_proxy} install --upgrade pip
                build_env/bin/pip --proxy ${https_proxy} install -r requirements.txt
                build_env/bin/pip --proxy ${https_proxy} install codecov
                \""""
        }

        stage("Build Executables") {

        def builders = [:]
        builders['centos7'] = get_linux_pipeline()
        builders['macOS'] = get_macos_pipeline()
        builders['windows10'] = get_win10_pipeline()

        parallel builders

        } // stage

        stage("Run Linter") {
        sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/flake8
            \""""
        }

        stage("Run tests") {
            def testsError = null
            try {
                sh """docker exec ${container_name} ${sh_cmd} -c \"
                    cd ${project}
                    build_env/bin/pytest ./tests --ignore=build_env --junitxml=/home/jenkins/${project}/test_results.xml
                \""""
                }
                catch(err) {
                    testsError = err
                    currentBuild.result = 'FAILURE'
                }
            sh """docker exec ${container_name} ${sh_cmd} -c \"
                cd ${project}
                build_env/bin/pytest --cov=geometry_constructor --cov-report=xml
                \""""
            withCredentials([string(credentialsId: 'nexus-constructor-codecov-token', variable: 'TOKEN')]) {
                sh """docker exec ${container_name} ${sh_cmd} -c \"
                    cd ${project}
                    build_env/bin/codecov -t ${TOKEN} -c ${scm_vars.GIT_COMMIT} -f coverage.xml
                    \""""
            }
            sh "docker cp ${container_name}:/home/jenkins/${project}/test_results.xml test_results.xml"
            junit "test_results.xml"
        }
    } finally {
        container.stop()
    }
}
