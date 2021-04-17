import argparse
import requests
import datetime
import dateutil.parser as dp
from uuid import uuid4
import json
from random import random


def convert_to_epoch_time(isotime):
    t = isotime
    parsed_t = dp.parse(t)
    t_in_seconds = parsed_t.strftime('%s')
    return int(t_in_seconds)

def convert_to_iso_time(epochtime):
    return datetime.datetime.fromtimestamp(epochtime).astimezone().isoformat()


def generate_common_data(args):
    ret = {
        "topic":f'company/hvac/things/{args.thing_no}',
        "payload": {
            "UUID": str(uuid4()),
            "type": "hvac",
            "deviceId": args.thing_no,
            "dateTime": convert_to_iso_time(epochtime + i * int(args.interval) * 60),
            "targetValue": {
                "status": args.target_status,
                "temperature": float(args.target_temp),
                "humidity": float(args.target_hum)
            }
        }
    }
    return ret

def add_constant_data(data, args):
    sensor_value = {
                "temperature": float(args.sensor_temp),
                "humidity": float(args.sensor_hum)
            }

    data['payload']['sensorValue'] = sensor_value

def add_random_data(data, args):
    targetHumidity = float(args.target_hum)
    sensorHumidity = float(args.sensor_hum)
    targetTemperature = float(args.target_temp)
    sensorTemperature = float(args.sensor_temp)

    gapHumidity = abs(targetHumidity - sensorHumidity)
    gapTemperature = abs(targetTemperature - sensorTemperature)

    random_factor = int(args.random_factor)

    sensor_value = {
                "temperature": float(args.target_temp) + int(random() * random_factor * 2) - random_factor,
                "humidity": float(args.target_hum) + int(random() * random_factor * 2) - random_factor
            }
    data['payload']['sensorValue'] = sensor_value

def add_increase_data(data, i, args):
    targetCount = int(args.count) - 1
    if targetCount == 0:
        targetCount = 1
    targetHumidity = float(args.target_hum)
    sensorHumidity = float(args.sensor_hum)
    targetTemperature = float(args.target_temp)
    sensorTemperature = float(args.sensor_temp)

    sensor_value = {
                "temperature": sensorTemperature + (targetTemperature - sensorTemperature) * i / targetCount,
                "humidity": sensorHumidity + (targetHumidity - sensorHumidity) * i / targetCount,
            }
    data['payload']['sensorValue'] = sensor_value

def add_decrease_data(data, i, args):
    targetCount = int(args.count) - 1
    if targetCount == 0:
        targetCount = 1
    targetHumidity = float(args.target_hum)
    sensorHumidity = float(args.sensor_hum)
    targetTemperature = float(args.target_temp)
    sensorTemperature = float(args.sensor_temp)

    sensor_value = {
                "temperature": targetTemperature - (targetTemperature - sensorTemperature) * i / targetCount,
                "humidity": targetHumidity - (targetHumidity - sensorHumidity) * i / targetCount,
            }
    body['payload']['sensorValue'] = sensor_value


def generate_data(i, args):
    data = generate_common_data(args)
    if args.pattern == 'constant':
        add_constant_data(data, args)
    if args.pattern == 'random':
        add_random_data(data, args)
    if args.pattern == 'increase':
        add_increase_data(data, i, args)
    if args.pattern == 'decrease':
        add_decrease_data(data, i, args)
    return data

def add_plugin(body, recent_body):
    diffTemperature = abs(body['payload']['targetValue']['temperature'] - body['payload']['sensorValue']['temperature'])
    diffHumidity = abs(body['payload']['targetValue']['humidity'] - body['payload']['sensorValue']['humidity'])
    
    temperature_threshold = 2
    humidity_threshold = 5
    symtom_duration_min_threshold = 30

    if recent_body != {} and (diffTemperature >= temperature_threshold or diffHumidity >= humidity_threshold):
        recent_plugin = recent_body['payload'].get('plugin', None)
        symtom_start = recent_plugin.get('symtomStart', "") if recent_plugin is not None else ""
        symtom_start_millis = convert_to_epoch_time(symtom_start) if symtom_start != "" else None
        cur_millis = convert_to_epoch_time(body['payload']['dateTime'])
        symtom_duration_min = (cur_millis - symtom_start_millis) / 60 if symtom_start_millis is not None else 0
        symtom = 1 if symtom_duration_min >= symtom_duration_min_threshold else 0
    else:
        symtom = 0
        symtom_start = ""

    plugin = {
        'diffTemperature': diffTemperature,
        'diffHumidity': diffHumidity,
        'symtom': symtom,
        'symtomStart': symtom_start if symtom_start != "" else body['payload']['dateTime']
    }

    body['payload']['plugin'] = plugin




"""How to use

$ python3 simulator.py --topic company/hvac/things/ --thing-no 1 --start 2021-03-04T10:23:52+09:00 --count 100 --interval 10 --target-status cold --target-temp 23.0 --target-hum 69.0 --sensor-temp 22.5 --sensor-hum 68.0

This will generate 100 payloads with specified values of 10 minutes intervals from 2021-03-04T10:23:52+09:00 and publish the payloads to the company/hvac/things/1 topic

"""


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
parser.add_argument('--pattern', default='constant', help="Random generated pattern. options: constant | random | increase | decrease")
parser.add_argument('--random-factor', default=1, help="Random factor")

# Using globals to simplify sample code
args = parser.parse_args()

print(args)

"""
body = {
	"topic":"company/hvac/things/1",
	"payload": {
        "UUID": "30819289-300a-4e49-a475-e33785e818da",
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
        },

        "plugin": {
            "symtom": 0,
            "symtomStart": "2021-03-04T10:00:52+09:00",
            "diffTemperature":1.2,
            "diffHumidity":0.5
        }
    }
}
"""

epochtime = convert_to_epoch_time(args.start)
URL = 'http://127.0.0.1:5000/publish'

recent_body = {}

for i in range(0, int(args.count)):
    body = generate_data(i, args)
    add_plugin(body, recent_body)
    recent_body = body

    #requests.post(URL, json=body)
    print(body)
