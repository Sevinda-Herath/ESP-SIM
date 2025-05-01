import time
import random
import json
from paho.mqtt.client import Client, MQTTv5
import socket

# MQTT Broker configuration
BROKER = ""  # Changed to a public test broker
PORT = 1883
PUBLISH_TOPIC = "esp32/sensor"
SUBSCRIBE_TOPIC = "esp32/control"

# Relay state (simulated)
relay_state = "OFF"

# Callback when connected to broker
def on_connect(client, userdata, flags, rc, properties=None):  # Updated signature for MQTTv5
    if rc == 0:
        print("Successfully connected to MQTT broker")
        client.subscribe(SUBSCRIBE_TOPIC)
    else:
        print(f"Connection failed with code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    global relay_state
    message = msg.payload.decode()
    print(f"[RECEIVED] Topic: {msg.topic}, Message: {message}")

    if message.upper() in ["ON", "OFF"]:
        relay_state = message.upper()
        print(f"Relay turned {relay_state}")

# MQTT client setup with retry mechanism
def connect_mqtt():
    client = Client(client_id=f"esp32_simulator_{random.randint(0, 1000)}", protocol=MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message
    
    retry_count = 0
    while retry_count < 3:
        try:
            print(f"Attempting to connect to {BROKER}:{PORT}")
            client.connect(BROKER, PORT, 60)
            return client
        except socket.error as e:
            retry_count += 1
            print(f"Connection attempt {retry_count} failed: {e}")
            time.sleep(2)
    raise ConnectionError("Failed to connect after 3 attempts")

# Main execution
try:
    mqtt_client = connect_mqtt()
    mqtt_client.loop_start()

    while True:
        temperature = round(random.uniform(22, 30), 2)
        humidity = round(random.uniform(40, 60), 2)
        soil_moisture = random.randint(200, 800)

        payload = {
            "temp": temperature,
            "humidity": humidity,
            "soil": soil_moisture
        }

        mqtt_client.publish(PUBLISH_TOPIC, json.dumps(payload))
        print(f"[PUBLISHED] {payload} | Relay: {relay_state}")
        time.sleep(5)

except ConnectionError as e:
    print(f"Connection error: {e}")
except KeyboardInterrupt:
    print("\nSimulation stopped.")
finally:
    try:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    except:
        pass