# 🏢 ParkPython BE

현대오토에버 모빌리티 SW 스쿨 미니프로젝트의 일환으로, 주차장 여석 조회 서비스입니다.

<br>
<img width="685" height="300" alt="프로젝트 구조" src="https://github.com/user-attachments/assets/d9595d79-37af-4ec8-b1c3-89002a0a6d8d" />

## 📋 개요

ParkPython은 이용자들의 Zone 별 주차장 여석 조회를 지원하는 Django 기반의 MSA 백엔드 서버입니다.
주차장의 전체 / Zone 별 여석 조회, 차량의 현재 위치 조회 및 입/출차를 지원합니다.

## 🛠 기술 스택

### 코어 프레임워크
- **Python + Django 4.2.29** - 백엔드 애플리케이션 전반 구현
- **Django REST Framework** - RESTful API 개발
- **gRPC + Protocol Buffers** - 마이크로서비스 간 내부 통신
- **MSA 구조** - 조회, 명령, 차량, 구역, 오케스트레이션 서비스 분리

### 데이터베이스
- **MariaDB** - 관계형 데이터베이스
- **Django ORM** - 데이터 모델링 및 영속성 관리

### API 문서화
- **drf-spectacular + Swagger UI** - OpenAPI 기반 API 문서화

### CI/CD 및 인프라
- **Docker** - 컨테이너 기반 배포
- **Kubernetes** - 컨테이너 오케스트레이션
- **Jenkins** - CI 파이프라인 및 이미지 빌드 자동화
- **ArgoCD** - GitOps 기반 배포 자동화

### 자동화 도구
- **Go Bot** - 데이터 입력 및 삭제 자동화


## 🏗 아키텍처

<img width="685" height="364" alt="스크린샷 2026-03-13 오전 9 27 11" src="https://github.com/user-attachments/assets/e8b36eb7-32f1-4b0d-b5ca-65857a04b9a6" />


## 📚 API 문서

어플리케이션 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/docs/swagger
