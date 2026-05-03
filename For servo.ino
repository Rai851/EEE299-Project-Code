#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

const char* ssid     = "POCO X4 Pro 5G";
const char* password = "Raiyan1234";

WebServer server(8080);

Servo servo_plastic, servo_paper, servo_metal;
#define PIN_PLASTIC 13
#define PIN_PAPER   12
#define PIN_METAL   14

int count_plastic = 0;
int count_paper   = 0;
int count_metal   = 0;

void showDisplay(String category, int p, int pa, int m) {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println(category);
  display.setTextSize(1);
  display.setCursor(0, 30);
  display.println("Plastic: " + String(p));
  display.println("Paper:   " + String(pa));
  display.println("Metal:   " + String(m));
  display.display();
}

void openBin(Servo &s, String name, int &count) {
  count++;
  showDisplay(name, count_plastic, count_paper, count_metal);
  s.write(90);
  delay(5500);
  s.write(0);
  showDisplay("Ready...", count_plastic, count_paper, count_metal);
}

void setup() {
  Serial.begin(115200);

  Wire.begin(21, 22);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found!");
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Connecting WiFi...");
  display.display();

  servo_plastic.attach(PIN_PLASTIC);
  servo_paper.attach(PIN_PAPER);
  servo_metal.attach(PIN_METAL);
  servo_plastic.write(0);
  servo_paper.write(0);
  servo_metal.write(0);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("WiFi Connected!");
  display.println(WiFi.localIP().toString());
  display.display();

  Serial.println("\nIP: " + WiFi.localIP().toString());

  server.on("/open/plastic", []() { openBin(servo_plastic, "PLASTIC", count_plastic); server.send(200, "text/plain", "OK"); });
  server.on("/open/paper",   []() { openBin(servo_paper,   "PAPER",   count_paper);   server.send(200, "text/plain", "OK"); });
  server.on("/open/metal",   []() { openBin(servo_metal,   "METAL",   count_metal);   server.send(200, "text/plain", "OK"); });

  server.begin();
  showDisplay("Ready...", 0, 0, 0);
}

void loop() {
  server.handleClient();
}
