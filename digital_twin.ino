#include <Arduino.h>
#include <Wire.h>
#include <Arduino_RouterBridge.h>

#define DS18B20_PIN A0
#define NOISE_PIN   A1
#define VIBRATION_PIN A2
#define HR202_PIN   A3

#define HALL_PIN 8

#define LCD_ADDR 0x27

#define PZEM_ADDRESS 0xF8

volatile unsigned long pulseCount = 0;
unsigned long lastRPMTime = 0;
float motorRPM = 0;

float voltage = 0;
float current = 0;
float power = 0;
float energy = 0;
float frequency = 0;
float powerFactor = 0;

float cachedTemperature = 0;
float cachedNoise = 0;
float cachedVibration = 0;
int cachedHumidity = 0;
unsigned long lastSensorReadTime = 0;

bool showScreenTwo = false;

void lcdPrintInt(int value);
void lcdPrintFloat(float value, int decimals);
float readNoiseDb();
float readVibrationFrequency();

String getVoltage() {
  return String(voltage, 2);
}

String getCurrent() {
  return String(current, 3);
}

String getPower() {
  return String(power, 2);
}

String getEnergy() {
  return String(energy, 3);
}

String getFrequency() {
  return String(frequency, 2);
}

String getPowerFactor() {
  return String(powerFactor, 2);
}

String getRPM() {
  return String(motorRPM, 0);
}

String getTemperature() {
  return String(cachedTemperature, 2);
}

String getNoise() {
  return String(cachedNoise, 1);
}

String getVibration() {
  return String(cachedVibration, 2);
}

String getHumidity() {
  return String(cachedHumidity);
}

String getMotorCondition() {

  int score = 0;

  if (cachedTemperature > 80)
    score += 3;
  else if (cachedTemperature > 60)
    score += 2;
  else if (cachedTemperature > 45)
    score += 1;

  if (voltage < 200 || voltage > 250)
    score += 3;
  else if (voltage < 215 || voltage > 245)
    score += 1;

  if (current > 5.0)
    score += 3;
  else if (current > 4.0)
    score += 2;
  else if (current > 3.0)
    score += 1;

  if (powerFactor < 0.60)
    score += 3;
  else if (powerFactor < 0.75)
    score += 2;
  else if (powerFactor < 0.85)
    score += 1;

  if (frequency < 45 || frequency > 55)
    score += 3;
  else if (frequency < 48 || frequency > 52)
    score += 1;

  if (motorRPM < 50)
    return "STOPPED";

  if (motorRPM < 1000)
    score += 2;

  if (score >= 8)
    return "BAD";
  else if (score >= 4)
    return "MODERATE";
  else
    return "GOOD";
}

void displayMainScreen() {

  lcdClear();

  lcdSetCursor(0, 0);
  lcdPrint("LOCATION: ELECTRICAL");

  lcdSetCursor(0, 1);
  lcdPrint("MACHINE LAB");

  lcdSetCursor(0, 2);
  lcdPrint("MOTOR CONDITION");

  lcdSetCursor(0, 3);
  lcdPrint("STATUS: ");

  String condition = getMotorCondition();
  lcdPrint(condition.c_str());
}

void countPulse() {
  pulseCount++;
}

void lcdWrite(uint8_t data, uint8_t mode) {

  uint8_t high = data & 0xF0;
  uint8_t low  = (data << 4) & 0xF0;

  Wire.beginTransmission(LCD_ADDR);

  Wire.write(high | mode | 0x08);
  Wire.write(high | mode | 0x0C);
  Wire.write(high | mode | 0x08);

  Wire.write(low | mode | 0x08);
  Wire.write(low | mode | 0x0C);
  Wire.write(low | mode | 0x08);

  Wire.endTransmission();
}

void lcdCommand(uint8_t command) {
  lcdWrite(command, 0);
}

void lcdChar(char c) {
  lcdWrite(c, 1);
}

void lcdPrint(const char *text) {
  while (*text) {
    lcdChar(*text++);
  }
}

void lcdSetCursor(uint8_t col, uint8_t row) {

  uint8_t addresses[] = {
    0x00,
    0x40,
    0x14,
    0x54
  };

  lcdCommand(0x80 | (addresses[row] + col));
}

void lcdClear() {
  lcdCommand(0x01);
  delay(2);
}

void lcdInit() {

  delay(50);

  lcdCommand(0x33);
  lcdCommand(0x32);
  lcdCommand(0x28);
  lcdCommand(0x0C);
  lcdCommand(0x06);
  lcdCommand(0x01);

  delay(5);
}

void oneWireLow() {

  pinMode(DS18B20_PIN, OUTPUT);
  digitalWrite(DS18B20_PIN, LOW);
}

void oneWireRelease() {

  pinMode(DS18B20_PIN, INPUT_PULLUP);
}

bool oneWireReset() {

  bool presence;

  oneWireLow();

  delayMicroseconds(480);

  oneWireRelease();

  delayMicroseconds(70);

  presence = (digitalRead(DS18B20_PIN) == LOW);

  delayMicroseconds(410);

  return presence;
}

void oneWireWriteBit(bool bitValue) {

  if (bitValue) {

    oneWireLow();

    delayMicroseconds(6);

    oneWireRelease();

    delayMicroseconds(64);

  } else {

    oneWireLow();

    delayMicroseconds(60);

    oneWireRelease();

    delayMicroseconds(10);
  }
}

bool oneWireReadBit() {

  bool bitValue;

  oneWireLow();

  delayMicroseconds(6);

  oneWireRelease();

  delayMicroseconds(9);

  bitValue = digitalRead(DS18B20_PIN);

  delayMicroseconds(55);

  return bitValue;
}

void oneWireWriteByte(uint8_t data) {

  for (int i = 0; i < 8; i++) {

    oneWireWriteBit(data & 0x01);

    data >>= 1;
  }
}

uint8_t oneWireReadByte() {

  uint8_t data = 0;

  for (int i = 0; i < 8; i++) {

    if (oneWireReadBit()) {
      data |= (1 << i);
    }
  }

  return data;
}

float readTemperature() {

  if (!oneWireReset()) {
    return -999;
  }

  oneWireWriteByte(0xCC);
  oneWireWriteByte(0x44);

  delay(750);

  if (!oneWireReset()) {
    return -999;
  }

  oneWireWriteByte(0xCC);
  oneWireWriteByte(0xBE);

  uint8_t tempLSB = oneWireReadByte();
  uint8_t tempMSB = oneWireReadByte();

  int16_t rawTemperature =
    ((int16_t)tempMSB << 8) | tempLSB;

  return rawTemperature / 16.0;
}

float readNoiseDb() {

  const int samples = 200;
  const float adcReference = 3.3;

  float mean = 0;

  for (int i = 0; i < samples; i++) {
    mean += analogRead(NOISE_PIN);
    delayMicroseconds(200);
  }

  mean /= samples;

  float sum = 0;

  for (int i = 0; i < samples; i++) {

    float sample = analogRead(NOISE_PIN);
    float difference = sample - mean;

    sum += difference * difference;

    delayMicroseconds(200);
  }

  float rmsAdc = sqrt(sum / samples);
  float rmsVoltage = (rmsAdc / 1023.0) * adcReference;

  if (rmsVoltage <= 0.00002) {
    return 0;
  }

  float db = 20.0 * log10(rmsVoltage / 0.00002);

  if (db < 0) {
    db = 0;
  }

  return db;
}

float readVibrationFrequency() {

  const int calibrationSamples = 100;
  const unsigned long measurementTime = 1000;

  float mean = 0;

  for (int i = 0; i < calibrationSamples; i++) {
    mean += analogRead(VIBRATION_PIN);
    delayMicroseconds(500);
  }

  mean /= calibrationSamples;

  int threshold = (int)mean;
  int lastValue = analogRead(VIBRATION_PIN);

  unsigned long crossings = 0;
  unsigned long startTime = millis();

  while (millis() - startTime < measurementTime) {

    int currentValue = analogRead(VIBRATION_PIN);

    if (lastValue < threshold && currentValue >= threshold) {
      crossings++;
    }

    lastValue = currentValue;
  }

  return (float)crossings;
}

uint16_t crc16(uint8_t *data, uint8_t len) {

  uint16_t crc = 0xFFFF;

  for (uint8_t pos = 0; pos < len; pos++) {

    crc ^= data[pos];

    for (uint8_t i = 0; i < 8; i++) {

      if (crc & 0x0001) {

        crc >>= 1;
        crc ^= 0xA001;

      } else {

        crc >>= 1;
      }
    }
  }

  return crc;
}

uint16_t get16(uint8_t *data, uint8_t index) {

  return ((uint16_t)data[index] << 8) |
         data[index + 1];
}

bool readPZEM(uint8_t *response, uint8_t length) {

  while (Serial1.available()) {
    Serial1.read();
  }

  uint8_t request[8];

  request[0] = PZEM_ADDRESS;
  request[1] = 0x04;
  request[2] = 0x00;
  request[3] = 0x00;
  request[4] = 0x00;
  request[5] = 0x0A;

  uint16_t crc = crc16(request, 6);

  request[6] = crc & 0xFF;
  request[7] = (crc >> 8) & 0xFF;

  Serial1.write(request, 8);
  Serial1.flush();

  unsigned long startTime = millis();
  uint8_t index = 0;

  while (millis() - startTime < 1000) {

    if (Serial1.available()) {

      response[index++] = Serial1.read();

      if (index >= length) {
        return true;
      }
    }
  }

  return false;
}

void updatePZEM() {

  uint8_t response[25];

  if (!readPZEM(response, 25)) {
    return;
  }

  if (response[0] != PZEM_ADDRESS ||
      response[1] != 0x04 ||
      response[2] != 0x14) {

    return;
  }

  uint16_t receivedCRC =
    response[23] |
    ((uint16_t)response[24] << 8);

  uint16_t calculatedCRC =
    crc16(response, 23);

  if (receivedCRC != calculatedCRC) {
    return;
  }

  voltage = get16(response, 3) / 10.0;

  uint32_t currentRaw =
    ((uint32_t)get16(response, 5)) |
    ((uint32_t)get16(response, 7) << 16);

  current = currentRaw / 1000.0;

  uint32_t powerRaw =
    ((uint32_t)get16(response, 9)) |
    ((uint32_t)get16(response, 11) << 16);

  power = powerRaw / 10.0;

  uint32_t energyRaw =
    ((uint32_t)get16(response, 13)) |
    ((uint32_t)get16(response, 15) << 16);

  energy = energyRaw / 1000.0;

  frequency = get16(response, 17) / 10.0;

  powerFactor = get16(response, 19) / 100.0;
}

void updateRPM() {

  if (millis() - lastRPMTime >= 1000) {

    noInterrupts();

    unsigned long pulses = pulseCount;

    pulseCount = 0;

    interrupts();

    lastRPMTime = millis();

    motorRPM = pulses * 60.0;

    Serial.print("Pulses: ");
    Serial.print(pulses);

    Serial.print(" | RPM: ");
    Serial.println(motorRPM);
  }
}

void displayElectrical() {

  lcdClear();

  lcdSetCursor(0, 0);
  lcdPrint("V:");
  lcdPrintFloat(voltage, 1);
  lcdPrint(" I:");
  lcdPrintFloat(current, 3);
  lcdPrint("A");

  lcdSetCursor(0, 1);
  lcdPrint("P:");
  lcdPrintFloat(power, 1);
  lcdPrint("W PF:");
  lcdPrintFloat(powerFactor, 2);

  lcdSetCursor(0, 2);
  lcdPrint("E:");
  lcdPrintFloat(energy, 3);
  lcdPrint(" F:");
  lcdPrintFloat(frequency, 1);
  lcdPrint("Hz");

  lcdSetCursor(0, 3);
  lcdPrint("Motor:");
  lcdPrintFloat(motorRPM, 0);
  lcdPrint(" RPM");
}

void displaySensors() {

  lcdClear();

  lcdSetCursor(0, 0);
  lcdPrint("Temp:");

  if (cachedTemperature == -999) {
    lcdPrint("ERROR");
  } else {
    lcdPrintFloat(cachedTemperature, 1);
    lcdPrint(" C");
  }

  lcdSetCursor(0, 1);
  lcdPrint("HR202:");
  lcdPrintInt(cachedHumidity);

  lcdSetCursor(0, 2);
  lcdPrint("Noise:");
  lcdPrintFloat(cachedNoise, 1);
  lcdPrint(" dB");

  lcdSetCursor(0, 3);
  lcdPrint("RPM:");
  lcdPrintFloat(motorRPM, 0);
  lcdPrint(" Monitoring");
}

void lcdPrintInt(int value) {

  char buffer[16];

  snprintf(buffer, sizeof(buffer), "%d", value);

  lcdPrint(buffer);
}

void lcdPrintFloat(float value, int decimals) {

  char buffer[32];

  if (decimals == 0) {

    snprintf(buffer, sizeof(buffer), "%.0f", value);

  } else if (decimals == 1) {

    snprintf(buffer, sizeof(buffer), "%.1f", value);

  } else if (decimals == 2) {

    snprintf(buffer, sizeof(buffer), "%.2f", value);

  } else if (decimals == 3) {

    snprintf(buffer, sizeof(buffer), "%.3f", value);

  } else {

    snprintf(buffer, sizeof(buffer), "%.2f", value);
  }

  lcdPrint(buffer);
}

void setup() {

  Serial.begin(115200);

  Serial1.begin(9600, SERIAL_8N1);

  pinMode(HALL_PIN, INPUT_PULLUP);

  attachInterrupt(
    digitalPinToInterrupt(HALL_PIN),
    countPulse,
    FALLING
  );

  lastRPMTime = millis();

  pinMode(NOISE_PIN, INPUT);

  pinMode(VIBRATION_PIN, INPUT);

  pinMode(HR202_PIN, INPUT);
  pinMode(DS18B20_PIN, INPUT_PULLUP);

  Wire.begin();

  lcdInit();

  lcdClear();

  lcdSetCursor(0, 0);
  lcdPrint("INDUCTION MOTOR");

  lcdSetCursor(0, 1);
  lcdPrint("MONITORING SYSTEM");

  lcdSetCursor(0, 2);
  lcdPrint("Arduino UNO Q");

  lcdSetCursor(0, 3);
  lcdPrint("Starting...");

  delay(2500);

  showScreenTwo = false;

  Bridge.begin();

  Bridge.provide("get_voltage", getVoltage);
  Bridge.provide("get_current", getCurrent);
  Bridge.provide("get_power", getPower);
  Bridge.provide("get_energy", getEnergy);
  Bridge.provide("get_frequency", getFrequency);
  Bridge.provide("get_pf", getPowerFactor);
  Bridge.provide("get_rpm", getRPM);
  Bridge.provide("get_temperature", getTemperature);
  Bridge.provide("get_noise", getNoise);
  Bridge.provide("get_vibration", getVibration);
  Bridge.provide("get_humidity", getHumidity);
}

void loop() {

  updateRPM();

  updatePZEM();

  if (millis() - lastSensorReadTime >= 2000) {

    lastSensorReadTime = millis();

    cachedTemperature = readTemperature();

    cachedNoise = readNoiseDb();

    cachedVibration = readVibrationFrequency();

    cachedHumidity = analogRead(HR202_PIN);
  }

  static unsigned long lcdUpdateTime = 0;

  if (millis() - lcdUpdateTime >= 1000) {

    lcdUpdateTime = millis();

    displayMainScreen();
  }

  Serial.println();
  Serial.println("================================");

  Serial.print("Voltage     : ");
  Serial.print(voltage, 2);
  Serial.println(" V");

  Serial.print("Current     : ");
  Serial.print(current, 3);
  Serial.println(" A");

  Serial.print("Power       : ");
  Serial.print(power, 2);
  Serial.println(" W");

  Serial.print("Energy      : ");
  Serial.print(energy, 3);
  Serial.println(" kWh");

  Serial.print("Frequency   : ");
  Serial.print(frequency, 2);
  Serial.println(" Hz");

  Serial.print("Power Factor: ");
  Serial.println(powerFactor, 2);

  Serial.print("Motor RPM   : ");
  Serial.print(motorRPM, 0);
  Serial.println(" RPM");

  Serial.print("Temperature : ");
  Serial.println(cachedTemperature);

  Serial.print("Noise       : ");
  Serial.print(cachedNoise, 1);
  Serial.println(" dB");

  Serial.print("Vibration   : ");
  Serial.print(cachedVibration, 2);
  Serial.println(" Hz");

  Serial.print("Motor Condition: ");
  Serial.println(getMotorCondition());

  Serial.println("================================");
}
