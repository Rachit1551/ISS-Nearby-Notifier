import os
import requests as r
from datetime import datetime
from zoneinfo import ZoneInfo
import smtplib as s
from email.message import EmailMessage
from plyer import notification  # For Windows desktop notifications

# Clear terminal screen (for Windows)
os.system('cls')


# Get user's current latitude and longitude based on IP address
def Current_Lang_Long():
    response = r.get("https://ipinfo.io/json", timeout=5)
    data = response.json()
    loc = data.get("loc")  # Format: "latitude,longitude"
    if loc:
        latitude, longitude = map(float, loc.split(','))
        return latitude, longitude
    return None


# Get the current position of the International Space Station (ISS)
def ISS_position():
    response = r.get("http://api.open-notify.org/iss-now.json", timeout=5)
    response.raise_for_status()
    iss_data = response.json()
    iss_lat = float(iss_data['iss_position']['latitude'])
    iss_long = float(iss_data['iss_position']['longitude'])
    return iss_lat, iss_long


# Get sunrise and sunset times in IST for the user's location
def Sun_rise_set():
    lat, long = Current_Lang_Long()
    current_location = {
        "lat": lat,
        "lng": long,
        "formatted": 0
    }

    response = r.get("https://api.sunrise-sunset.org/json", params=current_location, timeout=5)
    response.raise_for_status()
    sun_data = response.json()

    utc_sunrise = sun_data['results']['sunrise']
    utc_sunset = sun_data['results']['sunset']

    sunrise_utc = datetime.fromisoformat(utc_sunrise)
    sunset_utc = datetime.fromisoformat(utc_sunset)

    sunrise_ist = sunrise_utc.astimezone(ZoneInfo("Asia/Kolkata"))
    sunset_ist = sunset_utc.astimezone(ZoneInfo("Asia/Kolkata"))

    return sunrise_ist.hour, sunset_ist.hour


# Send an email alert to the user
def Email_sender(message):
    my_email = ""      # Your Gmail address
    password = ""      # Gmail App Password (not regular password)

    msg = EmailMessage()
    msg["Subject"] = "ISS Visibility Alert"
    msg["From"] = my_email
    msg["To"] = my_email
    msg.set_content(message)

    with s.SMTP("smtp.gmail.com", 587) as con:
        con.starttls()
        con.login(my_email, password)
        con.send_message(msg)


# Show a desktop notification (Windows)
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10,
        app_name="ISS Tracker"
    )


# Main program logic
def main():
    now = datetime.now()
    lat, lon = Current_Lang_Long()
    iss_lat, iss_long = ISS_position()
    sr_hour, ss_hour = Sun_rise_set()

    # Check if ISS is near user's location
    if (lat - 5 <= iss_lat <= lat + 5) and (lon - 5 <= iss_long <= lon + 5):
        if now.hour >= ss_hour or now.hour <= sr_hour:
            msg = (
                f"ISS is currently near your location. It is dark enough to view it in the sky.\n\n"
                f"Your Location: Latitude {lat}, Longitude {lon}\n"
                f"ISS Location: Latitude {iss_lat}, Longitude {iss_long}"
            )
        else:
            msg = (
                f"ISS is currently near your location, but it is daylight. Visibility might be limited.\n\n"
                f"Your Location: Latitude {lat}, Longitude {lon}\n"
                f"ISS Location: Latitude {iss_lat}, Longitude {iss_long}"
            )

        show_notification("ISS Tracker Notification", msg)
        Email_sender(msg)


# Execute the script
if __name__ == "__main__":
    main()
