from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import RequestLog, SuspiciousIP

@shared_task
def detect_anomalies():
    one_hour_ago = timezone.now() - timedelta(hours=1)
    logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    ip_counts = {}

    for log in logs:
        ip = log.ip_address
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

        if log.path in ["/admin", "/login"]:
            SuspiciousIP.objects.create(
                ip_address=ip,
                reason=f"Accessed sensitive path: {log.path}"
            )

    for ip, count in ip_counts.items():
        if count > 100:
            SuspiciousIP.objects.create(
                ip_address=ip,
                reason="More than 100 requests per hour"
            )
