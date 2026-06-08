from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from access.models import AccessDevice, AlarmEvent, DoorOpenLog, VisitorPass


class Command(BaseCommand):
    help = "Create demo data for the smart access control system."

    def handle(self, *args, **options):
        now = timezone.now()
        main_gate, _ = AccessDevice.objects.update_or_create(
            device_code="GATE-A-001",
            defaults={
                "name": "东门人脸门禁",
                "location": "一期东门",
                "status": AccessDevice.Status.ONLINE,
                "last_heartbeat": now,
            },
        )
        garage_gate, _ = AccessDevice.objects.update_or_create(
            device_code="GARAGE-B-018",
            defaults={
                "name": "地下车库闸机",
                "location": "B区地下车库",
                "status": AccessDevice.Status.ONLINE,
                "last_heartbeat": now - timedelta(minutes=2),
            },
        )
        north_gate, _ = AccessDevice.objects.update_or_create(
            device_code="GATE-N-006",
            defaults={
                "name": "北门二维码门禁",
                "location": "二期北门",
                "status": AccessDevice.Status.MAINTENANCE,
                "last_heartbeat": now - timedelta(hours=1),
            },
        )

        visitor, _ = VisitorPass.objects.update_or_create(
            phone="13800001111",
            visit_time=now + timedelta(hours=2),
            defaults={
                "visitor_name": "李明",
                "host_name": "张女士",
                "reason": "亲友来访",
                "device": main_gate,
                "leave_time": now + timedelta(hours=5),
                "pass_status": VisitorPass.PassStatus.APPROVED,
                "id_card_last4": "1024",
            },
        )
        VisitorPass.objects.update_or_create(
            phone="13900002222",
            visit_time=now + timedelta(days=1),
            defaults={
                "visitor_name": "王工",
                "host_name": "物业中心",
                "reason": "电梯维保",
                "device": north_gate,
                "pass_status": VisitorPass.PassStatus.PENDING,
                "id_card_last4": "7788",
            },
        )

        AlarmEvent.objects.update_or_create(
            title="北门设备维护超时",
            occurred_at=now - timedelta(minutes=35),
            defaults={
                "device": north_gate,
                "alarm_type": AlarmEvent.AlarmType.DEVICE_OFFLINE,
                "level": AlarmEvent.Level.MEDIUM,
                "description": "北门门禁设备心跳异常，请值班人员复核网络与供电。",
                "status": AlarmEvent.Status.PROCESSING,
                "handled_by": "周安保",
            },
        )
        AlarmEvent.objects.update_or_create(
            title="车库疑似尾随通行",
            occurred_at=now - timedelta(minutes=8),
            defaults={
                "device": garage_gate,
                "alarm_type": AlarmEvent.AlarmType.TAILGATING,
                "level": AlarmEvent.Level.HIGH,
                "description": "同一次开闸检测到两次通行轨迹，已推送监控中心。",
                "status": AlarmEvent.Status.OPEN,
            },
        )

        log_rows = [
            (main_gate, visitor, "李明", DoorOpenLog.OpenerType.VISITOR, DoorOpenLog.CredentialMethod.QRCODE, DoorOpenLog.Result.SUCCESS, now - timedelta(minutes=20), ""),
            (main_gate, None, "陈先生", DoorOpenLog.OpenerType.RESIDENT, DoorOpenLog.CredentialMethod.FACE, DoorOpenLog.Result.SUCCESS, now - timedelta(minutes=14), ""),
            (garage_gate, None, "未知人员", DoorOpenLog.OpenerType.VISITOR, DoorOpenLog.CredentialMethod.QRCODE, DoorOpenLog.Result.DENIED, now - timedelta(minutes=9), "访客二维码已过期"),
            (garage_gate, None, "物业管理员", DoorOpenLog.OpenerType.ADMIN, DoorOpenLog.CredentialMethod.REMOTE, DoorOpenLog.Result.SUCCESS, now - timedelta(minutes=4), ""),
        ]
        for device, pass_obj, name, opener_type, method, result, opened_at, reason in log_rows:
            DoorOpenLog.objects.update_or_create(
                device=device,
                opener_name=name,
                opened_at=opened_at,
                defaults={
                    "visitor_pass": pass_obj,
                    "opener_type": opener_type,
                    "credential_method": method,
                    "result": result,
                    "failure_reason": reason,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
