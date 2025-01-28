from umqtt.simple import MQTTClient
from time import sleep
import network
import neopixel

#ssid="IoT-UNICA"
#password="I@T_unic@2019"

ssid="iPhone di Michele"
password="ArchitetturaEdge"
#ssid ="Free WiFi Ca"
#password=""
ClientID = "raspberry-sub"
name ='prova'
ip_address='172.25.192.1'

server="broker.mqtt-dashboard.com"
topic = b'tinys3/imu'
msg ='near_miss'

from umqtt.simple import MQTTClient
import time
from machine import Pin

# Configurazione WiFi e MQTT
myled =Pin(17,Pin.OUT)
myled.value(1)
ClientID = "mqtt-sensor-variance"
msg_template = "{},{},near_miss"
treshold = 2  
np = neopixel.NeoPixel(Pin(18), 1)

# Imposta il LED 0 al colore verde
np[0] = (255, 0, 0) 
np.write()  # Aggiorna la striscia LED

# Connessione WiFi
def connect_wifi(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, password)
    while not sta_if.isconnected():
        print("Connessione WiFi in corso...")
        time.sleep(1)
    print("Connesso al WiFi:", sta_if.ifconfig())
    np[0] = (0, 255, 0) 
    np.write()

# Calcolo della varianza
def calculate_variance(values):
    n = len(values)
    if n <= 1:
        return 0  
    mean = sum(values) / n  # Media
    variance = sum((x - mean) ** 2 for x in values) / n  # Varianza
    return variance
def mqtt_callback(topic, msg):
    print("Messaggio ricevuto dal topic", topic.decode("utf-8"), ":", msg)
    
def process_dataset(mqtt_client, topic, treshold):
    imu_dataset = []
    acc__variance_counter=0
    gyro__variance_counter=0
    mag__variance_counter=0
    ang__variance_counter=0
    send_message=False
    # Leggi il file CSV
    with open('/dataset/Dataset_imu.csv', 'r') as file:
        lines = file.readlines()
        
        # Intestazioni dalla prima riga
        headers = lines[0].strip().split(',') 
        
        # Processa ogni riga
        for line in lines[1:]:
            row = line.strip().split(',')
            timestamp = row[0]  # Il primo elemento è il timestamp
            
            # Estrai i dati di ogni sensore
            acc_values = [float(row[1]), float(row[2]), float(row[3])]
            gyro_values = [float(row[4]), float(row[5]), float(row[6])]
            ang_values = [float(row[7]), float(row[8]), float(row[9])]
            mag_values = [float(row[10]), float(row[11]), float(row[12])]  
            
            # Calcola la varianza per ogni sensore
            var_acc = calculate_variance(acc_values)
            var_gyro = calculate_variance(gyro_values)
            var_mag = calculate_variance(mag_values)
            var_ang = calculate_variance(ang_values)
            
            
            # Verifica la soglia e invia il messaggio se la soglia viene superata
            if (var_acc > treshold):
                acc__variance_counter=(acc__variance_counter+1)%3
            if (var_gyro > treshold):
                gyro__variance_counter=(gyro__variance_counter+1)%3
            if (var_mag > treshold):
                mag__variance_counter=(mag__variance_counter+1)%3
            if (var_ang > treshold):
                ang__variance_counter=(ang__variance_counter+1)%3
            
            if(acc__variance_counter>=2):
                sensor_id = f"Accele01"
                msg = msg_template.format(timestamp, sensor_id)
                mqtt_client.publish(topic, msg.encode('utf-8'), qos=0)
                print("Messaggio inviato:", msg)
            if(gyro__variance_counter>=2):
                sensor_id = f"Girosc01"
                msg = msg_template.format(timestamp, sensor_id)
                mqtt_client.publish(topic, msg.encode('utf-8'), qos=0)
                print("Messaggio inviato:", msg)
            if(mag__variance_counter>=2):
                sensor_id = f"Magnet01"
                msg = msg_template.format(timestamp, sensor_id)
                mqtt_client.publish(topic, msg.encode('utf-8'), qos=0)
                print("Messaggio inviato:", msg)
            if(ang__variance_counter>=2):
                sensor_id = f"Angola01"
                msg = msg_template.format(timestamp, sensor_id)
                mqtt_client.publish(topic, msg.encode('utf-8'), qos=0)
                print("Messaggio inviato:", msg)
               
                
            mqtt_client.check_msg()
            time.sleep(4)  


connect_wifi(ssid, password)
mqtt_client = MQTTClient(ClientID, server)
mqtt_client.set_callback(mqtt_callback)
mqtt_client.connect()
print("Connesso al broker MQTT")
subscribe_topic="tinys3/check"
mqtt_client.subscribe(subscribe_topic)

    
  
# Processa il dataset e invia i messaggi MQTT
process_dataset( mqtt_client, topic, treshold)
    
mqtt_client.disconnect()
print("Disconnesso dal broker MQTT")
np[0] = (0, 0, 0) 
np.write()