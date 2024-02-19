from flask import Flask, jsonify
import threading
from azure.iot.hub import IoTHubRegistryManager, DigitalTwinClient
import logging
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
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

connection_str_event_hub = 'Endpoint=sb://iothub-ns-rd-iothub-57224525-ae5daa8d09.servicebus.windows.net/;SharedAccessKeyName=iothubowner;SharedAccessKey=TcpaortpcdjcMkZDre1kVhBMdkAZVUXYPAIoTPaN/kQ=;EntityPath=rd-iothub'
consumer_group = '$Default'
eventhub_name = 'rd-iothub'
client = EventHubConsumerClient.from_connection_string(connection_str_event_hub, consumer_group, eventhub_name=eventhub_name)

logger = logging.getLogger("azure.eventhub")
logging.basicConfig(level=logging.INFO)

latest_display_value = 0

@app.route('/get_display_value')
def get_display_value():
    return jsonify({"display_value":latest_display_value.body_as_str()})


async def on_event(partition_context, event):
    global latest_display_value
    logger.info("Received event from partition {}".format(partition_context.partition_id))
    latest_display_value = event
    print(latest_display_value)
    await partition_context.update_checkpoint(event)

client = EventHubConsumerClient.from_connection_string(connection_str_event_hub, consumer_group, eventhub_name=eventhub_name)

async def receive():
    async with client:
        await client.receive(
            on_event=on_event,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )
        # receive events from specified partition:
        # await client.receive(on_event=on_event, partition_id='0')

def run_flask():
    app.run(debug=True)

if __name__ == '__main__':
    # Start the Event Hub receiver thread
    event_hub_thread = threading.Thread(target=asyncio.run, args=(receive(),))
    event_hub_thread.start()

    # Start the Flask server in the main thread
    run_flask()