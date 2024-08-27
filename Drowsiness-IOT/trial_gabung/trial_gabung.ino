#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include "soc/soc.h"           // Disable brownout problems
#include "soc/rtc_cntl_reg.h"  // Disable brownout problems
#include "Arduino.h"
#include <base64.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <string.h>

// Define the I2C address of your LCD module
#define LCD_ADDRESS 0x27
#define LCD_COLUMNS 16
#define LCD_ROWS 2

// Define the SDA and SCL pins for the ESP32-CAM
#define SDA_PIN 14
#define SCL_PIN 15

// Define the pin for the buzzer
#define BUZZER_PIN 13

// Create an instance of the LiquidCrystal_I2C class
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLUMNS, LCD_ROWS);

// ===================
// Camera Configuration 
// ===================
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// 4 for flash led or 33 for normal led
#define LED_GPIO_NUM   4

const char *ssid = "jesheng";
const char *password = "na77na10";

const char* serverName = "http://192.168.242.38:5000/predict";

void setupCamera() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Prevent brownout detector from resetting the ESP32

  Serial.begin(115200);
  Serial.setDebugOutput(true);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize the camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA;
  config.jpeg_quality = 10;
  config.fb_count = 2;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void setupLCD() {
    Wire.begin(SDA_PIN, SCL_PIN);
    lcd.begin();
    lcd.backlight();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("HELLO!");
    lcd.setCursor(0, 1);
    lcd.print("DAELY HERE!");
}

void printMemoryUsage() {
    Serial.printf("Free heap: %d\n", ESP.getFreeHeap());
    if (psramFound()) {
        Serial.printf("Free PSRAM: %d\n", ESP.getFreePsram());
    }
}

void setup() {
    Serial.begin(115200);
    printMemoryUsage();
    // setupCamera(); // Initialize the camera
    // Serial.println("Camera done");
    // printMemoryUsage();
    setupLCD();    // Initialize the LCD
    printMemoryUsage();
    // pinMode(BUZZER_PIN, OUTPUT); // Set the buzzer pin as output
    // noTone(BUZZER_PIN);
    printMemoryUsage(); 
    Serial.println("Setup done");
}
int count = 0;

void loop() {
  if (count == 0){
    setupLCD();
  }
    //camera take pic
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }else {
    Serial.println("Camera capture succeed");
  }

  String imageBase64 = base64::encode(fb->buf, fb->len);

  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);
  // Prepare JSON payload
  String jsonPayload = "{\"image\":\"" + imageBase64 + "\"}";

  // Send HTTP POST request
  int httpResponseCode = http.POST(jsonPayload);

  if (true) {
    String response = http.getString();
    String keyword = "Fatigue Subjects";
    Serial.println(response.indexOf(keyword));
    if(true){
      count++;
      if (count==3) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Severe-Drowsy:");
        lcd.setCursor(0, 1);
        lcd.print("STOP NOW");
        pinMode(BUZZER_PIN, OUTPUT); // Set the buzzer pin as output
        noTone(BUZZER_PIN);
        tone(BUZZER_PIN, 1000);
        delay(5000);
        pinMode(BUZZER_PIN, INPUT); // Set the buzzer pin as output
        delay(1000);
        Serial.println("BUZZER ON");
        count=0;
      }
      if (count==2) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Moderate-Drowsy:");
        lcd.setCursor(0, 1);
        lcd.print("Short Break");
        pinMode(BUZZER_PIN, OUTPUT); // Set the buzzer pin as output
        noTone(BUZZER_PIN);
        tone(BUZZER_PIN, 1000);
        delay(1000);
        pinMode(BUZZER_PIN, INPUT); // Set the buzzer pin as output
        delay(1000);
        Serial.println("BUZZER ON");
      }
      if (count==1){
        // Wire.begin(SDA_PIN, SCL_PIN);
        // lcd.init();
        // lcd.backlight();
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Mild-Drowsy:");
        lcd.setCursor(0, 1);
        lcd.print("Take a Rest");
      }
    }
    Serial.println(count);
    Serial.println(httpResponseCode);
    Serial.println(response);
  }
  else {
    String response = http.getString();
    Serial.print("Error on sending POST: ");
    Serial.println(httpResponseCode);
  }
  http.end();

  esp_camera_fb_return(fb);
  // Wait for 10 seconds before sending next image
  delay(5000);
}
