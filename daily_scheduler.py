import json
import time
import schedule
from datetime import date
from scheduler import load_schedule
from remainder import send_daily_nudge

def send_scheduled_email():
    print("===== EMAIL FUNCTION STARTED =====")
    data = load_schedule()

    if not data:
        return

    email = data["email"]

    try:

        with open("timetable.json", "r") as f:
            timetable = json.load(f)
            
    # Check if timetable is finished

        last_study_day = timetable["timetable"][-1]["date"]

        if str(date.today()) > last_study_day:

            print("Syllabus completed. Stopping reminders.")

            with open("schedule.json", "r") as f:
                schedule_data = json.load(f)

            schedule_data["active"] = False

            with open("schedule.json", "w") as f:
                json.dump(schedule_data, f, indent=2)

            return

        rows = []

        for day in timetable["timetable"]:

            for slot in day["slots"]:

                rows.append({
                    "date": day["date"],
                    "subject": slot["subject"],
                    "topic": ", ".join(
                        slot["chapters_to_cover"]
                    ),
                    "minutes": slot["duration_minutes"],
                    "notes": slot.get("notes", "")
                })

        print("About to send email...")
        print("Recipient:", email)
            
        send_daily_nudge(
            rows,
            recipient_email=email
        )

        print(
            f"Email sent successfully to {email}"
        )

    except Exception as e:

        print(
            f"Email failed: {e}"
        )

schedule_data = load_schedule()

if schedule_data:

    time_string = schedule_data["time"]

    schedule.every().day.at(
        time_string[:5]
    ).do(
        send_scheduled_email
    )

    print(f"Loaded schedule time: {time_string}")
    print("Waiting for scheduled email...")
        
    print(
        f"Scheduler running at {time_string}"
    )

    while True:

        schedule.run_pending()

        time.sleep(1)

else:

    print(
        "No schedule configured."
    )