from flask import Flask, jsonify
from azure.iot.hub import IoTHubRegistryManager, DigitalTwinClient
import msrest

app = Flask(__name__)

connection_str = "HostName=rd-iothub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=TcpaortpcdjcMkZDre1kVhBMdkAZVUXYPAIoTPaN/kQ="
device_id = "7CDFA11A3024"

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the IoT API'})

@app.route('/up')
def up():
    sent_message = "*U10C01#"
    try:
        registry_manager = IoTHubRegistryManager.from_connection_string(connection_str)
        registry_manager.send_c2d_message(device_id, sent_message)
        return jsonify({'message': f"Message {sent_message} sent successfully"})
    except msrest.exceptions.HttpOperationError as ex:
        return jsonify({'error': f"HttpOperationError: {ex.response.text}"})
    except Exception as ex:
        return jsonify({'error': f"Unexpected error: {ex}"})

@app.route('/down')
def down():
    sent_message = "*U01C01#"
    try:
        registry_manager = IoTHubRegistryManager.from_connection_string(connection_str)
        registry_manager.send_c2d_message(device_id, sent_message)
        return jsonify({'message': f"Message {sent_message} sent successfully"})
    except msrest.exceptions.HttpOperationError as ex:
        return jsonify({'error': f"HttpOperationError: {ex.response.text}"})
    except Exception as ex:
        return jsonify({'error': f"Unexpected error: {ex}"})

@app.route('/get_display_value')
def get_display_value():
    try:
        digital_twin_client = DigitalTwinClient.from_connection_string(connection_str)
        digital_twin = digital_twin_client.get_digital_twin(device_id)
        if digital_twin:
            display_value = digital_twin["$metadata"]["display"]["desiredValue"]
            return jsonify({'display_value': display_value})
        else:
            return jsonify({'error': 'No digital twin found'})
    except Exception as exc:
        return jsonify({'error': str(exc)})

if __name__ == '__main__':
    app.run(debug=True)
