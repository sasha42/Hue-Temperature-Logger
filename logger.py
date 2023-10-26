import time
import datetime
import csv
import os
import logging
from phue import Bridge
import gspread
import json

# Set up logging
logging.basicConfig(filename='temperature_logger.log', level=logging.INFO)

def check_env_vars():
    '''Check if the required environment variables are set'''
    required_vars = ['PHILIPS_HUE_IP', 'SHEET_URL']
    missing_vars = []

    for var in required_vars:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        logging.error(f"[PF] The following environment variables are missing: {', '.join(missing_vars)}")
        return False
    else:
        return True


def send_to_google_sheets(timestamp, upstairs, downstairs):
    '''Send the data to Google Sheets'''
    # Open the Google Sheet
    gc = gspread.service_account(filename='service_account.json')
    sheet_url = os.environ.get("SHEET_URL")
    sheet = gc.open_by_url(sheet_url).worksheet("Raw data")
    data = [ 
        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        round(upstairs/100,2),
        round(downstairs/100,2)
    ]

    # Append data to sheet
    sheet.append_row(data)


def connect_to_bridge():
    ip = os.environ.get("PHILIPS_HUE_IP")
    logging.info("Connecting to Philips Hue bridge at {}".format(ip))
    b = Bridge(ip)
    try:
        b.connect()
        data = b.get_api() # just to check if connection was successful
    except Exception as e:
        logging.error("Could not connect to Philips Hue bridge: {}".format(e))
        raise e
    return b


def get_sensors(b):
    upstairs = b.get_sensor()['14']['state']['temperature']
    downstairs = b.get_sensor()['61']['state']['temperature']
    timestamp = datetime.datetime.now()
    with open('sensors.csv', mode='a') as sensor_file:
        sensor_writer = csv.writer(sensor_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sensor_writer.writerow([timestamp, upstairs, downstairs])
    logging.info(f"{timestamp} {upstairs} {downstairs}")
    return timestamp, upstairs, downstairs


if __name__ == '__main__':
    # Check environment variables
    if not check_env_vars():
        exit(1)

    # Connect to bridge
    b = None
    while b is None:
        try:
            b = connect_to_bridge()
        except:
            logging.error('Could not connect to Philips Hue bridge. Retrying in 10 seconds...')
            time.sleep(10)

    # Connected to bridge, proceed to get sensors
    now = datetime.datetime.now()
    next_interval = now + datetime.timedelta(minutes=5 - now.minute % 5)
    sleep_time = (next_interval - now).total_seconds()
    time.sleep(sleep_time)

    while True:
        # Get sensors and send data to Google Sheets
        timestamp, upstairs, downstairs = get_sensors(b)
        send_to_google_sheets(timestamp, upstairs, downstairs)

        # Wait until the next 5-minute interval
        now = datetime.datetime.now()
        next_interval = now + datetime.timedelta(minutes=5 - now.minute % 5)
        sleep_time = (next_interval - now).total_seconds()
        time.sleep(sleep_time)