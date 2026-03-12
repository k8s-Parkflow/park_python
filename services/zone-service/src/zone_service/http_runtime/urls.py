from zone_service.urls import urlpatterns

from park_py.error_handling import handler404 as json_handler404
from park_py.error_handling import handler500 as json_handler500


handler404 = json_handler404
handler500 = json_handler500
