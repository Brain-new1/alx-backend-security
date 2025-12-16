from django.db import models
from django.utils.timezone import now

class BlockedIP(models.Model):
    ip_address = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=100, default="Unknown")
    reason = models.CharField(max_length=255, blank=True, null=True)

    blocked_at = models.DateTimeField(default=now)
    unblocked_at = models.DateTimeField(null=True, blank=True)
    manually_unblocked = models.BooleanField(default=False)

    def is_expired(self):
        """Check if block time (1 hour) is over"""
        return (now() - self.blocked_at).total_seconds() > 3600

    def __str__(self):
        return self.ip_address


class RequestLog(models.Model):
    ip_address = models.CharField(max_length=50)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=100, default="Unknown")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path}"
