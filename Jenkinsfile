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
        // 도커 허브 이미지 경로 (지환님의 계정명 반영)
        DOCKER_IMAGE = "hyungdongjo/parking-backend"
        // 배포용 매니페스트 레포지토리 주소
        DEPLOY_REPO_URL = "https://github.com/k8s-Parkflow/Deploy.git"
    }

    stages {
        stage('Checkout') {
            steps {
                // 현재 백엔드 소스 코드 체크아웃
                checkout scm
            }
        }

        stage('Build and Push Image') {
            steps {
                container('kaniko') {
                    // 빌드 번호(v1, v2...)와 latest 태그로 이미지 푸시
                    sh """
                    /kaniko/executor \
                      --context "${env.WORKSPACE}" \
                      --dockerfile Dockerfile \
                      --destination ${DOCKER_IMAGE}:v${env.BUILD_NUMBER} \
                      --destination ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        stage('Update Manifests') {
            steps {
                script {
                    // 기존 배포 폴더 정리 및 새로 클론
                    sh "rm -rf deploy-repo"
                    
                    // 깃허브 토큰 인증 정보 로드
                    withCredentials([usernamePassword(credentialsId: 'github-token', passwordVariable: 'GIT_TOKEN', usernameVariable: 'GIT_USER')]) {
                        dir('deploy-repo') {
                            git credentialsId: 'github-token', 
                                url: "${env.DEPLOY_REPO_URL}",
                                branch: 'main'
                            
                            // 1. 업데이트할 5개 MSA 서비스 리스트
                            def targetServices = [
                                "orchestration", 
                                "command", 
                                "query", 
                                "vehicle", 
                                "zone"
                            ]
                            
                            // 2. 각 서비스의 deployment.yaml 파일 내 이미지 태그 수정
                            targetServices.each { serviceName ->
                                def fileName = "backend/${serviceName}-deployment.yaml"
                                if (fileExists(fileName)) {
                                    sh "sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:v${env.BUILD_NUMBER}|g' ${fileName}"
                                    echo "✅ ${fileName}의 이미지를 v${env.BUILD_NUMBER}로 업데이트했습니다."
                                } else {
                                    echo "⚠️ ${fileName} 파일을 찾을 수 없어 건너뜁니다."
                                }
                            }
                            
                            // 3. 변경 사항 커밋 및 푸시
                            sh """
                                git config user.email "jenkins-bot@parkflow.local"
                                git config user.name "Jenkins-CI-Bot"
                                git add .
                                # 변경사항이 있을 때만 실행 (무한루프 방지 [skip ci] 포함)
                                if ! git diff --staged --quiet; then
                                    git commit -m "Deploy: backend v${env.BUILD_NUMBER} updated to all 5 services [skip ci]"
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
            echo "🎉 성공: 모든 서비스의 이미지가 v${env.BUILD_NUMBER}로 업데이트되어 배포되었습니다!"
        }
        failure {
            echo "❌ 실패: 빌드 또는 업데이트 중 문제가 발생했습니다. 로그를 확인해 주세요."
        }
    }
}
