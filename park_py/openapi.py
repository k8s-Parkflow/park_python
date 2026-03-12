from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


def build_openapi_schema(*, server_url: str = "/") -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "AutoE API",
            "version": "1.0.0",
            "description": "parking-command public API and orchestration gateway/internal APIs",
        },
        "servers": [{"url": server_url}],
        "paths": {
            "/zones/{zoneId}/slots": {
                "get": {
                    "tags": ["parking-query"],
                    "summary": "존별 슬롯 목록 조회",
                    "parameters": [
                        {
                            "name": "zoneId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "존별 슬롯 목록"},
                        "404": {"description": "존을 찾을 수 없음"},
                    },
                }
            },
            "/api/parking/entry": {
                "post": {
                    "tags": ["parking-command"],
                    "summary": "Create parking entry record",
                    "responses": {
                        "201": {"description": "Created"},
                        "400": {"description": "Bad Request"},
                        "404": {"description": "Not Found"},
                        "409": {"description": "Conflict"},
                    },
                }
            },
            "/api/parking/exit": {
                "post": {
                    "tags": ["parking-command"],
                    "summary": "Create parking exit record",
                    "responses": {
                        "200": {"description": "OK"},
                        "400": {"description": "Bad Request"},
                        "404": {"description": "Not Found"},
                        "409": {"description": "Conflict"},
                    },
                }
            },
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
                    "responses": {"200": {"description": "차량 정보"}},
                }
            },
            "/internal/zones/slots/{slot_id}/entry-policy": {
                "get": {
                    "tags": ["internal"],
                    "summary": "입차 정책 조회",
                    "responses": {"200": {"description": "입차 정책"}},
                }
            },
            "/internal/parking-command/entries": {
                "post": {
                    "tags": ["internal"],
                    "summary": "입차 command",
                    "responses": {"201": {"description": "입차 처리"}},
                }
            },
            "/internal/parking-command/entries/compensations": {
                "post": {
                    "tags": ["internal"],
                    "summary": "입차 보상",
                    "responses": {"200": {"description": "입차 취소"}},
                }
            },
            "/internal/parking-command/exits": {
                "post": {
                    "tags": ["internal"],
                    "summary": "출차 command",
                    "responses": {"200": {"description": "출차 처리"}},
                }
            },
            "/internal/parking-command/exits/compensations": {
                "post": {
                    "tags": ["internal"],
                    "summary": "출차 보상",
                    "responses": {"200": {"description": "출차 복구"}},
                }
            },
            "/internal/parking-query/current-parking/{vehicle_num}": {
                "get": {
                    "tags": ["internal"],
                    "summary": "현재 주차 조회",
                    "responses": {"200": {"description": "현재 주차 상태"}},
                }
            },
            "/internal/parking-query/entries": {
                "post": {
                    "tags": ["internal"],
                    "summary": "입차 projection",
                    "responses": {"200": {"description": "projection 반영"}},
                }
            },
            "/internal/parking-query/entries/compensations": {
                "post": {
                    "tags": ["internal"],
                    "summary": "입차 projection 보상",
                    "responses": {"200": {"description": "projection 원복"}},
                }
            },
            "/internal/parking-query/exits": {
                "post": {
                    "tags": ["internal"],
                    "summary": "출차 projection",
                    "responses": {"200": {"description": "projection 반영"}},
                }
            },
            "/internal/parking-query/exits/compensations": {
                "post": {
                    "tags": ["internal"],
                    "summary": "출차 projection 보상",
                    "responses": {"200": {"description": "projection 복구"}},
                }
            },
        },
    }


def openapi_json_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse(build_openapi_schema())


@ensure_csrf_cookie
def swagger_ui_view(_request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AutoE Swagger</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
    />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      function getCookie(name) {
        const cookieValue = document.cookie
          .split(";")
          .map((item) => item.trim())
          .find((item) => item.startsWith(name + "="));
        return cookieValue ? decodeURIComponent(cookieValue.split("=").slice(1).join("=")) : null;
      }

      window.onload = function () {
        window.ui = SwaggerUIBundle({
          url: "/api/docs/openapi.json",
          dom_id: "#swagger-ui",
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout",
          deepLinking: true,
          requestInterceptor: (request) => {
            const csrfToken = getCookie("csrftoken");
            request.credentials = "same-origin";

            if (csrfToken && !["GET", "HEAD", "OPTIONS", "TRACE"].includes((request.method || "GET").toUpperCase())) {
              request.headers["X-CSRFToken"] = csrfToken;
            }

            return request;
          },
        });
      };
    </script>
  </body>
</html>
        """.strip(),
        content_type="text/html; charset=utf-8",
    )
