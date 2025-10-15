#include <Arduino.h>
#include "DHT.h"

const int PINO_BOTAO_N = 12;
const int PINO_BOTAO_P = 13;
const int PINO_BOTAO_K = 14;
const int PINO_LDR = 34;
const int PINO_DHT = 15;
const int PINO_RELE = 27;

#define DHTTYPE DHT22
DHT dht(PINO_DHT, DHTTYPE);

void setup() {
  Serial.begin(115200);

  pinMode(PINO_BOTAO_N, INPUT_PULLUP);
  pinMode(PINO_BOTAO_P, INPUT_PULLUP);
  pinMode(PINO_BOTAO_K, INPUT_PULLUP);
  pinMode(PINO_LDR, INPUT);
  
  pinMode(PINO_RELE, OUTPUT);
  digitalWrite(PINO_RELE, LOW);

  dht.begin();
  
  Serial.println("ESP32 pronto. Enviando dados dos sensores em formato JSON...");
}

void loop() {
  int estado_N = !digitalRead(PINO_BOTAO_N);
  int estado_P = !digitalRead(PINO_BOTAO_P);
  int estado_K = !digitalRead(PINO_BOTAO_K);

  float valor_ldr = analogRead(PINO_LDR);
  float ph_simulado = (valor_ldr / 4095.0) * 14.0;

  float umidade = dht.readHumidity();

  if (!isnan(umidade)) {
    Serial.print("{\"n\":");
    Serial.print(estado_N);
    Serial.print(",\"p\":");
    Serial.print(estado_P);
    Serial.print(",\"k\":");
    Serial.print(estado_K);
    Serial.print(",\"ph\":");
    Serial.print(ph_simulado, 1);
    Serial.print(",\"umidade\":");
    Serial.print(umidade, 1);
    Serial.println("}");
  }

  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();

    if (comando == "LIGAR") {
      digitalWrite(PINO_RELE, HIGH);
      Serial.println("Comando recebido: BOMBA LIGADA");
    } else if (comando == "DESLIGAR") {
      digitalWrite(PINO_RELE, LOW);
      Serial.println("Comando recebido: BOMBA DESLIGADA");
    }
  }
  
  delay(2000);
}
