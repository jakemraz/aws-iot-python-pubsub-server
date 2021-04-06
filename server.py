from flask import Flask, request
import pubsub

app = Flask(__name__)

@app.route('/ping')
def ping():
	return 'pong'

@app.route('/publish', methods=['POST'])
def publish():
	data = request.get_json()
	print(data)
	topic = data['topic']
	payload = data['payload']
	pubsub.publish(topic, payload)
	return 'ok'
