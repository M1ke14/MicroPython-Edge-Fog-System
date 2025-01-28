from umqtt.simple import MQTTClient
import time
import network
import neopixel
from machine import Pin, PWM
from time import sleep
# Configurazione WiFi
#ssid="IoT-UNICA"
#password="I@T_unic@2019"
# Configurazione MQTT
ssid="iPhone di Michele"
password="ArchitetturaEdge"
ClientID = "raspberry-csv"
server = "broker.mqtt-dashboard.com"
topic = b'tinys3/three'


ledpower= Pin(17,Pin.OUT)
ledpower.value(1)

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

def process_csv(mqtt_client, topic):
    messages = []
    with open('/dataset/Dataset_three_dataset.csv', 'r') as csv_file:
        lines = csv_file.readlines()  # Leggi tutte le righe del file
        header = lines[0].strip().split(",")  # Estrai l'intestazione
        for line in lines[1:]:
            values = line.strip().split(",")  # Dividi la riga nei singoli valori
            row = dict(zip(header, values))  # Associa i valori alle colonne
            timestamp = row['timestamp_ns']
            sensor_id = row['device_name']
            number = int(sensor_id[6:]) 
            sensor_id=f"device{number:02}"
            media = float(row['rssi']) 
            if media > -75:
                message = {
                    "timestamp": timestamp,
                    "id": sensor_id,
                    "message": "fully_equipped"
                    }
            else:
                message = {
                    "timestamp": timestamp,
                    "id": sensor_id,
                    "message": "not_wearing_hard_hat"
                    }
            msg_payload = f"{message['timestamp']},{message['id']},{message['message']}"
            mqtt_client.publish(topic, msg_payload)
            print("Messaggio inviato:", msg_payload)
            mqtt_client.check_msg()
            sleep(4)

# Funzione di callback MQTT
def mqtt_callback(topic, msg):
    print("Messaggio ricevuto dal topic", topic.decode("utf-8"), ":", msg)
    


connect_wifi(ssid, password)
mqtt_client = MQTTClient(ClientID, server)
mqtt_client.set_callback(mqtt_callback)
mqtt_client.connect()
print("Connesso al broker MQTT")
subscribe_topic = "tinys3/check"

mqtt_client.subscribe(subscribe_topic)
print("Iscritto al topic:", subscribe_topic)

process_csv(mqtt_client, topic)
    


    # Disconnessione MQTT
mqtt_client.disconnect()
print("Disconnesso dal broker MQTT")


