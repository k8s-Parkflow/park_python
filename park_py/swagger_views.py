from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from park_py.openapi import build_openapi_schema


SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Park Py Swagger</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = function () {
        window.ui = SwaggerUIBundle({
          url: "%(schema_url)s",
          dom_id: "#swagger-ui",
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout"
        });
      };
    </script>
  </body>
</html>
"""


@require_GET
def openapi_json(request: HttpRequest) -> JsonResponse:
    base_url = f"{request.scheme}://{request.get_host()}"
    return JsonResponse(build_openapi_schema(base_url=base_url))


@require_GET
def swagger_ui(request: HttpRequest) -> HttpResponse:
    base_url = f"{request.scheme}://{request.get_host()}"
    html = SWAGGER_UI_HTML % {"schema_url": f"{base_url}/openapi.json"}
    return HttpResponse(html)
