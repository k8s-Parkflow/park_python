from rest_framework import serializers


class AvailabilityQuerySerializer(serializers.Serializer):
    slot_type = serializers.CharField(required=False)


class TypedAvailabilitySerializer(serializers.Serializer):
    slotType = serializers.CharField()
    availableCount = serializers.IntegerField()


class TotalAvailabilitySerializer(serializers.Serializer):
    availableCount = serializers.IntegerField()


class ErrorBodySerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
    )


class ErrorResponseSerializer(serializers.Serializer):
    error = ErrorBodySerializer()
