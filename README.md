# Architettura IoT Multi-livello per Monitoraggio Sicurezza (Edge-Fog-Cloud)

## Descrizione del Progetto
Il progetto implementa un'architettura IoT gerarchica progettata per il monitoraggio di eventi critici in contesti operativi. Il sistema utilizza microcontrollori TinyS3 e il linguaggio MicroPython per gestire il flusso di dati attraverso tre livelli: Edge (acquisizione e pre-processing), Fog (aggregazione e traduzione protocolli) e Cloud (storicizzazione e risposta).

## Architettura del Sistema
L'infrastruttura si articola su tre livelli funzionali:

1.  **Livello Edge (2 nodi TinyS3)**: 
    - Esegue il monitoraggio locale di dataset IMU e RSSI.
    - Implementa algoritmi di calcolo della varianza e della media on-device.
    - Pubblica messaggi di allerta ("near miss", "not wearing hard hat") tramite protocollo MQTT.
2.  **Livello Fog (1 nodo TinyS3)**: 
    - Agisce da gateway sottoscrivendo i topic MQTT provenienti dall'Edge.
    - Normalizza i timestamp nel formato ISO 8601 e incapsula i dati in strutture JSON.
    - Inoltra i dati al server Cloud tramite richieste HTTP POST.
3.  **Livello Cloud**: 
    - Gestisce gli endpoint API per la ricezione degli eventi.
    - Restituisce conferme di ricezione che vengono propagate fino ai nodi Edge per la validazione del ciclo di trasmissione.

## Requisiti

### Hardware
- 3x Microcontrollori TinyS3.
- Cavi di connessione USB-C per il flashing.
- Rete Wi-Fi locale (2.4 GHz).

### Software e Ambiente di Sviluppo
- **Firmware**: MicroPython (versione aggiornata per ESP32-S3).
- **IDE**: Thonny.
- **Librerie**: 
    - `umqtt.simple` per la gestione del protocollo MQTT.
    - `ujson` per la formattazione dei dati.
    - `network` e `utime` per la gestione dei servizi di sistema.

## Installazione e Download

### 1. Download del Codice
Per scaricare il repository locale, eseguire il comando:
```bash
git clone [https://github.com/m1ke14/readingcourse.git](https://github.com/m1ke14/readingcourse.git)
cd readingcourse
