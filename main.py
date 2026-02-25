# a tool to convert a image of prayer times to an ics file
from icalendar import Calendar, Event, vCalAddress, vText, Alarm
import pytz
from datetime import datetime, timedelta
from ai_reader import extract_prayer_times
import json

def get_month_number(month):
    match month.lower():
        case 'january': return 1
        case 'february': return 2
        case 'march': return 3
        case 'april': return 4
        case 'may': return 5
        case 'june': return 6
        case 'july': return 7
        case 'august': return 8
        case 'september': return 9
        case 'october': return 10
        case 'november': return 11
        case 'december': return 12
        case _: raise ValueError(f"Invalid month name: {month}")

def create_event(day, month, year, prayer_name, prayer_time, reminders_before_minutes, tz):
    event = Event()
    event.add('summary', f'{prayer_name} Prayer')
    event.add('description', f'Time for {prayer_name} prayer.')
    event.add('location', vText("Grey's prayer room or Elvet prayer room"))
    event.add('uid', f'Prayer-{prayer_name.lower()}-{day}-{prayer_time.replace(":", "")}@amalworks.dev')

    # time is in 12 hour format, need to convert to 24 hour format
    # assume fajr is always am
    # sunrise is always am
    # if dhuhr isn't 12 its am, else pm
    # asr is always pm
    # maghrib is always pm
    # isha is always pm
    if prayer_name in ['Fajr', 'Sunrise']:
        pass  # already am
    else:
        hour, minute = map(int, prayer_time.split(':'))
        if prayer_name == 'Dhuhr':
            if hour < 10:
                hour += 12
            prayer_time = f"{hour}:{minute:02d}"
        else:
            # Asr, Maghrib, Isha
            if hour != 12:
                hour += 12
            prayer_time = f"{hour}:{minute:02d}"

    hour, minute = map(int, prayer_time.split(':'))
    start_time = datetime(year, get_month_number(month), day, hour, minute, 0)
    end_time = start_time + timedelta(minutes=15)  # assuming 15 mins for prayer
    event.add('dtstart', tz.localize(start_time))
    event.add('dtend', tz.localize(end_time))
    event.add('dtstamp', datetime.now(tz))

    # alarm for reminder
    alarm = Alarm()
    alarm.add("trigger", timedelta(minutes=-10))
    alarm.add("action", "DISPLAY")
    alarm.add("description", f"Reminder: {prayer_name} prayer in 10 minutes.")

    # add alarm to event
    event.add_component(alarm)

    return event

def test_prayer_times(filename):
    with open(filename, 'r') as f:
        prayer_data = f.read()
    return prayer_data

def main():

    # inputs
    reminders_before_minutes = input("Enter reminder time before prayer in minutes (default 10): ")
    if reminders_before_minutes.strip() == '':
        reminders_before_minutes = 10
    else:
        reminders_before_minutes = int(reminders_before_minutes)


    tz = pytz.timezone('Europe/London')

    # localize datetime to Europe/London timezone
    # dt = tz.localize(datetime(2025, 11, 12, 12, 0, 0))
    # print(dt)

    cal = Calendar()
    
    cal.add('version', '2.0')
    

    # # get the prayer times json from the image
    # with open('prayer_times_november.jpeg', 'rb') as img_file:
    #     image_bytes = img_file.read()

    # extracted_json = extract_prayer_times(image_bytes)
    extracted_json = test_prayer_times("prayer_times_ramadan.json")
    prayer_data = json.loads(extracted_json)

    first_month = prayer_data['months'][0]['month']
    first_day = prayer_data['months'][0]['daily_times'][0]['day']

    last_month = prayer_data['months'][-1]['month']
    last_day = prayer_data['months'][-1]['daily_times'][-1]['day']

    year = prayer_data['months'][0]['year']
    year_last = prayer_data['months'][-1]['year']

    prodid = "Durham Prayer times for"
    calname = ""

    if first_month == last_month and year == year_last:
        prodid += f" {first_month} {year}"
        calname = f'Prayer Times Month: {first_month} {year}'
    else:
        prodid += f" {first_day} {first_month} {year} to {last_day} {last_month} {year_last}"
        calname = f'Prayer Times Months: {first_day} {first_month} {year} to {last_day} {last_month} {year_last}'

    cal.add('prodid', f'-//{prodid}//com.amalworks.prayer_times//')
    cal.add('X-WR-CALNAME', f'{calname}')
    
    for month_data in prayer_data['months']:
        month = month_data['month']
        year = month_data['year']

        for daily_time in month_data['daily_times']:
            day = daily_time['day']
            print(f"Processing day {day}...")
            for prayer_name in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']: # Excluding Sunrise
                prayer_time = daily_time[prayer_name]
                event = create_event(day, month, year, prayer_name, prayer_time, reminders_before_minutes, tz)
                cal.add_component(event)
    
    
    ics_content = cal.to_ical()

    with open(f'prayer_times_{first_month}_{year}.ics', 'wb') as f:
        f.write(ics_content)

    print(f"ICS file 'prayer_times_{first_month}_{year}.ics' created successfully.")

if __name__ == "__main__":
    main()