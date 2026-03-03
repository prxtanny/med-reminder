from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
import database
import smtplib
from email.message import EmailMessage

def reset_if_new_day():
    today = str(date.today())
    last = database.get_setting("last_reset_date")

    if today != last:
        with database.connect() as conn:
            conn.execute("UPDATE medicines SET taken_today=0, last_notified=NULL")
        database.set_setting("last_reset_date", today)
        database.log("เริ่มวันใหม่ รีเซ็ตสถานะยา")

def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg["From"] = to_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # NOTE: ตรงนี้ยังไม่ใส่รหัส
    # เราจะเปิดใช้จริงใน STEP ถัดไป
    # เพื่อให้ debug ง่าย

def check_medicines():
    reset_if_new_day()

    delay = int(database.get_setting("notify_delay"))
    email_enabled = database.get_setting("email_enabled") == "1"
    caregiver_email = database.get_setting("caregiver_email")

    now = datetime.now()

    with database.connect() as conn:
        meds = conn.execute(
            "SELECT id, name, time, taken_today, last_notified FROM medicines"
        ).fetchall()

    for m in meds:
        mid, name, time_str, taken, last_notified = m
        med_time = datetime.strptime(time_str, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )

        if taken == 1:
            continue

        minutes_passed = (now - med_time).total_seconds() / 60

        if minutes_passed >= delay:
            today = str(date.today())

            if last_notified == today:
                continue

            if email_enabled and caregiver_email:
                # (เปิดใช้จริงใน STEP Email)
                database.log(f"ถึงเวลาแจ้งเตือนยา {name}")

                with database.connect() as conn:
                    conn.execute(
                        "UPDATE medicines SET last_notified=? WHERE id=?",
                        (today, mid)
                    )

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_medicines, "interval", minutes=1)
    scheduler.start()