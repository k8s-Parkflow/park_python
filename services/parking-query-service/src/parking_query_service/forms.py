import re

from django import forms

from parking_query_service.vehicle_num import normalize_vehicle_num


VEHICLE_NUM_PATTERN = re.compile(r"^\d{2,3}[가-힣]\d{4}$")


class CurrentLocationQueryForm(forms.Form):
    vehicle_num = forms.CharField(required=True)

    def clean_vehicle_num(self) -> str:
        vehicle_num = self.cleaned_data["vehicle_num"]
        normalized_vehicle_num = normalize_vehicle_num(vehicle_num)
        if not VEHICLE_NUM_PATTERN.fullmatch(normalized_vehicle_num):
            raise forms.ValidationError("지원하지 않는 차량 번호 형식입니다.")
        return normalized_vehicle_num
