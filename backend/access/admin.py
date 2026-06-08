from django.contrib import admin

from .models import AccessDevice, AlarmEvent, DoorOpenLog, VisitorPass


@admin.register(AccessDevice)
class AccessDeviceAdmin(admin.ModelAdmin):
    list_display = ("device_code", "name", "location", "status", "last_heartbeat")
    search_fields = ("device_code", "name", "location")
    list_filter = ("status",)


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = ("visitor_name", "host_name", "device", "visit_time", "pass_status")
    search_fields = ("visitor_name", "phone", "host_name")
    list_filter = ("pass_status", "device")


@admin.register(AlarmEvent)
class AlarmEventAdmin(admin.ModelAdmin):
    list_display = ("alarm_type", "level", "device", "status", "occurred_at", "handled_by")
    search_fields = ("title", "description", "handled_by")
    list_filter = ("alarm_type", "level", "status")


@admin.register(DoorOpenLog)
class DoorOpenLogAdmin(admin.ModelAdmin):
    list_display = ("device", "opener_name", "opener_type", "credential_method", "result", "opened_at")
    search_fields = ("opener_name", "failure_reason")
    list_filter = ("result", "opener_type", "credential_method", "device")
