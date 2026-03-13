pipeline {
    agent {
        kubernetes {
            // Kaniko를 사용하여 도커 이미지 빌드 (쿠버네티스 환경 최적화)
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    command:
    - sleep
    args:
    - 999d
    volumeMounts:
    - name: kaniko-secret
      mountPath: /kaniko/.docker
  volumes:
  - name: kaniko-secret
    secret:
      secretName: dockerhub-secret
      items:
        - key: .dockerconfigjson
          path: config.json
"""
        }
    }

    environment {
        // 도커 허브 이미지 기본 경로 (지환님의 계정명 반영)
        DOCKER_REGISTRY = "hyungdongjo"
        // 배포용 매니페스트 레포지토리 주소
        DEPLOY_REPO_URL = "https://github.com/k8s-Parkflow/Deploy.git"
    }

    stages {
        stage('Checkout') {
            steps {
                // 현재 백엔드 소스 코드 및 이전 커밋 로그를 위해 플래그 추가
                checkout scm
                script {
                    // 이전 커밋과 비교하기 위해 fetch 수행
                    sh "git fetch --tags --force --progress -- origin main"
                }
            }
        }

        stage('Determine Changes') {
            steps {
                script {
                    // 변경된 파일 목록 추출 (이전 성공 커밋 기준, 없으면 이전 커밋 HEAD~1)
                    def changedFiles = ""
                    try {
                        changedFiles = sh(script: "git diff --name-only HEAD~1 HEAD", returnStdout: true).trim()
                    } catch (Exception e) {
                        echo "Git diff 실패, 모든 서비스를 빌드 대상으로 간주합니다."
                        changedFiles = "all"
                    }
                    
                    echo "Changed Files: \n${changedFiles}"

                    // 서비스별 디렉토리 및 이미지 명칭 매핑
                    def serviceMap = [
                        "orchestration": [dir: "services/orchestration-service", image: "parking-orchestration-app"],
                        "command"      : [dir: "services/parking-command-service", image: "parking-command-app"],
                        "query"        : [dir: "services/parking-query-service", image: "parking-query-app"],
                        "vehicle"      : [dir: "services/vehicle-service", image: "parking-vehicle-app"],
                        "zone"         : [dir: "services/zone-service", image: "parking-zone-app"]
                    ]

                    // 빌드 대상 목록을 담을 리스트
                    env.TARGET_SERVICES = ""

                    // 공통 코드가 변경되었는지 확인 (shared, requirements.txt, Dockerfile 등)
                    def isCommonChanged = changedFiles.contains("shared/") || 
                                          changedFiles.contains("requirements.txt") ||
                                          changedFiles == "all" ||
                                          changedFiles.contains("manage.py") ||
                                          changedFiles.contains("park_py/")

                    if (isCommonChanged) {
                        echo "공통 코드가 변경되어 5개 서비스 전체를 빌드합니다."
                        env.TARGET_SERVICES = serviceMap.keySet().join(",")
                    } else {
                        def targets = []
                        serviceMap.each { key, value ->
                            if (changedFiles.contains(value.dir)) {
                                targets.add(key)
                            }
                        }
                        if (targets.isEmpty()) {
                            echo "✅ 마이크로서비스 코드 변경사항이 없습니다. CI를 종료합니다."
                            currentBuild.result = 'SUCCESS'
                            return
                        }
                        env.TARGET_SERVICES = targets.join(",")
                    }
                    echo "🌟 빌드 및 배포 대상 서비스: ${env.TARGET_SERVICES}"
                }
            }
        }

        stage('Build and Push Images') {
            when {
                expression { return env.TARGET_SERVICES && env.TARGET_SERVICES != "" }
            }
            steps {
                container('kaniko') {
                    script {
                        def targets = env.TARGET_SERVICES.split(",")
                        def serviceMap = [
                            "orchestration": [dockerfile: "services/orchestration-service/Dockerfile", image: "parking-orchestration-app"],
                            "command"      : [dockerfile: "services/parking-command-service/Dockerfile", image: "parking-command-app"],
                            "query"        : [dockerfile: "services/parking-query-service/Dockerfile", image: "parking-query-app"],
                            "vehicle"      : [dockerfile: "services/vehicle-service/Dockerfile", image: "parking-vehicle-app"],
                            "zone"         : [dockerfile: "services/zone-service/Dockerfile", image: "parking-zone-app"]
                        ]
                        
                        targets.each { target ->
                            def srv = serviceMap[target]
                            def imageFullPath = "${env.DOCKER_REGISTRY}/${srv.image}"
                            def buildContext = "${env.WORKSPACE}"
                            // 컨텍스트는 루트로 유지한채 해당 서비스의 Dockerfile 사용
                            echo "🚀 Building and Pushing: ${target} (${imageFullPath}:v${env.BUILD_NUMBER})"
                            
                            sh """
                            /kaniko/executor \\
                              --context "${buildContext}" \\
                              --dockerfile "${buildContext}/${srv.dockerfile}" \\
                              --destination "${imageFullPath}:v${env.BUILD_NUMBER}" \\
                              --destination "${imageFullPath}:latest"
                            """
                        }
                    }
                }
            }
        }

        stage('Update Manifests') {
            when {
                expression { return env.TARGET_SERVICES && env.TARGET_SERVICES != "" }
            }
            steps {
                script {
                    sh "rm -rf deploy-repo"
                    
                    withCredentials([usernamePassword(credentialsId: 'github-token', passwordVariable: 'GIT_TOKEN', usernameVariable: 'GIT_USER')]) {
                        dir('deploy-repo') {
                            git credentialsId: 'github-token', 
                                url: "${env.DEPLOY_REPO_URL}",
                                branch: 'main'
                            
                            def targets = env.TARGET_SERVICES.split(",")
                            def serviceMap = [
                                "orchestration": "parking-orchestration-app",
                                "command"      : "parking-command-app",
                                "query"        : "parking-query-app",
                                "vehicle"      : "parking-vehicle-app",
                                "zone"         : "parking-zone-app"
                            ]
                            
                            targets.each { target ->
                                def imageName = serviceMap[target]
                                def fileName = "backend/${target}-deployment.yaml"
                                if (fileExists(fileName)) {
                                    // image: hyungdongjo/parking-command-app:latest 등을 v{BUILD_NUMBER}로 치환
                                    sh "sed -i 's|image: ${env.DOCKER_REGISTRY}/${imageName}:.*|image: ${env.DOCKER_REGISTRY}/${imageName}:v${env.BUILD_NUMBER}|g' ${fileName}"
                                    echo "✅ ${fileName}의 이미지를 v${env.BUILD_NUMBER}로 업데이트했습니다."
                                } else {
                                    echo "⚠️ ${fileName} 파일을 찾을 수 없어 건너뜁니다."
                                }
                            }
                            
                            sh """
                                git config user.email "jenkins-bot@parkflow.local"
                                git config user.name "Jenkins-CI-Bot"
                                git add .
                                
                                if ! git diff --staged --quiet; then
                                    git commit -m "Deploy: Updated services [${env.TARGET_SERVICES}] to v${env.BUILD_NUMBER} [skip ci]"
                                    git remote set-url origin https://${GIT_USER}:${GIT_TOKEN}@github.com/k8s-Parkflow/Deploy.git
                                    git push origin main
                                else
                                    echo "변경사항이 없어 푸시를 생략합니다."
                                fi
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                if (env.TARGET_SERVICES && env.TARGET_SERVICES != "") {
                    def msg = "✅ [성공] CI 빌드 및 배포 완료\n- 대상: ${env.TARGET_SERVICES}\n- 빌드 번호: #${env.BUILD_NUMBER}"
                    echo msg
                    slackSend(color: "good", message: msg)
                } else {
                    echo "🎉 코드가 변경되지 않아 스킵되었습니다."
                }
            }
        }
        failure {
            script {
                def msg = "❌ [실패] CI 빌드 및 배포 실패\n- 빌드 번호: #${env.BUILD_NUMBER}\n젠킨스 로그를 확인해 주세요."
                echo msg
                slackSend(color: "danger", message: msg)
            }
        }
    }
}
