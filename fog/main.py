from umqtt.simple import MQTTClient
import urequests
import ujson
import time
import network
import neopixel
from machine import Pin

#ssid = "Free WiFi Ca"
#password=""
ssid="iPhone di Michele"
password="ArchitetturaEdge"
#ClientID = "raspberry-sub"
server = "broker.mqtt-dashboard.com"
api_url = "http://57.129.55.123:3000/environment-events"

ClientID = "mqtt-to-api"
topics = {
    b'tinys3/three': {
        "token": "zh1IkgjZDRJuw85aSmZOPB",
        "url": "http://57.129.55.123:3000/operator-events"
    },
    b'tinys3/imu': {
        "token": "Abh9bAAYFcUUVEEfGsIhZx",
        "url": "http://57.129.55.123:3000/environment-events"
    }
}
myled =Pin(17,Pin.OUT)
myled.value(1)
leddata=18
num_leds=1
np =neopixel.NeoPixel(Pin(leddata),num_leds)
np[0] =(255,0,0)
np.write()

    
# Connessione WiFi
def connect_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, password)
    while not sta_if.isconnected():
        print("Connessione WiFi in corso...")
        time.sleep(1)
    print("Connesso al WiFi:", sta_if.ifconfig())
    np[0]=(0,255,0)
    np.write()

# Funzione per convertire il timestamp in formato ISO 8601
def convert_to_iso_custom(timestamp):
    try:
        ts = int(timestamp)  
        seconds = ts // 1000
        milliseconds = ts % 1000
        year, month, day, hour, minute, second = time.gmtime(seconds)[:6]
        return "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}.{:03d}".format(
            year, month, day, hour, minute, second, milliseconds
        )
    except ValueError:
        print("Errore nella conversione del timestamp:", timestamp)
        return None

# Funzione per elaborare il messaggio e transformarlo in formato JSON
def process_mqtt_message(msg, token):
    try:
        parts = msg.decode("utf-8").split(",")  #divide il messaggio
        timestamp = convert_to_iso_custom(parts[0])  # usa la funzione per convertire il timestamp
        sensor_id = parts[1]
        event_type = parts[2]
        return {
            "token": token,
            "timestamp": timestamp,
            "sensorId": sensor_id,
            "eventType": event_type
        }
    except (IndexError, ValueError):
        print("Errore nell'elaborazione del messaggio:", msg)
        return None

# Funzione per inviare dati all'API
def send_data_to_api(data, url,mqtt_client):
    try:
        headers = {"Content-Type": "application/json"}
        response = urequests.post(url, json=data, headers=headers)
        print("Risposta API:", response.status_code, response.text)
        message=response.text
        mqtt_client.publish("tinys3/check",message.encode('utf-8'),qos=0)
        response.close()
    except Exception as e:
        print("Errore nell'invio della richiesta API:", e)

# Funzione di callback MQTT
def mqtt_callback(topic, msg):
    print("Messaggio ricevuto dal topic", topic.decode("utf-8"), ":", msg)
    topic_info = topics.get(topic, None)  # Ottieni il token e l'URL associati al topic
    if topic_info:
        token = topic_info["token"]
        url = topic_info["url"]
        data = process_mqtt_message(msg, token)
        if data:
            print(data)
            send_data_to_api(data, url,mqtt_client)
    else:
        print("Nessuna configurazione associata al topic:", topic.decode("utf-8"))

# Configura e avvia il client MQTT
def setup_mqtt(client_id, server):
    client = MQTTClient(client_id, server)
    client.set_callback(mqtt_callback)
    client.connect()
    print("Connesso al broker MQTT")
    for topic in topics.keys():
        client.subscribe(topic)  # Iscrizione a tutti i topic
        print("Iscritto al topic:", topic.decode("utf-8"))
    return client


connect_wifi(ssid, password)
mqtt_client = setup_mqtt(ClientID, server)
while True:
    mqtt_client.wait_msg()
    print("In attesa di messaggi MQTT...")