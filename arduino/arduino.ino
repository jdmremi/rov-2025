#include <ArduinoJson.h>
#include <Servo.h>

Servo left;
Servo right;
Servo leftUp;
Servo rightUp;

// Pin for left forward-facing servo 
byte leftServoPin= 26; 
// Pin for right forward-facing servo
byte rightServoPin = 24;
// Pin for left upward-facing servo
byte leftUpServoPin = 22; 
// Pin for right upward-facing servo
byte rightUpServoPin = 28;

const int MAX_BUFFER_SIZE = 512;
char jsonBuffer[MAX_BUFFER_SIZE];

void setup() {
  // Initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
   // Turn off LED if previously turned on
  digitalWrite(LED_BUILTIN, LOW);
   // Set baudrate to 9600
  Serial.begin(9600);
  // Attach the Servos to pins
  left.attach(leftServoPin);
  right.attach(rightServoPin);
  leftUp.attach(leftUpServoPin);
  rightUp.attach(rightUpServoPin);

  // delay to allow ESC to recognize the stopped signal
  delay(7000); 
  // Turn on LED after initializing
  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
    static bool messageComplete = false;
    static int index = 0;
    if (Serial.available() > 0) {
        char receivedChar = Serial.read();

        // If we come across our null-terminator
        if (receivedChar == '\0') {
            // Null-terminate the buffer
            jsonBuffer[index] = '\0'; 
            // Reset index for next message
            index = 0;
            messageComplete = true;
        } else {
            // Add character to buffer if there's space
            if (index < MAX_BUFFER_SIZE - 1) {
                jsonBuffer[index++] = receivedChar;
            }
        }

        // Process JSON message if complete. jsonBuffer will contain all data.
        if (messageComplete) {
            StaticJsonDocument<MAX_BUFFER_SIZE> doc;
            StaticJsonDocument<MAX_BUFFER_SIZE> out;
            DeserializationError error = deserializeJson(doc, jsonBuffer);
            if (error) {
                Serial.print("Error parsing JSON: ");
                Serial.println(error.c_str());
            } else {
                JsonArray axisInfo = doc["axisInfo"];
                int forwardBackwardPulsewidth = axisInfo[0];
                int leftPulsewidth = axisInfo[1];
                int rightPulsewidth = axisInfo[2];
                int ascendDescendPulsewidth = axisInfo[3];
                int pitchLeftPulsewidth = axisInfo[4];
                int pitchRightPulsewidth = axisInfo[5];
                
                // If there's no forward/backward movement, then we can move left (since both are handled by left/right motors)
                if(forwardBackwardPulsewidth == 1500) {
                  left.writeMicroseconds(leftPulsewidth);
                  right.writeMicroseconds(rightPulsewidth);
                } else {
                  left.writeMicroseconds(forwardBackwardPulsewidth);
                  right.writeMicroseconds(forwardBackwardPulsewidth);
                }

                if(ascendDescendPulsewidth == 1500) {
                  leftUp.writeMicroseconds(pitchLeftPulsewidth);
                  rightUp.writeMicroseconds(pitchRightPulsewidth);  
                } else {
                  leftUp.writeMicroseconds(ascendDescendPulsewidth);
                  rightUp.writeMicroseconds(ascendDescendPulsewidth);
                }                
                // DHT11 sensor provides humidity value in percentage in relative humidity (20 to 90% RH) and temperature values in degree Celsius (0 to 50 °C).
                // DHT11 sensor uses resistive humidity measurement component, and NTC temperature measurement component.
                // out["humidity"] = humidity;
                // out["temperature"] = temperature;
                out["axisInfo"] = axisInfo;
                // Convert to Json string, send data to surface (Python).
                serializeJson(out,Serial);
                // Small delay
                delay(100);
                Serial.println();
            }
            messageComplete = false;
        }
    }
}