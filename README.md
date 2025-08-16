# Robot-shuttlecock
Robot mobile pour la récupération des volants de badminton après les entraînements*

Architecture du système
Le système repose sur une architecture modulaire combinant vision par ordinateur, contrôle embarqué et mécanique mobile :
- Détection des lignes : Une Raspberry Pi 3B+ avec une caméra capte les lignes blanches du terrain via OpenCV.
- Commande moteur : Les instructions de déplacement sont envoyées via UART à un Arduino Mega, qui pilote 4 moteurs à l’aide d’un driver Adafruit (L293D).
- Châssis et ramassage : Le robot se déplace avec des roues omnidirectionnelles (mécanum) et collecte les volants grâce à un entonnoir à brosses rotatives.
- Planification de trajectoire : Le robot balaye le terrain selon une trajectoire en zigzag, avec détection automatique des bords.

