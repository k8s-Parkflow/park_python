import re

from django import forms


VEHICLE_NUM_PATTERN = re.compile(r"^\d{2,3}[가-힣]\d{4}$")


class CurrentLocationQueryForm(forms.Form):
    vehicle_num = forms.CharField(required=True)

    def clean_vehicle_num(self) -> str:
        vehicle_num = self.cleaned_data["vehicle_num"]
        normalized_vehicle_num = vehicle_num.replace("-", "").replace(" ", "")
        if not VEHICLE_NUM_PATTERN.fullmatch(normalized_vehicle_num):
            raise forms.ValidationError("지원하지 않는 차량 번호 형식입니다.")
        return normalized_vehicle_num
