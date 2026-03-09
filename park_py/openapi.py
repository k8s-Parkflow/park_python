from __future__ import annotations

from django.http import HttpRequest, HttpResponse, JsonResponse


def openapi_json_view(request: HttpRequest) -> JsonResponse:
    base_url = request.build_absolute_uri("/").rstrip("/")
    return JsonResponse(
        {
            "openapi": "3.0.3",
            "info": {
                "title": "Parking Command Service API",
                "version": "1.0.0",
                "description": "parking-command-service write API documentation.",
            },
            "servers": [{"url": base_url}],
            "paths": {
                "/api/parking/entry": {
                    "post": {
                        "summary": "Create parking entry record",
                        "operationId": "createParkingEntry",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["vehicle_num", "slot_id"],
                                        "properties": {
                                            "vehicle_num": {"type": "string", "example": "69가-3455"},
                                            "slot_id": {"type": "integer", "example": 33},
                                            "entry_at": {
                                                "type": "string",
                                                "format": "date-time",
                                                "example": "2026-03-10T09:00:00+09:00",
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "201": {
                                "description": "Created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/ParkingRecordSnapshot"}
                                    }
                                },
                            },
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                            "409": {"$ref": "#/components/responses/Conflict"},
                        },
                    }
                },
                "/api/parking/exit": {
                    "post": {
                        "summary": "Create parking exit record",
                        "operationId": "createParkingExit",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["vehicle_num"],
                                        "properties": {
                                            "vehicle_num": {"type": "string", "example": "69가-3455"},
                                            "exit_at": {
                                                "type": "string",
                                                "format": "date-time",
                                                "example": "2026-03-10T12:10:00+09:00",
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/ParkingRecordSnapshot"}
                                    }
                                },
                            },
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                            "409": {"$ref": "#/components/responses/Conflict"},
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "ParkingRecordSnapshot": {
                        "type": "object",
                        "properties": {
                            "history_id": {"type": "integer", "example": 101},
                            "vehicle_num": {"type": "string", "example": "69가3455"},
                            "slot_id": {"type": "integer", "example": 33},
                            "status": {"type": "string", "example": "PARKED"},
                            "entry_at": {
                                "type": "string",
                                "format": "date-time",
                                "example": "2026-03-10T09:00:00+09:00",
                            },
                            "exit_at": {
                                "type": "string",
                                "format": "date-time",
                                "nullable": True,
                                "example": None,
                            },
                        },
                    },
                    "ErrorResponse": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "example": "bad_request"},
                                    "message": {"type": "string", "example": "잘못된 요청입니다."},
                                    "details": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                },
                            }
                        },
                    },
                },
                "responses": {
                    "BadRequest": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "NotFound": {
                        "description": "Not Found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                    "Conflict": {
                        "description": "Conflict",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            },
        }
    )


def swagger_ui_view(_request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Parking Command Service Swagger</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
    />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = function () {
        window.ui = SwaggerUIBundle({
          url: "/api/docs/openapi.json",
          dom_id: "#swagger-ui",
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout",
          deepLinking: true,
        });
      };
    </script>
  </body>
</html>
        """.strip(),
        content_type="text/html; charset=utf-8",
    )
