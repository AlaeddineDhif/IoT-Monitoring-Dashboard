#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>
#include <time.h>

// Configuration du DHT22
#define DHTPIN D4       // Broche D4 pour le capteur
#define DHTTYPE DHT22   // Type du capteur : DHT22
DHT dht(DHTPIN, DHTTYPE);

String URL = "http://192.168.1.20/DHT22_Project/test_data.php";

const char* ssid = "TOPNET_5300";
const char* password = "lz9xfzz5p6";

// Configuration NTP
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600;  // Décalage horaire GMT+1 (Tunisie)
const int daylightOffset_sec = 0;

// Variables de timing
unsigned long lastSensorUpdate = 0;  // Dernière lecture du capteur
unsigned long lastSend = 0;          // Dernier envoi de données
float lastTemp = NAN;                // Dernière température valide
float lastHum = NAN;                 // Dernière humidité valide

void setup() {
  Serial.begin(115200);
  dht.begin();  // Initialisation du capteur DHT22
  connectWiFi();
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);  // Initialisation du serveur NTP
}

void loop() {
  unsigned long now = millis();  // Temps actuel en millisecondes

  // Lecture du capteur toutes les 2 secondes (limite physique du DHT22)
  if (now - lastSensorUpdate >= 2000) {
    float temperature = dht.readTemperature();  // Température en °C
    float humidity = dht.readHumidity();       // Humidité en %

    // Vérifier si les lectures sont valides
    if (!isnan(temperature)) {  // Correction : Ajout de la parenthèse manquante
      lastTemp = temperature;
    }
    if (!isnan(humidity)) {     // Correction : Ajout de la parenthèse manquante
      lastHum = humidity;
    }
    lastSensorUpdate = now;  // Mettre à jour le temps de la dernière lecture
  }

  // Envoi des données toutes les 1 seconde
  if (now - lastSend >= 1000) {
    if (WiFi.status() != WL_CONNECTED) {
      connectWiFi();  // Reconnexion WiFi si nécessaire
    }

    // Vérifier si les dernières valeurs sont valides
    if (!isnan(lastTemp) && !isnan(lastHum)) {
      struct tm timeInfo;
      if (getLocalTime(&timeInfo)) {  // Obtenir l'heure actuelle via NTP
        char dateTimeBuffer[30];
        strftime(dateTimeBuffer, sizeof(dateTimeBuffer), "%Y-%m-%d %H:%M:%S", &timeInfo);

        // Préparer les données à envoyer
        String postData = "temperature=" + String(lastTemp) + 
                          "&humidity=" + String(lastHum) + 
                          "&datetime=" + String(dateTimeBuffer);

        WiFiClient client;
        HTTPClient http;
        http.begin(client, URL);  // Initialiser la connexion HTTP
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");

        int httpCode = http.POST(postData);  // Envoyer les données
        String payload = http.getString();   // Réponse du serveur

        // Affichage des informations dans le moniteur série
        Serial.print("URL : "); Serial.println(URL);
        Serial.print("Data: "); Serial.println(postData);
        Serial.print("httpCode: "); Serial.println(httpCode);
        Serial.print("payload : "); Serial.println(payload);
        Serial.println("--------------------------------------------------");

        http.end();  // Fermer la connexion
      } else {
        Serial.println("Erreur de récupération de l'heure via NTP");
      }
    } else {
      Serial.println("Erreur : Données du capteur invalides");
    }
    lastSend = now;  // Mettre à jour le temps du dernier envoi
  }
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.print("Connected to: "); Serial.println(ssid);
  Serial.print("IP address: "); Serial.println(WiFi.localIP());
}
