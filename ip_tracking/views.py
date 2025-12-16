from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from ratelimit.decorators import ratelimit
from .models import BlockedIP

from .models import RequestLog, BlockedIP


# ===============================
# HELPER: ADMIN CHECK
# ===============================
def is_admin(user):
    return user.is_superuser or user.is_staff


# ===============================
# HOME PAGE
# ===============================
def home(request):
    return render(request, "home.html")


# ===============================
# LOGIN WITH RATE LIMIT
# ===============================
@ratelimit(key="ip", rate="5/m", block=False)
def login_view(request):

    ip = request.META.get("REMOTE_ADDR", "Unknown")
    was_limited = getattr(request, "limited", False)

    # If rate limit exceeded → block IP
    if was_limited:
        BlockedIP.objects.get_or_create(
            ip_address=ip,
            defaults={"reason": "Too many login attempts"}
        )
        messages.error(
            request,
            "Too many login attempts! Your IP is blocked for 1 hour."
        )
        return render(request, "login.html")

    # Normal login
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    # ✅ ALWAYS RETURN RESPONSE
    return render(request, "login.html")


# ===============================
# LOGOUT
# ===============================
def logout_view(request):
    logout(request)
    return redirect("login")


# ===============================
# ADMIN DASHBOARD
# ===============================
@login_required
@user_passes_test(is_admin)
def dashboard(request):

    # 🌍 COUNTRY MAP DATA (MOVED HERE — FIXED)
    country_stats = (
        RequestLog.objects.values("country")
        .annotate(visits=Count("id"))
        .order_by("-visits")
    )

    countries = [c["country"] for c in country_stats]
    visits = [c["visits"] for c in country_stats]

    context = {
        "logs_count": RequestLog.objects.count(),
        "blocked_count": BlockedIP.objects.filter(unblocked_at__isnull=True).count(),
        "unblocked_count": BlockedIP.objects.filter(unblocked_at__isnull=False).count(),
        "recent_logs": RequestLog.objects.order_by("-timestamp")[:10],
        "countries": countries,
        "visits": visits,
    }

    return render(request, "admin/dashboard.html", context)


# ===============================
# REQUEST LOGS
# ===============================
@login_required
@user_passes_test(is_admin)
def logs_view(request):
    logs = RequestLog.objects.order_by("-timestamp")
    return render(request, "admin/logs.html", {"logs": logs})


# ===============================
# BLOCKED IP LIST
# ===============================
@login_required
@user_passes_test(is_admin)
def blocked_ips(request):
    blocked = BlockedIP.objects.filter(unblocked_at__isnull=True).order_by("-blocked_at")
    return render(request, "admin/blocked_ips.html", {"blocked": blocked})


# ===============================
# UNBLOCK HISTORY
# ===============================
@login_required
@user_passes_test(is_admin)
def unblock_history(request):
    history = BlockedIP.objects.filter(unblocked_at__isnull=False).order_by("-unblocked_at")
    return render(request, "admin/unblock_history.html", {"history": history})


# ===============================
# MANUAL BLOCK (ADMIN)
# ===============================
@login_required
@user_passes_test(is_admin)
def block_ip(request):
    if request.method == "POST":
        ip = request.POST.get("ip_address")

        if ip and not BlockedIP.objects.filter(ip_address=ip, unblocked_at__isnull=True).exists():
            entry = BlockedIP.objects.create(
                ip_address=ip,
                reason="Blocked manually by Admin"
            )

            send_mail(
                subject="Admin Action: IP Blocked",
                message=f"""
IP BLOCKED BY ADMIN

IP Address: {ip}
Reason: Manual Block
Blocked At: {entry.blocked_at}
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )

        return redirect("blocked_ips")

    return render(request, "admin/block_form.html")


# ===============================
# UNBLOCK IP (ADMIN — NO WAITING)
# ===============================
@login_required
@user_passes_test(is_admin)
def unblock_ip(request, ip):
    entry = BlockedIP.objects.filter(ip_address=ip, unblocked_at__isnull=True).first()

    if entry:
        entry.unblocked_at = now()
        entry.save()

        send_mail(
            subject="Security Alert: IP Unblocked",
            message=f"""
IP UNBLOCKED BY ADMIN

IP Address: {entry.ip_address}
Blocked Reason: {entry.reason}
Blocked At: {entry.blocked_at}
Unblocked At: {entry.unblocked_at}
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )

    return redirect("blocked_ips")
