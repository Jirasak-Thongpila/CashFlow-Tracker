# 💰 CashFlow Tracker

ระบบจัดการรายรับ-รายจ่ายส่วนบุคคลที่พัฒนาด้วย Django และ PostgreSQL พร้อมระบบแดชบอร์ดที่สวยงามและฟีเจอร์การวิเคราะห์กระแสเงินสด

## 🛠️ เทคโนโลยีที่ใช้

### Backend
- **Django 5.2.5** - Python Web Framework
- **Python** - ภาษาโปรแกรมหลัก
- **PostgreSQL** - ระบบจัดการฐานข้อมูล
- **SQLite** - ฐานข้อมูลสำหรับการพัฒนา

### Frontend
- **Bootstrap 5.3.0** - CSS Framework
- **Font Awesome 6.0.0** - ไอคอน
- **Chart.js** - การสร้างกราฟและชาร์ต
- **JavaScript** - สำหรับ Interactive UI

### DevOps & Deployment
- **Vercel** - แพลตฟอร์มสำหรับ deployment
- **Docker** - สำหรับ containerization
- **WhiteNoise** - การจัดการ static files
- **SSL/HTTPS** - ความปลอดภัย

### Python Packages
- **django-extensions** - เครื่องมือเสริมสำหรับ Django
- **python-dotenv** - การจัดการ environment variables
- **psycopg2-binary** - PostgreSQL adapter
- **pyOpenSSL** - SSL/TLS support
- **cryptography** - การเข้ารหัส
- **Werkzeug** - WSGI utilities

## ✨ คุณสมบัติหลัก

### การจัดการบัญชีผู้ใช้
- ระบบสมัครสมาชิก/เข้าสู่ระบบ
- โปรไฟล์ผู้ใช้ที่ปรับแต่งได้
- ระบบความปลอดภัยระดับสูง

### การจัดการธุรกรรม
- เพิ่ม/แก้ไข/ลบ รายรับ-รายจ่าย
- ระบบหมวดหมู่ที่ยืดหยุ่น (พร้อมไอคอนและสี)
- ระบบค้นหาและกรองข้อมูล
- การตรวจสอบข้อมูลอัตโนมัติ

### แดชบอร์ดและรายงาน
- แดshboard แสดงภาพรวมทางการเงิน
- กราฟแสดงกระแสเงินสดรายเดือน
- แผนภูมิวงกลมแสดงสัดส่วนรายจ่าย
- สถิติและข้อมูลสรุปต่างๆ
- ระบบ cache เพื่อประสิทธิภาพ

### การวิเคราะห์ข้อมูล
- ยอดสุทธิและยอดคงเหลือ
- การเปรียบเทียบรายรับ-รายจ่าย
- แนวโน้มการใช้จ่ายรายหมวดหมู่
- การวิเคราะห์ตามช่วงเวลาต่างๆ

## 📁 โครงสร้างโปรเจค

```
CashFlow-Tracker/
├── accounts/              # แอพจัดการผู้ใช้
│   ├── models.py         # CustomUser model
│   ├── views.py          # Dashboard และ authentication
│   ├── forms.py          # ฟอร์มสมัครสมาชิก
│   └── templatetags/     # Template tags
├── categories/           # แอพจัดการหมวดหมู่
│   ├── models.py        # Category model พร้อม QuerySet
│   ├── management/      # Management commands
│   └── views.py         # CRUD operations
├── transactions/        # แอพจัดการธุรกรรม
│   ├── models.py       # Transaction model พร้อม validation
│   └── views.py        # การจัดการรายการ
├── templates/          # HTML templates
│   ├── base.html       # Template หลัก
│   ├── dashboard.html  # หน้า Dashboard
│   └── */              # Templates ของแต่ละแอพ
├── static/            # Static files (CSS, JS, Images)
├── ssl/              # SSL certificates
└── CashFlow_Tracker/ # การตั้งค่าหลัก
    ├── settings.py   # การตั้งค่า Django
    ├── urls.py       # URL routing
    └── wsgi.py       # WSGI configuration
```

## 🚀 การติดตั้งและใช้งาน

### ความต้องการระบบ
- Python 3.12+
- PostgreSQL
- Git

### การติดตั้งในเครื่อง

1. **Clone repository:**
```bash
git clone https://github.com/yourusername/CashFlow-Tracker.git
cd CashFlow-Tracker
```

2. **สร้าง virtual environment:**
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
# หรือ
env\Scripts\activate     # Windows
```

3. **ติดตั้ง dependencies:**
```bash
pip install -r requirements.txt
```

4. **ตั้งค่า environment variables:**
```bash
cp .env.example .env
```
แก้ไขไฟล์ `.env` ตามการตั้งค่าของคุณ:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=cashflow_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_CONN_MAX_AGE=60

# Session Settings
SESSION_COOKIE_AGE=1209600  # 2 weeks

# Cache Settings
CACHE_MAX_ENTRIES=1000
CACHE_CULL_FREQUENCY=3
CACHE_TTL=300  # 5 minutes
```

5. **ตั้งค่าฐานข้อมูล:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **สร้างหมวดหมู่เริ่มต้น:**
```bash
python manage.py create_default_categories
```

7. **สร้าง superuser:**
```bash
python manage.py createsuperuser
```

8. **รันเซิร์ฟเวอร์:**
```bash
python manage.py runserver
```

เข้าใช้งานที่: `http://localhost:8000`

## 🔧 การปรับแต่งและกำหนดค่า

### การใช้กับ SQLite (สำหรับการพัฒนา)
หากต้องการใช้ SQLite แทน PostgreSQL ให้แก้ไขในไฟล์ `settings.py`:

```python
# เปิด comment ใน settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Management Commands
- `python manage.py create_default_categories` - สร้างหมวดหมู่เริ่มต้น
- `python create_user.py` - สร้างผู้ใช้ทดสอบ

### การจัดการ Static Files
```bash
python manage.py collectstatic
```

## 🚀 การ Deploy

### Vercel Deployment
โปรเจคนี้พร้อมสำหรับ deploy บน Vercel:

1. Push โค้ดไปยัง GitHub
2. เชื่อมต่อกับ Vercel
3. ตั้งค่า environment variables
4. Deploy อัตโนมัติ

ไฟล์ `vercel.json` และ `build_files.sh` ได้ถูกจัดเตรียมไว้แล้ว

### ความปลอดภัย
- SSL/HTTPS บังคับใช้ในโปรดักชัน
- CSRF protection
- XSS protection
- Secure cookies
- HSTS headers

## 📊 ฟีเจอร์เด่น

### ระบบ Cache
- ใช้ Local Memory Cache
- Cache dashboard data เพื่อประสิทธิภาพ
- TTL กำหนดได้ผ่าน environment

### ระบบความปลอดภัย
- Password validation
- Session management
- CSRF protection
- SQL injection protection

### ระบบฐานข้อมูล
- Database indexing สำหรับ query ที่เร็ว
- Custom QuerySets และ Managers
- Data validation ระดับ model

### UI/UX
- Responsive design ทุกหน้าจอ
- Glass morphism design
- Interactive charts
- Real-time data updates

## 🤝 การมีส่วนร่วม

1. Fork โปรเจค
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. Push ไปยัง branch
5. สร้าง Pull Request

## 📝 License

โปรเจคนี้เป็น open source และใช้ภายใต้ MIT License

## 🎯 Roadmap

- [ ] API REST สำหรับ mobile app
- [ ] Export ข้อมูลเป็น PDF/Excel
- [ ] ระบบแจ้งเตือนและเป้าหมายการออม
- [ ] Multi-currency support
- [ ] Mobile application
- [ ] Advanced analytics และ AI insights

---

💡 **หมายเหตุ:** โปรเจคนี้เหมาะสำหรับผู้ที่ต้องการจัดการการเงินส่วนตัว พัฒนาด้วยเทคโนโลยีทันสมัยและเน้นประสิทธิภาพในการใช้งาน
