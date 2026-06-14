from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import AccessDevice, AlarmEvent, DoorOpenLog, VisitorPass


class AccessControlTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()
        self.today = timezone.localdate()

        self.device_online = AccessDevice.objects.create(
            name="东门人脸门禁",
            device_code="GATE-A-001",
            location="一期东门",
            status=AccessDevice.Status.ONLINE,
            last_heartbeat=self.now,
        )
        self.device_offline = AccessDevice.objects.create(
            name="西门门禁",
            device_code="GATE-A-002",
            location="一期西门",
            status=AccessDevice.Status.OFFLINE,
            last_heartbeat=self.now - timedelta(hours=2),
        )
        self.device_maintenance = AccessDevice.objects.create(
            name="北门二维码门禁",
            device_code="GATE-N-006",
            location="二期北门",
            status=AccessDevice.Status.MAINTENANCE,
            last_heartbeat=self.now - timedelta(hours=1),
        )

        self.visitor_approved = VisitorPass.objects.create(
            visitor_name="李明",
            phone="13800001111",
            host_name="张女士",
            reason="亲友来访",
            device=self.device_online,
            visit_time=self.now + timedelta(hours=2),
            leave_time=self.now + timedelta(hours=5),
            pass_status=VisitorPass.PassStatus.APPROVED,
            id_card_last4="1024",
        )
        self.visitor_pending = VisitorPass.objects.create(
            visitor_name="王工",
            phone="13900002222",
            host_name="物业中心",
            reason="电梯维保",
            device=self.device_maintenance,
            visit_time=self.now + timedelta(days=1),
            pass_status=VisitorPass.PassStatus.PENDING,
            id_card_last4="7788",
        )
        self.visitor_rejected = VisitorPass.objects.create(
            visitor_name="赵某某",
            phone="13700003333",
            host_name="刘先生",
            reason="快递投递",
            device=self.device_online,
            visit_time=self.now - timedelta(days=1),
            pass_status=VisitorPass.PassStatus.REJECTED,
        )
        self.visitor_expired = VisitorPass.objects.create(
            visitor_name="孙某某",
            phone="13600004444",
            host_name="陈女士",
            reason="家政服务",
            device=self.device_offline,
            visit_time=self.now - timedelta(days=2),
            pass_status=VisitorPass.PassStatus.EXPIRED,
        )

        self.alarm_open = AlarmEvent.objects.create(
            title="车库疑似尾随通行",
            device=self.device_offline,
            alarm_type=AlarmEvent.AlarmType.TAILGATING,
            level=AlarmEvent.Level.HIGH,
            description="同一次开闸检测到两次通行轨迹",
            status=AlarmEvent.Status.OPEN,
            occurred_at=self.now - timedelta(minutes=8),
        )
        self.alarm_processing = AlarmEvent.objects.create(
            title="北门设备维护超时",
            device=self.device_maintenance,
            alarm_type=AlarmEvent.AlarmType.DEVICE_OFFLINE,
            level=AlarmEvent.Level.MEDIUM,
            description="北门门禁设备心跳异常",
            status=AlarmEvent.Status.PROCESSING,
            occurred_at=self.now - timedelta(minutes=35),
            handled_by="周安保",
        )
        self.alarm_resolved = AlarmEvent.objects.create(
            title="暴力开门告警",
            device=self.device_online,
            alarm_type=AlarmEvent.AlarmType.FORCED_OPEN,
            level=AlarmEvent.Level.HIGH,
            description="检测到异常开门",
            status=AlarmEvent.Status.RESOLVED,
            occurred_at=self.now - timedelta(hours=3),
            handled_by="李安保",
            handled_at=self.now - timedelta(hours=2),
        )
        self.alarm_low = AlarmEvent.objects.create(
            title="黑名单人员尝试进入",
            device=self.device_online,
            alarm_type=AlarmEvent.AlarmType.BLACKLIST,
            level=AlarmEvent.Level.LOW,
            description="黑名单人员刷脸被拦截",
            status=AlarmEvent.Status.OPEN,
            occurred_at=self.now - timedelta(minutes=15),
        )

        self.log_success_visitor = DoorOpenLog.objects.create(
            device=self.device_online,
            visitor_pass=self.visitor_approved,
            opener_name="李明",
            opener_type=DoorOpenLog.OpenerType.VISITOR,
            credential_method=DoorOpenLog.CredentialMethod.QRCODE,
            result=DoorOpenLog.Result.SUCCESS,
            opened_at=self.now - timedelta(minutes=20),
        )
        self.log_success_resident = DoorOpenLog.objects.create(
            device=self.device_online,
            opener_name="陈先生",
            opener_type=DoorOpenLog.OpenerType.RESIDENT,
            credential_method=DoorOpenLog.CredentialMethod.FACE,
            result=DoorOpenLog.Result.SUCCESS,
            opened_at=self.now - timedelta(minutes=14),
        )
        self.log_denied = DoorOpenLog.objects.create(
            device=self.device_offline,
            opener_name="未知人员",
            opener_type=DoorOpenLog.OpenerType.VISITOR,
            credential_method=DoorOpenLog.CredentialMethod.QRCODE,
            result=DoorOpenLog.Result.DENIED,
            opened_at=self.now - timedelta(minutes=9),
            failure_reason="访客二维码已过期",
        )
        self.log_success_admin = DoorOpenLog.objects.create(
            device=self.device_offline,
            opener_name="物业管理员",
            opener_type=DoorOpenLog.OpenerType.ADMIN,
            credential_method=DoorOpenLog.CredentialMethod.REMOTE,
            result=DoorOpenLog.Result.SUCCESS,
            opened_at=self.now - timedelta(minutes=4),
        )
        self.log_old = DoorOpenLog.objects.create(
            device=self.device_maintenance,
            opener_name="张某某",
            opener_type=DoorOpenLog.OpenerType.RESIDENT,
            credential_method=DoorOpenLog.CredentialMethod.CARD,
            result=DoorOpenLog.Result.SUCCESS,
            opened_at=self.now - timedelta(days=3),
        )


class DoorLogFilterTests(AccessControlTestBase):
    def test_filter_by_result_success(self):
        response = self.client.get("/api/door-logs/", {"result": "success"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)
        results = [log["result"] for log in response.data["results"]]
        self.assertTrue(all(r == "success" for r in results))

    def test_filter_by_result_denied(self):
        response = self.client.get("/api/door-logs/", {"result": "denied"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["result"], "denied")
        self.assertEqual(response.data["results"][0]["opener_name"], "未知人员")

    def test_filter_by_opener_type_visitor(self):
        response = self.client.get("/api/door-logs/", {"opener_type": "visitor"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        opener_types = [log["opener_type"] for log in response.data["results"]]
        self.assertTrue(all(t == "visitor" for t in opener_types))

    def test_filter_by_opener_type_resident(self):
        response = self.client.get("/api/door-logs/", {"opener_type": "resident"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_opener_type_admin(self):
        response = self.client.get("/api/door-logs/", {"opener_type": "admin"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["opener_name"], "物业管理员")

    def test_filter_by_keyword_opener_name(self):
        response = self.client.get("/api/door-logs/", {"keyword": "李明"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["opener_name"], "李明")

    def test_filter_by_keyword_device_name(self):
        response = self.client.get("/api/door-logs/", {"keyword": "东门"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        device_names = [log["device_name"] for log in response.data["results"]]
        self.assertTrue(all("东门" in name for name in device_names))

    def test_filter_by_keyword_device_location(self):
        response = self.client.get("/api/door-logs/", {"keyword": "一期西门"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_time_range(self):
        start_time = (self.now - timedelta(minutes=30)).isoformat()
        end_time = self.now.isoformat()
        response = self.client.get(
            "/api/door-logs/",
            {"start_time": start_time, "end_time": end_time},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)

    def test_filter_by_start_time_only(self):
        start_time = (self.now - timedelta(minutes=10)).isoformat()
        response = self.client.get("/api/door-logs/", {"start_time": start_time})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_end_time_only(self):
        end_time = (self.now - timedelta(days=1)).isoformat()
        response = self.client.get("/api/door-logs/", {"end_time": end_time})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["opener_name"], "张某某")

    def test_combined_filters_result_and_opener_type(self):
        response = self.client.get(
            "/api/door-logs/",
            {"result": "success", "opener_type": "visitor"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["opener_name"], "李明")

    def test_combined_filters_keyword_and_time_range(self):
        start_time = (self.now - timedelta(minutes=30)).isoformat()
        end_time = self.now.isoformat()
        response = self.client.get(
            "/api/door-logs/",
            {"keyword": "陈先生", "start_time": start_time, "end_time": end_time},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_no_filters_returns_all(self):
        response = self.client.get("/api/door-logs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)

    def test_export_csv(self):
        response = self.client.get("/api/door-logs/export/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8-sig")
        self.assertIn("attachment; filename=\"door_logs.csv\"", response["Content-Disposition"])
        content = response.content.decode("utf-8-sig")
        self.assertIn("时间,人员,类型,设备,开门方式,结果,说明", content)
        self.assertIn("李明", content)
        self.assertIn("陈先生", content)


class AlarmStatusFilterTests(AccessControlTestBase):
    def test_filter_by_status_open(self):
        response = self.client.get("/api/alarms/", {"status": "open"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        statuses = [alarm["status"] for alarm in response.data["results"]]
        self.assertTrue(all(s == "open" for s in statuses))

    def test_filter_by_status_processing(self):
        response = self.client.get("/api/alarms/", {"status": "processing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "processing")
        self.assertEqual(response.data["results"][0]["handled_by"], "周安保")

    def test_filter_by_status_resolved(self):
        response = self.client.get("/api/alarms/", {"status": "resolved"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "resolved")

    def test_filter_by_level_high(self):
        response = self.client.get("/api/alarms/", {"level": "high"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        levels = [alarm["level"] for alarm in response.data["results"]]
        self.assertTrue(all(l == "high" for l in levels))

    def test_filter_by_level_medium(self):
        response = self.client.get("/api/alarms/", {"level": "medium"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["level"], "medium")

    def test_filter_by_level_low(self):
        response = self.client.get("/api/alarms/", {"level": "low"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["alarm_type"], "blacklist")

    def test_combined_status_and_level_filters(self):
        response = self.client.get(
            "/api/alarms/",
            {"status": "open", "level": "high"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "车库疑似尾随通行")

    def test_no_filters_returns_all_alarms(self):
        response = self.client.get("/api/alarms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)


class DeviceOnlineStatsTests(AccessControlTestBase):
    def test_stats_devices_total(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["devices_total"], 3)

    def test_stats_devices_online(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["devices_online"], 1)

    def test_stats_devices_online_after_changing_status(self):
        self.device_offline.status = AccessDevice.Status.ONLINE
        self.device_offline.save()
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["devices_online"], 2)

    def test_device_list_filter_by_search(self):
        response = self.client.get("/api/devices/", {"search": "东门"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "东门人脸门禁")

    def test_device_list_ordering_by_status(self):
        response = self.client.get("/api/devices/", {"ordering": "status"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        statuses = [d["status"] for d in response.data["results"]]
        self.assertEqual(statuses, sorted(statuses))


class VisitorStatusFilterTests(AccessControlTestBase):
    def test_filter_by_status_approved(self):
        response = self.client.get("/api/visitors/", {"status": "approved"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["pass_status"], "approved")
        self.assertEqual(response.data["results"][0]["visitor_name"], "李明")

    def test_filter_by_status_pending(self):
        response = self.client.get("/api/visitors/", {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["pass_status"], "pending")
        self.assertEqual(response.data["results"][0]["visitor_name"], "王工")

    def test_filter_by_status_rejected(self):
        response = self.client.get("/api/visitors/", {"status": "rejected"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["pass_status"], "rejected")

    def test_filter_by_status_expired(self):
        response = self.client.get("/api/visitors/", {"status": "expired"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["pass_status"], "expired")

    def test_stats_visitors_pending(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["visitors_pending"], 1)

    def test_stats_visitors_pending_after_approve(self):
        self.visitor_pending.pass_status = VisitorPass.PassStatus.APPROVED
        self.visitor_pending.save()
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["visitors_pending"], 0)

    def test_stats_visitors_pending_after_reject(self):
        self.visitor_pending.pass_status = VisitorPass.PassStatus.REJECTED
        self.visitor_pending.save()
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["visitors_pending"], 0)

    def test_no_filter_returns_all_visitors(self):
        response = self.client.get("/api/visitors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)


class StatsViewTests(AccessControlTestBase):
    def test_stats_open_alarms(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["open_alarms"], 3)

    def test_stats_open_alarms_after_resolve(self):
        self.alarm_open.status = AlarmEvent.Status.RESOLVED
        self.alarm_open.save()
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["open_alarms"], 2)

    def test_stats_today_success_logs(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["today_success_logs"], 3)

    def test_stats_logs_by_method(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        logs_by_method = response.data["logs_by_method"]
        self.assertIsInstance(logs_by_method, list)
        methods = [item["credential_method"] for item in logs_by_method]
        counts = {item["credential_method"]: item["count"] for item in logs_by_method}
        self.assertIn("face", methods)
        self.assertIn("qrcode", methods)
        self.assertIn("remote", methods)
        self.assertIn("card", methods)
        self.assertEqual(counts["face"], 1)
        self.assertEqual(counts["qrcode"], 2)
        self.assertEqual(counts["remote"], 1)
        self.assertEqual(counts["card"], 1)

    def test_stats_all_fields_present(self):
        response = self.client.get("/api/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = [
            "devices_total",
            "devices_online",
            "visitors_pending",
            "open_alarms",
            "today_success_logs",
            "logs_by_method",
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
