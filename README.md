# 🔐 ALX Backend Security System (Django)

A **Django-based backend security system** that protects web applications from malicious activity by logging IP requests, rate-limiting login attempts, and allowing administrators to block or unblock IP addresses through a secure dashboard.

---

## 🚀 Features

### 🔹 User Authentication
- Secure login and logout
- Rate-limited login attempts (anti–brute-force)
- Automatic IP blocking after too many failed attempts

### 🔹 IP Security & Monitoring
- Logs every incoming request
- Tracks IP address, path, timestamp, country, and city
- Blocks malicious IPs automatically or manually

### 🔹 Admin Dashboard
- View request logs
- View blocked IPs
- Manually block/unblock IPs
- Unblock history
- Admin-only access (staff/superuser)

### 🔹 Email Alerts
- Sends email when an IP is blocked or unblocked (admin action)

---

## 🛠️ Tech Stack

- **Backend:** Django 6.0
- **Database:** SQLite (development)
- **Security:** django-ratelimit
- **Geo Location:** GeoIP2 (GeoLite2)
- **Authentication:** Django Auth System
- **Version Control:** Git & GitHub

---

## 📂 Project Structure



alx-backend-security/
│
├── ip_tracking/
│ ├── models.py
│ ├── views.py
│ ├── middleware.py
│ ├── urls.py
│ └── templates/
│ ├── admin/
│ └── auth/
│
├── security_project/
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md


---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Brain-new1/alx-backend-security.git
cd alx-backend-security
