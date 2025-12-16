import os
import geoip2.database
from django.http import HttpResponse
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin
from .models import BlockedIP, RequestLog


class IPLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        ip = request.META.get("REMOTE_ADDR", "Unknown")

        # === CHECK IF IP IS BLOCKED ===
        blocked = BlockedIP.objects.filter(
            ip_address=ip,
            unblocked_at__isnull=True
        ).first()

        if blocked:
            # Auto-unblock after 1 hour
            if blocked.is_expired():
                blocked.unblocked_at = now()
                blocked.save()
            else:
                return HttpResponse(
                    "Your IP is blocked by admin or due to too many login attempts. "
                    "Please try again after 1 hour.",
                    status=403
                )

        # === GEOLOCATION ===
        country = "Unknown"
        city = "Unknown"

        GEO_DB_PATH = "D:/ALX_Project/alx-backend-security/geo/GeoLite2-City.mmdb"

        if os.path.exists(GEO_DB_PATH):
            try:
                with geoip2.database.Reader(GEO_DB_PATH) as reader:
                    response = reader.city(ip)
                    country = response.country.name or "Unknown"
                    city = response.city.name or "Unknown"
            except Exception:
                pass

        # === LOG REQUEST ===
        RequestLog.objects.create(
            ip_address=ip,
            path=request.path,
            country=country
        )

        print(f"[IP LOG] {ip} | {country} | {city}")

        return None
