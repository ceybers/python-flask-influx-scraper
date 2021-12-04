#!/usr/bin/env python3
import INA219 
import sys
import datetime
from time import sleep
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('ups')

def write():
    readings = INA219.getValues().split(',')
    json_body = [
        {
            "measurement": "INA219",
            "time": datetime.datetime.utcnow().isoformat(timespec='seconds'),
            "fields": {
                "voltage": float(readings[0]),
                "current": float(readings[1]),
                "power": float(readings[2]),
                "percent": float(readings[3])
            }
        }
    ]
    try:
        client.write_points(json_body)
    except Exception as e:
        sys.stderr.write("Could not write to database.\n")
        sys.stderr.write("Exception: %s" % str(e))
        sys.exit(1)
    return

if __name__=='__main__':
    print("Writing UPS data to InfluxDB...")
    while True:
        try:
            write()
            sleep(10)
        except KeyboardInterrupt:
            sys.stderr.write("Cancelled by keyboard input.")
            sys.exit(1)
        except:
            sys.exit(1)
