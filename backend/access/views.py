import csv
from io import StringIO

from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccessDevice, AlarmEvent, DoorOpenLog, VisitorPass
from .serializers import AccessDeviceSerializer, AlarmEventSerializer, DoorOpenLogSerializer, VisitorPassSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = AccessDevice.objects.all()
    serializer_class = AccessDeviceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "device_code", "location"]
    ordering_fields = ["device_code", "last_heartbeat", "status"]


class VisitorPassViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorPassSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["visitor_name", "phone", "host_name", "reason"]
    ordering_fields = ["visit_time", "created_at", "pass_status"]

    def get_queryset(self):
        queryset = VisitorPass.objects.select_related("device")
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(pass_status=status_value)
        return queryset


class AlarmViewSet(viewsets.ModelViewSet):
    serializer_class = AlarmEventSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "handled_by"]
    ordering_fields = ["occurred_at", "level", "status"]

    def get_queryset(self):
        queryset = AlarmEvent.objects.select_related("device")
        status_value = self.request.query_params.get("status")
        level = self.request.query_params.get("level")
        alarm_type = self.request.query_params.get("alarm_type")
        if status_value:
            queryset = queryset.filter(status=status_value)
        if level:
            queryset = queryset.filter(level=level)
        if alarm_type:
            queryset = queryset.filter(alarm_type=alarm_type)
        return queryset


class DoorLogViewSet(viewsets.ModelViewSet):
    serializer_class = DoorOpenLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["opener_name", "failure_reason", "device__name", "device__location"]
    ordering_fields = ["opened_at", "result", "opener_type"]

    def get_queryset(self):
        queryset = DoorOpenLog.objects.select_related("device", "visitor_pass")
        result = self.request.query_params.get("result")
        opener_type = self.request.query_params.get("opener_type")
        keyword = self.request.query_params.get("keyword")
        start_time = self.request.query_params.get("start_time")
        end_time = self.request.query_params.get("end_time")
        device = self.request.query_params.get("device")
        if result:
            queryset = queryset.filter(result=result)
        if opener_type:
            queryset = queryset.filter(opener_type=opener_type)
        if keyword:
            queryset = queryset.filter(
                Q(opener_name__icontains=keyword)
                | Q(device__name__icontains=keyword)
                | Q(device__location__icontains=keyword)
            )
        if start_time:
            queryset = queryset.filter(opened_at__gte=start_time)
        if end_time:
            queryset = queryset.filter(opened_at__lte=end_time)
        if device:
            queryset = queryset.filter(device_id=device)
        return queryset

    @action(detail=False, methods=["get"])
    def export(self, request):
        queryset = self.get_queryset()
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["时间", "人员", "类型", "设备", "开门方式", "结果", "说明"])
        for log in queryset:
            writer.writerow([
                timezone.localtime(log.opened_at).strftime("%Y-%m-%d %H:%M:%S"),
                log.opener_name,
                log.get_opener_type_display(),
                log.device.name,
                log.get_credential_method_display(),
                log.get_result_display(),
                log.failure_reason or "-",
            ])
        response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="door_logs.csv"'
        return response


class StatsView(APIView):
    def get(self, request):
        today = timezone.localdate()
        return Response(
            {
                "devices_total": AccessDevice.objects.count(),
                "devices_online": AccessDevice.objects.filter(status=AccessDevice.Status.ONLINE).count(),
                "visitors_by_status": {
                    "pending": VisitorPass.objects.filter(pass_status=VisitorPass.PassStatus.PENDING).count(),
                    "approved": VisitorPass.objects.filter(pass_status=VisitorPass.PassStatus.APPROVED).count(),
                    "rejected": VisitorPass.objects.filter(pass_status=VisitorPass.PassStatus.REJECTED).count(),
                    "expired": VisitorPass.objects.filter(pass_status=VisitorPass.PassStatus.EXPIRED).count(),
                },
                "open_alarms": AlarmEvent.objects.exclude(status=AlarmEvent.Status.RESOLVED).count(),
                "alarms_by_type": list(
                    AlarmEvent.objects.values("alarm_type").annotate(count=Count("id")).order_by("alarm_type")
                ),
                "today_success_logs": DoorOpenLog.objects.filter(
                    result=DoorOpenLog.Result.SUCCESS,
                    opened_at__date=today,
                ).count(),
                "logs_by_method": list(
                    DoorOpenLog.objects.values("credential_method").annotate(count=Count("id")).order_by("credential_method")
                ),
            }
        )
