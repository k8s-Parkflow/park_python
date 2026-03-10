def build_openapi_schema(*, base_url: str) -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Park Py API",
            "version": "1.0.0",
            "description": "orchestration-service gateway and internal participant APIs",
        },
        "servers": [{"url": base_url}],
        "paths": {
            "/api/v1/parking/entries": {
                "post": {
                    "tags": ["gateway"],
                    "summary": "입차 SAGA 시작",
                    "parameters": [
                        {
                            "name": "Idempotency-Key",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["vehicle_num", "slot_id", "requested_at"],
                                    "properties": {
                                        "vehicle_num": {"type": "string"},
                                        "slot_id": {"type": "integer"},
                                        "requested_at": {"type": "string", "format": "date-time"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "입차 완료"},
                        "409": {"description": "보상 완료"},
                        "500": {"description": "보상 취소"},
                    },
                }
            },
            "/api/v1/parking/exits": {
                "post": {
                    "tags": ["gateway"],
                    "summary": "출차 SAGA 시작",
                    "parameters": [
                        {
                            "name": "Idempotency-Key",
                            "in": "header",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["vehicle_num", "requested_at"],
                                    "properties": {
                                        "vehicle_num": {"type": "string"},
                                        "requested_at": {"type": "string", "format": "date-time"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "출차 완료"},
                        "409": {"description": "보상 완료"},
                        "500": {"description": "보상 취소"},
                    },
                }
            },
            "/api/v1/saga-operations/{operation_id}": {
                "get": {
                    "tags": ["gateway"],
                    "summary": "사가 상태 조회",
                    "parameters": [
                        {
                            "name": "operation_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "사가 상태"}},
                }
            },
            "/internal/vehicles/{vehicle_num}": {
                "get": {
                    "tags": ["internal"],
                    "summary": "차량 조회",
                    "parameters": [
                        {
                            "name": "vehicle_num",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "차량 정보"}},
                }
            },
            "/internal/zones/slots/{slot_id}/entry-policy": {
                "get": {
                    "tags": ["internal"],
                    "summary": "입차 정책 조회",
                    "parameters": [
                        {
                            "name": "slot_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {"200": {"description": "입차 정책"}},
                }
            },
            "/internal/parking-command/entries": {
                "post": {"tags": ["internal"], "summary": "입차 command", "responses": {"201": {"description": "입차 처리"}}}
            },
            "/internal/parking-command/entries/compensations": {
                "post": {"tags": ["internal"], "summary": "입차 보상", "responses": {"200": {"description": "입차 취소"}}}
            },
            "/internal/parking-command/exits": {
                "post": {"tags": ["internal"], "summary": "출차 command", "responses": {"200": {"description": "출차 처리"}}}
            },
            "/internal/parking-command/exits/compensations": {
                "post": {"tags": ["internal"], "summary": "출차 보상", "responses": {"200": {"description": "출차 복구"}}}
            },
            "/internal/parking-query/current-parking/{vehicle_num}": {
                "get": {"tags": ["internal"], "summary": "현재 주차 조회", "responses": {"200": {"description": "현재 주차 상태"}}}
            },
            "/internal/parking-query/entries": {
                "post": {"tags": ["internal"], "summary": "입차 projection", "responses": {"200": {"description": "projection 반영"}}}
            },
            "/internal/parking-query/entries/compensations": {
                "post": {"tags": ["internal"], "summary": "입차 projection 보상", "responses": {"200": {"description": "projection 원복"}}}
            },
            "/internal/parking-query/exits": {
                "post": {"tags": ["internal"], "summary": "출차 projection", "responses": {"200": {"description": "projection 반영"}}}
            },
            "/internal/parking-query/exits/compensations": {
                "post": {"tags": ["internal"], "summary": "출차 projection 보상", "responses": {"200": {"description": "projection 복구"}}}
            },
        },
    }
