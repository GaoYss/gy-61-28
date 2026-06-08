from rest_framework import serializers

from .models import AccessDevice, AlarmEvent, DoorOpenLog, VisitorPass


class AccessDeviceSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AccessDevice
        fields = "__all__"


class VisitorPassSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    pass_status_display = serializers.CharField(source="get_pass_status_display", read_only=True)

    class Meta:
        model = VisitorPass
        fields = "__all__"


class AlarmEventSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    alarm_type_display = serializers.CharField(source="get_alarm_type_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlarmEvent
        fields = "__all__"


class DoorOpenLogSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    opener_type_display = serializers.CharField(source="get_opener_type_display", read_only=True)
    credential_method_display = serializers.CharField(source="get_credential_method_display", read_only=True)
    result_display = serializers.CharField(source="get_result_display", read_only=True)

    class Meta:
        model = DoorOpenLog
        fields = "__all__"
