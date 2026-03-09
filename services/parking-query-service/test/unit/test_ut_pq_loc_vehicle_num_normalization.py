from django.test import SimpleTestCase

from park_py.tests.support.current_location import CurrentLocationModuleLoaderMixin


class VehicleNumNormalizationUnitTests(CurrentLocationModuleLoaderMixin, SimpleTestCase):
    def test_should_normalize_vehicle_num__when_formatted(self) -> None:
        # Given
        module = self.load_query_service_module()

        # When
        normalized = module.normalize_vehicle_num("69가-3455 ")

        # Then
        self.assertEqual(normalized, "69가3455")
