from flask import Flask, render_template, request, redirect
import database
import scheduler

app = Flask(__name__)


@app.before_first_request
def startup():
    database.init_db()
    scheduler.start_scheduler()


@app.route("/", methods=["GET", "POST"])
def elder():
    if request.method == "POST":
        mid = request.form["mid"]
        with database.connect() as conn:
            conn.execute(
                "UPDATE medicines SET taken_today=1 WHERE id=?",
                (mid,)
            )
        database.log("ผู้สูงอายุกดยืนยันกินยาแล้ว")
        return redirect("/")

    with database.connect() as conn:
        meds = conn.execute(
            "SELECT id, name, time, taken_today FROM medicines"
        ).fetchall()

    return render_template("elder.html", meds=meds)


@app.route("/caregiver", methods=["GET", "POST"])
def caregiver():
    if request.method == "POST":
        database.set_setting("caregiver_email", request.form["email"])
        database.set_setting("notify_delay", request.form["delay"])
        database.set_setting(
            "email_enabled", "1" if "email_enabled" in request.form else "0"
        )
        return redirect("/caregiver")

    with database.connect() as conn:
        meds = conn.execute(
            "SELECT id, name, time FROM medicines"
        ).fetchall()

    settings = {
        "email": database.get_setting("caregiver_email"),
        "delay": database.get_setting("notify_delay"),
        "enabled": database.get_setting("email_enabled")
    }

    return render_template("caregiver.html", meds=meds, settings=settings)


@app.route("/add", methods=["POST"])
def add():
    with database.connect() as conn:
        conn.execute(
            "INSERT INTO medicines (name, time) VALUES (?,?)",
            (request.form["name"], request.form["time"])
        )
    database.log("เพิ่มรายการยา")
    return redirect("/caregiver")


@app.route("/delete/<int:mid>")
def delete(mid):
    with database.connect() as conn:
        conn.execute("DELETE FROM medicines WHERE id=?", (mid,))
    database.log("ลบรายการยา")
    return redirect("/caregiver")
