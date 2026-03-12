from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "park_py.settings_zone")

application = get_wsgi_application()
