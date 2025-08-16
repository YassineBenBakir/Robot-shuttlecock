#include <AFMotor.h> // Bibliothèque du driver moteur

// Déclaration des moteurs pour les roues omnidirectionnelles
AF_DCMotor motorM3(3); // Avant droit
AF_DCMotor motorM4(4); // Avant gauche
AF_DCMotor motorM2(2); // Arrière droit
AF_DCMotor motorM1(1); // Arrière gauche

void setup() {
    Serial.begin(115200); // UART avec la Raspberry Pi 

    delay(10000);  //  TEMPORISATION pour attendre la Raspberry Pi
    Serial.println("Le robot commence à avancer !");
    avancer(); // Le robot avance immédiatement
}

void loop() {
    // Vérifier si un message est reçu via UART depuis la RPi
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n'); // Lire le message jusqu'à un saut de ligne
        message.trim(); // Supprimer les espaces ou caractères de fin de ligne
        if (message == "DEPLACEMENT") {
            Serial.println("Ordre reçu: déplacement à droite et rotation 180°");
            arreter();
            delay(500); // Petite pause avant l'action
            seDecalerDroite();
            delay(500); // Pause pour stabilisation
            avancer();
            delay(1000); // Pause avant d'avancer
            seDecalerDroite();
            delay(500);
            avancer();
            delay(4000);
            arreter();
            // Tout s'arrête après l'action finale
            Serial.println("Le robot s'est arrêté définitivement.");
            while (true); // Boucle infinie pour bloquer toute autre exécution
        }
    }
}

// Fonction pour avancer en ligne droite
void avancer() {
    motorM1.setSpeed(200);
    motorM2.setSpeed(200);
    motorM3.setSpeed(200);
    motorM4.setSpeed(200);
    
    motorM1.run(FORWARD);
    motorM2.run(FORWARD);
    motorM3.run(FORWARD);
    motorM4.run(FORWARD);
}



// Fonction pour arrêter les moteurs
void arreter() {
    Serial.println("Arrêt des moteurs.");
    motorM1.run(RELEASE);
    motorM2.run(RELEASE);
    motorM3.run(RELEASE);
    motorM4.run(RELEASE);
}

// Fonction pour se décaler vers la droite
void seDecalerDroite() {
    Serial.println("Décalage vers la droite.");
    motorM1.setSpeed(200);
    motorM2.setSpeed(200);
    motorM3.setSpeed(200);
    motorM4.setSpeed(200);

    motorM3.run(FORWARD);
    motorM4.run(BACKWARD);
    motorM1.run(BACKWARD);
    motorM2.run(FORWARD);
    
    delay(2300); // Ajuster selon le déplacement voulu
    arreter();
}
