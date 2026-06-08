from django.db import models
from django.utils import timezone


class AccessDevice(models.Model):
    class Status(models.TextChoices):
        ONLINE = "online", "在线"
        OFFLINE = "offline", "离线"
        MAINTENANCE = "maintenance", "维护中"

    name = models.CharField(max_length=80)
    device_code = models.CharField(max_length=40, unique=True)
    location = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ONLINE)
    last_heartbeat = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["device_code"]

    def __str__(self):
        return f"{self.name}({self.device_code})"


class VisitorPass(models.Model):
    class PassStatus(models.TextChoices):
        PENDING = "pending", "待审批"
        APPROVED = "approved", "已批准"
        REJECTED = "rejected", "已拒绝"
        EXPIRED = "expired", "已过期"

    visitor_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=30)
    host_name = models.CharField(max_length=60)
    reason = models.CharField(max_length=160)
    device = models.ForeignKey(AccessDevice, on_delete=models.PROTECT, related_name="visitor_passes")
    visit_time = models.DateTimeField()
    leave_time = models.DateTimeField(null=True, blank=True)
    pass_status = models.CharField(max_length=20, choices=PassStatus.choices, default=PassStatus.PENDING)
    id_card_last4 = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-visit_time"]

    def __str__(self):
        return f"{self.visitor_name} -> {self.host_name}"


class AlarmEvent(models.Model):
    class AlarmType(models.TextChoices):
        TAILGATING = "tailgating", "尾随通行"
        FORCED_OPEN = "forced_open", "暴力开门"
        DEVICE_OFFLINE = "device_offline", "设备离线"
        BLACKLIST = "blacklist", "黑名单告警"

    class Level(models.TextChoices):
        LOW = "low", "低"
        MEDIUM = "medium", "中"
        HIGH = "high", "高"

    class Status(models.TextChoices):
        OPEN = "open", "待处理"
        PROCESSING = "processing", "处理中"
        RESOLVED = "resolved", "已处理"

    device = models.ForeignKey(AccessDevice, on_delete=models.PROTECT, related_name="alarms")
    alarm_type = models.CharField(max_length=30, choices=AlarmType.choices)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.MEDIUM)
    title = models.CharField(max_length=120)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    occurred_at = models.DateTimeField(default=timezone.now)
    handled_by = models.CharField(max_length=60, blank=True)
    handled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return self.title


class DoorOpenLog(models.Model):
    class OpenerType(models.TextChoices):
        RESIDENT = "resident", "业主"
        VISITOR = "visitor", "访客"
        ADMIN = "admin", "管理员"
        SYSTEM = "system", "系统"

    class CredentialMethod(models.TextChoices):
        FACE = "face", "人脸"
        CARD = "card", "门禁卡"
        QRCODE = "qrcode", "二维码"
        REMOTE = "remote", "远程开门"
        PASSWORD = "password", "密码"

    class Result(models.TextChoices):
        SUCCESS = "success", "成功"
        DENIED = "denied", "拒绝"

    device = models.ForeignKey(AccessDevice, on_delete=models.PROTECT, related_name="door_logs")
    visitor_pass = models.ForeignKey(VisitorPass, on_delete=models.SET_NULL, null=True, blank=True, related_name="door_logs")
    opener_name = models.CharField(max_length=60)
    opener_type = models.CharField(max_length=20, choices=OpenerType.choices)
    credential_method = models.CharField(max_length=20, choices=CredentialMethod.choices)
    result = models.CharField(max_length=20, choices=Result.choices, default=Result.SUCCESS)
    opened_at = models.DateTimeField(default=timezone.now)
    failure_reason = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["-opened_at"]

    def __str__(self):
        return f"{self.opener_name} {self.get_result_display()} {self.opened_at:%Y-%m-%d %H:%M}"
