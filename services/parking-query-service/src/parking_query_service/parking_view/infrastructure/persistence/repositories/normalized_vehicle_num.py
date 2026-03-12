from django.db.models import QuerySet, Value
from django.db.models.functions import Replace


def with_normalized_vehicle_num(queryset: QuerySet) -> QuerySet:
    return queryset.annotate(
        normalized_vehicle_num=Replace(
            Replace("vehicle_num", Value("-"), Value("")),
            Value(" "),
            Value(""),
        )
    )
