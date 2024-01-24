Hinweis: Erstellt im Sommer 2021 für die Experimente bei Kotte

## Experimentbeschreibung

### Ziel
Erstellung von Latenzkarten vom Feld, in denen die Latenzen in Abhängigkeit von Datenpaketgrößen und genutzten Kommunikationsbibliotheken dargestellt sind.

### Versuchsaufbau

#### Hardware
- Das Versuchsfeld wird von einem WLAN Netzwerk abgedeckt
- An Roboter und Basisstation befindet sich jeweils eine ADVES-Box, welche:
    - beide über ein Ubuntu Betriebssystem verfügen 
    - miteinander kommunizieren
    - ihre Uhrzeiten regelmäßig miteinander synchronisieren (Zeitsynchronisation)
- Die ADVES-Box auf dem Roboter sendet Pakete unterschiedlicher Größe über verschiedene Kommunikationsbibliotheken und speichert die genaue Zeit, zu der jedes Paketes versendet wird sowie die zugehörige RTK-GPS-Position
- Die ADVES-Box an der Basisstation empfängt die Pakete und speichert die genaue Zeit, zu der ein Paket vollständig empfangen wurde

#### Software
Pseudocode des Programms, welches auf dem Roboter ausgeführt wird:
```Python
while True:
    for channel in [gRPC, MQTT, ZeroMQ]:
        for size in [1kB, 10kB, 100kB, 1MB, 10MB, 100MB, 1GB, 10GB]:
            packet = create_random_packet(size)
            save(current_time(), current_gps_position(), channel.name(), packet.size())
            channel.send(packet, blocking=True)
```

Pseudocode des Programms, welches auf der Basisstation ausgeführt wird:
```Python
def listen(channel):
    while True:
        packet = channel.receive(blocking=True)
        save(current_time(), channel.name(), packet.size())

for channel in [gRPC, MQTT, ZeroMQ]:
    spawn_subprocess(listen, parameters=[channel])
pause()
```

In diesem Pseudocode wird davon ausgegangen, dass es nur eine Fahrt auf dem Feld gibt.
Alternativ kann für jede Kommunikationsbibliothek eine separate Fahrt durchgeführt werden.
Die Auswahl der Kommunikationsbibliotheken, welche getestet werden, kann sich noch ändern.

Es wird davon ausgegangen, dass die Steuerung des Fahrzeuges von anderer Stelle übernommen wird (z.B. per Fernbedienung).
