from googleapiclient.discovery import build
import datab


def get_periods_for_slots(time_table, slots):
    periods = []
    for p in slots:
        try:
            periods.append(time_table[tuple(filter(None, p.split("-")))])
        except KeyError:
            periods.append(None)
    return periods


def getrecur(dates, time):
    time = time.replace(":", "")
    r_list = ["2021" + d.replace("-", "") + "T" + time + "00" for d in dates]
    r_string = ",".join(r_list)
    return r_string


def check_for_syncdemia(service):
    check_for_cal = service.calendarList().list().execute()
    for cal in check_for_cal['items']:
        if cal['summary'] == "SyncDemia":
            return cal
    return None


def create_syncdemia(service):
    calendar = {
        'summary': 'SyncDemia',
        'timeZone': 'Asia/Kolkata'
    }
    syncdemia = service.calendars().insert(body=calendar).execute()
    cal_list = {
        'id': syncdemia['id'],
        "defaultReminders": [
            {
                "method": "popup",
                "minutes": 5
            }
        ]
    }
    service.calendarList().insert(body=cal_list).execute()
    return syncdemia


def calsync(batch_no, time_table, creds, months=1):
    event = {
        'start': {
            'dateTime': '',
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': '',
            'timeZone': 'Asia/Kolkata',
        },
        'recurrence': [
            "RDATE;VALUE=DATE-TIME:"
        ],
        'reminders': {
            'useDefault': True
        }
    }

    service = build('calendar', 'v3', credentials=creds)

    syncdemia = check_for_syncdemia(service)
    if syncdemia is None:
        syncdemia = create_syncdemia(service)
    else:
        return "Calendar already Created"

    batch = service.new_batch_http_request()

    time = datab.gethead()
    time = [t.split("-") for t in time]

    for do in range(1, 5 + 1):
        dates = datab.getdatesofdo(do, months)
        slotlist = datab.getslots(batch_no, do)
        details = get_periods_for_slots(time_table, slotlist["slots"])
        for count, period in enumerate(details):
            if not period:
                continue
            event['summary'] = period[0]
            event['location'] = period[2]
            event['description'] = period[1]
            if period[3]:
                event['description'] += "\n" + "Meet Link: " + period[3]
            event['start']['dateTime'] = '2021-' + \
                dates[0] + 'T' + time[count][0] + ":00"
            event['end']['dateTime'] = '2021-' + \
                dates[0] + 'T' + time[count][1] + ":00"
            event['recurrence'] = ["RDATE;VALUE=DATE-TIME:" +
                                   getrecur(dates[1:], time[count][0])]
            batch.add(service.events().insert(
                calendarId=syncdemia['id'], body=event))
    batch.execute()
    return "Calendar Created"

