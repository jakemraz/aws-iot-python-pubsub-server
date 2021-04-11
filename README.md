



POST /publish
```json
// payload body
{
  "topic":"<topic>",
  "payload":{
    "deviceId":"<deviceId>",
  }
}
```

```json
// sample payload
{
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
    }
  }
}
```