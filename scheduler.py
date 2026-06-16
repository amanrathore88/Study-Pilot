import json

def save_schedule(email, time_str):

    data = {
        "email": email,
        "time": time_str,
        "active": True
    }

    with open("schedule.json", "w") as f:
        json.dump(data, f, indent=2)


def load_schedule():

    try:

        with open("schedule.json", "r") as f:

            data = json.load(f)

        if not data.get("active", True):
            return None

        return data

    except:
        return None