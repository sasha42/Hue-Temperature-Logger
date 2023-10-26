import time
import datetime
import csv
import os
from phue import Bridge
#import influxdb_client, os, time
#from influxdb_client import InfluxDBClient, Point, WritePrecision
#from influxdb_client.client.write_api import SYNCHRONOUS
import gspread
import json

# Influx DB config
# token = os.environ.get("INFLUXDB_TOKEN")
# org = os.environ.get("INFLUXDB_ORG")
# url = os.environ.get("INFLUXDB_URL")
# client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
# bucket="temperature"
# write_api = client.write_api(write_options=SYNCHRONOUS)

# def write_to_influxdb(temperature, location):
#    point = (
#      Point("sensors")
#      .field("realtemp", temperature)
#      .tag("location", location)
#    )
#    write_api.write(bucket=bucket, org=org, record=point)


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
    print("Connecting to Philips Hue bridge at {}".format(ip))
    b = Bridge(ip)
    try:
        b.connect()
        data = b.get_api() # just to check if connection was successful
    except Exception as e:
        print("Could not connect to Philips Hue bridge: {}".format(e))
        raise e
    return b


def get_sensors(b):
    upstairs = b.get_sensor()['14']['state']['temperature']
    downstairs = b.get_sensor()['61']['state']['temperature']
    timestamp = datetime.datetime.now()
    with open('sensors.csv', mode='a') as sensor_file:
        sensor_writer = csv.writer(sensor_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sensor_writer.writerow([timestamp, upstairs, downstairs])
        # write_to_influxdb(upstairs/100, "upstairs")
        # write_to_influxdb(downstairs/100, "downstairs")
    print(timestamp, upstairs, downstairs)
    return timestamp, upstairs, downstairs


if __name__ == '__main__':
    # Connect to bridge
    b = None
    while b is None:
        try:
            b = connect_to_bridge()
        except:
            print('Could not connect to Philips Hue bridge. Retrying in 10 seconds...')
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