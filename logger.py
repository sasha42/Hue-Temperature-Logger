import time
import datetime
import csv
from phue import Bridge
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Influx DB config
token = os.environ.get("INFLUXDB_TOKEN")
org = os.environ.get("INFLUXDB_ORG")
url = os.environ.get("INFLUXDB_URL")
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
bucket="temperature"
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_to_influxdb(temperature, location):
   point = (
     Point("sensors")
     .field("realtemp", temperature)
     .tag("location", location)
   )
   write_api.write(bucket=bucket, org=org, record=point)

def get_sensors():
    b = Bridge(os.environ.get("PHILIPS_HUE_IP"))
    b.connect()
    upstairs = b.get_sensor()['14']['state']['temperature']
    downstairs = b.get_sensor()['61']['state']['temperature']
    timestamp = datetime.datetime.now()
    with open('sensors.csv', mode='a') as sensor_file:
        sensor_writer = csv.writer(sensor_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sensor_writer.writerow([timestamp, upstairs, downstairs])
        write_to_influxdb(upstairs/100, "upstairs")
        write_to_influxdb(downstairs/100, "downstairs")
    print(timestamp, upstairs, downstairs)

while True:
    get_sensors()
    time.sleep(60)