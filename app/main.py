import requests
from flask import Flask
import re
import os
import sys
from icalendar import Calendar, Event
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import uuid


class Residence(object):
    def __init__(self, name, arrival_date, arrival_time, departure_date):
        self.name = name
        self.arrival_date = arrival_date
        self.arrival_time = arrival_time
        self.departure_date = departure_date


def get_address_reserved_list() -> list:
    user_email = os.environ["ADDRESS_USER"]
    user_password = os.environ["ADDRESS_PASSWORD"]
    if user_email is None or user_password is None:
        print("Authentication info not set on ADDRESS_USER/ADDRESS_PASSWORD", file=sys.stderr)
        sys.exit(1)

    session: requests.Session = requests.Session()
    base_url = 'https://home.address.love'
    login_url = base_url + '/login'
    reserve_url = base_url + '/reservations'

    res = session.get(login_url)
    # Get authenticity_token
    if res.ok:
        soup = BeautifulSoup(res.text)
        authenticity_token = soup.find("input").attrs['value']
    else:
        print(f"Failed to access {login_url}", file=sys.stderr)
        sys.exit(1)

    # Login to Address.love
    data = {
        "authenticity_token": authenticity_token,
        "user[email]": user_email,
        "user[password]": user_password,
        "user[remember_me]": 0,
    }
    res = session.post(login_url, data=data)
    if not res.ok:
        print(f"Failed to login Address.", file=sys.stderr)
        sys.exit(1)

    # Get Reservation List
    res = session.get(reserve_url)
    residence_list = list()
    if res.ok:
        soup = BeautifulSoup(res.text)
        div_history_list = soup.find_all('div', class_='history-list')
        # div_history_list = parse.cssselect('div.history-list')
        for div in div_history_list:
            name = div.find('a', class_='text-linkt').text
            li_list = div.find_all('li')
            arrival_date = li_list[0].text
            departure_date = li_list[1].text
            arrival_time = li_list[2].text

            residence_list.append(Residence(
                name=name,
                arrival_date=arrival_date,
                arrival_time=arrival_time,
                departure_date=departure_date,
            ))
    else:
        print(f"Failed to access {reserve_url}", file=sys.stderr)
        sys.exit(1)

    return residence_list

def create_ical(residences):
    tz_tokyo = pytz.timezone('Asia/Tokyo')
    re_ymd = re.compile(r"(\d{4})年(\d{2})月(\d{2})日")
    re_hm = re.compile(r"(\d{2}):(\d{2})")
    ical = Calendar()
    ical.add('prodid', '-//ADDRESS/ADDRESS-RESIDENCE//JA//')
    ical.add('version', '2.0')
    ical.add('calscale', 'GREGORIAN')
    ical.add('method', 'PUBLISH')
    ical.add('x-wr-calname', 'アドレス予約リスト')
    ical.add('x-wr-timezone', 'Asia/Tokyo')

    for residence in residences:
        # Build arrival/departure date as datetime object
        s = re_ymd.search(residence.arrival_date)
        (year, month, day) = s.groups()
        s = re_hm.search(residence.arrival_time)
        if s is None:
            (hour, minute) = ("19", "00")
        else:
            (hour, minute) = s.groups()
        arrival_date = datetime(int(year), int(month), int(day), int(hour), int(minute), tzinfo=tz_tokyo)

        s = re_ymd.search(residence.departure_date)
        (year, month, day) = s.groups()
        departure_date = datetime(int(year), int(month), int(day), 9, 0, tzinfo=tz_tokyo)

        # Add Event to iCal
        event = Event()
        event.add('summary', residence.name)
        event.add('dtstart', arrival_date)
        event.add('dtend', departure_date)
        event.add('dtstamp', datetime.now(tz=tz_tokyo))
        event.add('uid', uuid.uuid1())
        ical.add_component(event)
    return ical


def create_ics(icalendar, filename):
    with open(filename, 'wb') as f:
        f.write(icalendar.to_ical())

app = Flask(__name__)

@app.route("/address.ics")
def katsuma_join():
    residence_list = get_address_reserved_list()
    # Create iCal
    ical = create_ical(residence_list)
    return ical.to_ical()


if __name__ == '__main__':
    # Create iCal
    app.run(host="0.0.0.0", port=5000, debug=True)

