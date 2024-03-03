from flask import Flask, jsonify
from azure.iot.hub import IoTHubRegistryManager, DigitalTwinClient
import msrest

app = Flask(__name__)

#connection string for sending C2D messages
connection_str = "HostName=rd-iothub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=TcpaortpcdjcMkZDre1kVhBMdkAZVUXYPAIoTPaN/kQ="
device_id = "10521C663374"

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the IoT HUB sample API'})

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
    return jsonify({"display_value":get_digital_twin()})

def get_digital_twin():
    try:
        digital_twin_client = DigitalTwinClient.from_connection_string(connection_str)
        digital_twin = digital_twin_client.get_digital_twin(device_id)
        if digital_twin:
            print("Digital Twin:", digital_twin)
            display_value = digital_twin["txESPData"]
            print("Display Value:", display_value)  
            print("cleaned Display Value:", display_value[2:4]) 
            return display_value[2:4]       
        else:
            print("No digital twin found")
            return -1
    except msrest.exceptions.HttpOperationError as ex:
        print("HttpOperationError: {0}".format(ex.response.text)) 
        return -1       
    except Exception as exc:
        print("Unexpected error: {0}".format(exc))
        return -1

if __name__ == '__main__':
    # Start the Flask server in the main thread
    app.run()