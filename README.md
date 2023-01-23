# Hue temperature logger

![Temperature logging](TempLogger.png)

**🌡 Log temperature with Hue Sensors**

**☁️ Save data to InfluxDB**

**📊 Visualize with Grafana**

Log temperature from your Philips Hue Motion Sensors (which also log temperature) and save it to InfluxDB to visualize with Grafana. This code only does the logging part, intended to be run on a server or a Raspberry Pi sitting in your home, pushing data to a remote InfluxDB server.


## Setup
Here's what you'll need in order to get this up and running:
- Philips Hue Motion Sensor
- Philips Hue Bridge
- Raspberry Pi (or any other server)
- InfluxDB credentials
- Grafana

You'll need to clone this repository onto a Raspberry Pi or another server running at home. Next, you'll need to install the dependencies:
```
pip install -r requirements.txt
```

You'll need to setup a few environment variables for the script to work:
```
export PHILIPS_HUE_IP="192.168.1.10"
export INFLUXDB_TOKEN="5DcKJF7tLRG22zgh6ui_N8EtjYXp1PMVZWKqf5yBHl-a3_aTGB-BpmkDlWZYJQNX7FjTgl2aRfWcNzQKJLH9P=="
export INFLUXDB_ORG="Sasha"
export INFLUXDB_URL="https://eu-central-1-1.aws.cloud2.influxdata.com"
export INFLUXDB_BUCKET="home"
```

Then, when you run the script for the first time, you'll need to follow the instructions to authenticate with the Hue Bridge. After that, you can run the script as a cron job or a systemd service.

## Configuring sensors
I've hardcoded my sensors into the script, but you can easily change that to fit your needs. I used the `Hue Esssentials` app to get the IDs of my sensors, however you can also use a command line tool like `phue`. You can change the sensors on line 28 and 29 to suit your needs:
```    
upstairs = b.get_sensor()['14']['state']['temperature']
downstairs = b.get_sensor()['61']['state']['temperature']
```

## Grafana dashboard
Once you have the data in InfluxDB, you can create a Grafana dashboard to visualize it. For my setup, I used both the InfluxDB Cloud and Grafana Cloud to avoid managing the services myself.

Here's the query get the data for a single sensor:
```
from(bucket: "temperature")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "sensors")
  |> filter(fn: (r) => r["_field"] == "realtemp")
  |> filter(fn: (r) => r["location"] == "upstairs")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

And for the hisotgram:
```
from(bucket: "temperature")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "sensors")
  |> filter(fn: (r) => r["_field"] == "realtemp")
  |> filter(fn: (r) => r["location"] == "downstairs" or r["location"] == "upstairs")
  |> timedMovingAverage(every: 1m, period: 1h)
  |> yield(name: "mean")
```

---

Made with ♥️ in Switzerland