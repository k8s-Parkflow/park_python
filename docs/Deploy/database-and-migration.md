# DB 연결과 마이그레이션

## 1. 현재 코드의 DB 구조

현재 프로젝트는 Django multi-database router 를 사용한다.

- `default` -> `orchestration-service`
- `vehicle` -> `vehicle-service`
- `zone` -> `zone-service`
- `parking_command` -> `parking-command-service`
- `parking_query` -> `parking-query-service`

즉, 코드 기준으로는 서비스별 DB 분리를 이미 전제하고 있다.

## 2. 운영 환경에서 권장하는 DB 방식

운영에서는 SQLite 대신 외부 RDB 를 사용한다.

추천 방식:

- MariaDB 인스턴스 1개 + 논리 DB 5개
- 또는 서비스별 별도 MariaDB 인스턴스 5개

DB 이름 예시:

- `autoe_orchestration`
- `autoe_vehicle`
- `autoe_zone`
- `autoe_parking_command`
- `autoe_parking_query`

로컬 검증용 구성:

- `docker-compose.mariadb.yml`
- `docker/mariadb/init/001-create-service-databases.sql`

로컬 실행 예시:

```bash
docker compose -f docker-compose.mariadb.yml up -d
docker exec autoe-mariadb mariadb -uroot -proot -e "SHOW DATABASES;"
```

기본 포트:

- 호스트 `3306`
- 컨테이너 `3306`

## 3. 권장 settings_prod.py 구조

운영용 설정 파일을 새로 두고, 서비스별 DB 접속 정보를 환경 변수로 주입하는 방식을 추천한다.

예시:

```python
from park_py.settings import *

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["ORCHESTRATION_DB_NAME"],
        "USER": os.environ["ORCHESTRATION_DB_USER"],
        "PASSWORD": os.environ["ORCHESTRATION_DB_PASSWORD"],
        "HOST": os.environ["ORCHESTRATION_DB_HOST"],
        "PORT": os.environ.get("ORCHESTRATION_DB_PORT", "3306"),
    },
    "vehicle": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["VEHICLE_DB_NAME"],
        "USER": os.environ["VEHICLE_DB_USER"],
        "PASSWORD": os.environ["VEHICLE_DB_PASSWORD"],
        "HOST": os.environ["VEHICLE_DB_HOST"],
        "PORT": os.environ.get("VEHICLE_DB_PORT", "3306"),
    },
    "zone": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["ZONE_DB_NAME"],
        "USER": os.environ["ZONE_DB_USER"],
        "PASSWORD": os.environ["ZONE_DB_PASSWORD"],
        "HOST": os.environ["ZONE_DB_HOST"],
        "PORT": os.environ.get("ZONE_DB_PORT", "3306"),
    },
    "parking_command": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["PARKING_COMMAND_DB_NAME"],
        "USER": os.environ["PARKING_COMMAND_DB_USER"],
        "PASSWORD": os.environ["PARKING_COMMAND_DB_PASSWORD"],
        "HOST": os.environ["PARKING_COMMAND_DB_HOST"],
        "PORT": os.environ.get("PARKING_COMMAND_DB_PORT", "3306"),
    },
    "parking_query": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["PARKING_QUERY_DB_NAME"],
        "USER": os.environ["PARKING_QUERY_DB_USER"],
        "PASSWORD": os.environ["PARKING_QUERY_DB_PASSWORD"],
        "HOST": os.environ["PARKING_QUERY_DB_HOST"],
        "PORT": os.environ.get("PARKING_QUERY_DB_PORT", "3306"),
    },
}
```

## 4. Kubernetes Secret 예시

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: autoe-db-secret
type: Opaque
stringData:
  ORCHESTRATION_DB_HOST: mysql
  ORCHESTRATION_DB_NAME: autoe_orchestration
  ORCHESTRATION_DB_USER: autoe
  ORCHESTRATION_DB_PASSWORD: change-me
  VEHICLE_DB_HOST: mysql
  VEHICLE_DB_NAME: autoe_vehicle
  VEHICLE_DB_USER: autoe
  VEHICLE_DB_PASSWORD: change-me
  ZONE_DB_HOST: mysql
  ZONE_DB_NAME: autoe_zone
  ZONE_DB_USER: autoe
  ZONE_DB_PASSWORD: change-me
  PARKING_COMMAND_DB_HOST: mysql
  PARKING_COMMAND_DB_NAME: autoe_parking_command
  PARKING_COMMAND_DB_USER: autoe
  PARKING_COMMAND_DB_PASSWORD: change-me
  PARKING_QUERY_DB_HOST: mysql
  PARKING_QUERY_DB_NAME: autoe_parking_query
  PARKING_QUERY_DB_USER: autoe
  PARKING_QUERY_DB_PASSWORD: change-me
```

## 5. 마이그레이션 실행 방식

현재 저장소에는 서비스별 DB 마이그레이션 명령이 이미 있다.

- 전체 실행: `python manage.py migrate_msa_databases`
- 단일 서비스 실행: `python manage.py migrate_service_db --service <service>`

추천 방식은 Deployment 기동 전에 Kubernetes Job 으로 한 번 실행하는 것이다.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: autoe-migrate
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: your-registry/autoe-backend:latest
          command: ["python", "manage.py", "migrate_msa_databases"]
          envFrom:
            - secretRef:
                name: autoe-db-secret
```

## 6. 배포 순서

1. DB 생성
2. Secret 반영
3. 마이그레이션 Job 실행
4. 내부 gRPC 파드 배포
5. HTTP gateway 배포

## 7. 주의사항

- 마이그레이션은 애플리케이션 기동과 분리하는 편이 안전하다.
- 각 서비스는 자기 DB alias 에 대해서만 마이그레이션이 적용된다.
- 서비스 간 테이블을 조인하는 운영 쿼리는 지양해야 한다.
