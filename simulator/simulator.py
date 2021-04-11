import argparse
import requests
import datetime
import dateutil.parser as dp
from uuid import uuid4

"""How to use

$ python3 simulator.py --topic company/hvac/things/ --thing-no 1 --start 2021-03-04T10:23:52+09:00 --count 100 --interval 10 --target-status cold --target-temp 23.0 --target-hum 69.0 --sensor-temp 22.5 --sensor-hum 68.0

This will generate 100 payloads with specified values of 10 minutes intervals from 2021-03-04T10:23:52+09:00 and publish the payloads to the company/hvac/things/1 topic

"""

def convert_to_epoch_time(isotime):
    t = isotime
    parsed_t = dp.parse(t)
    t_in_seconds = parsed_t.strftime('%s')
    return t_in_seconds

def convert_to_iso_time(epochtime):
    return datetime.datetime.fromtimestamp(epochtime).astimezone().isoformat()


parser = argparse.ArgumentParser(description="Simulator")

parser.add_argument('--topic', default="company/hvac/things/", help="publish topic")
parser.add_argument('--thing-no', required=True, help="Thing number")
parser.add_argument('--start', default=datetime.datetime.now().astimezone().replace(microsecond=0).isoformat(), help="from ISO time. i.e), 2021-03-04T10:23:52+09:00")
parser.add_argument('--count', default=1000, help="The number of payload generated. default: 1000")
parser.add_argument('--interval', default=1, help="The interval of each generated payload. default: 1 minute")
parser.add_argument('--target-status', default="cold", help="Target Status")
parser.add_argument('--target-temp', default=25.0, help="Target temperature")
parser.add_argument('--target-hum', default=70.0, help="Target humidity")
parser.add_argument('--sensor-temp', default=24.0, help="Target temperature")
parser.add_argument('--sensor-hum', default=69.0, help="Target humidity")

# Using globals to simplify sample code
args = parser.parse_args()

print(args)

"""
body = {
	"topic":"company/hvac/things/1",
	"payload": {
        "UUID": uuid4(),
        "type": "hvac",
        "deviceId": "1",
        "dateTime": "2021-03-04T10:23:52+09:00",
		"targetValue": {
			"status": "cold",
			"temperature": 23.0,
			"humidity": 50.0
		},
        "sensorValue": {
            "temperature": 23.0,
            "humidity": 45.5
        }
    }
}
"""

epochtime = int(convert_to_epoch_time(args.start))

for i in range(0, int(args.count)):
    body = {
        "topic":f'company/hvac/things/{args.thing_no}',
        "payload": {
            "UUID": uuid4(),
            "type": "hvac",
            "deviceId": args.thing_no,
            "dateTime": convert_to_iso_time(epochtime + i * int(args.interval) * 60),
            "targetValue": {
                "status": args.target_status,
                "temperature": float(args.target_temp),
                "humidity": float(args.target_hum)
            },
            "sensorValue": {
                "temperature": float(args.sensor_temp),
                "humidity": float(args.sensor_hum)
            }
        }
    }
    print(body)



URL = 'http://127.0.0.1:5000'
#response = requests.post(URL)


