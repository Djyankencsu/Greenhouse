#include <ESP8266HTTPClient.h>

#include <ArduinoWiFiServer.h>
#include <BearSSLHelpers.h>
#include <CertStoreBearSSL.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiAP.h>
#include <ESP8266WiFiGeneric.h>
#include <ESP8266WiFiGratuitous.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266WiFiSTA.h>
#include <ESP8266WiFiScan.h>
#include <ESP8266WiFiType.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <WiFiClientSecureBearSSL.h>
#include <WiFiServer.h>
#include <WiFiServerSecure.h>
#include <WiFiServerSecureBearSSL.h>
#include <WiFiUdp.h>

#include "config.h"
//#include <twilio.hpp>
//#include <WiFi.h>
//#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char* ssid = NETSSID;
const char* password = NETPASSWORD;
const int pin_number = 2;

/*
Twilio *twilio;

static const char *account_sid = TWILIOACCNTSID;
static const char *auth_token = TWILIOAUTHTOKEN;
// Phone number should start with "+<countrycode>"
static const char *from_number = TWILIOFROMNUMBER;

// You choose!
// Phone number should start with "+<countrycode>"
static const char *to_number = TONUMBER;
*/
// Domain Name with full URL Path for HTTP POST Request
const char *serverName = SERVERADDRESSANDPORT;
// Service API Key
String WriteKey = WRITEKEY;

// THE DEFAULT TIMER IS SET TO 10 SECONDS FOR TESTING PURPOSES
// For a final application, check the API call limits per hour/minute to avoid getting blocked/banned
unsigned long lastTime = 0;
// Set timer to 2 minutes (120000)
unsigned long timerDelay = 10000;
// Timer set to 10 seconds (10000)
//unsigned long timerDelay = 10000;

OneWire oneWire(pin_number);

DallasTemperature sensors(&oneWire);
/*
bool TwilioSend(float temperature) {
  String payload = "Alert! Temperature is " + String(temperature) + " degrees F";
  String response;
  twilio = new Twilio(account_sid, auth_token);
  bool success = twilio->send_message(to_number, from_number, payload, response);
  return success;
}
*/
void setup() {
  delay(5000);
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.println("\nConnecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  sensors.begin();
  delay(750);
  //Test to keep connection timing out
  WiFi.disconnect();
}

void loop() {
  float tempF = -196.00;
  if ((millis()-lastTime) > timerDelay) {
    while (tempF < -50){
      sensors.requestTemperatures();
      tempF = sensors.getTempFByIndex(0);
      Serial.println(tempF);
      //delay(1000);
    }
    WiFi.begin(ssid,password);
    while(WiFi.status() != WL_CONNECTED) {
      delay(500);
      //Serial.print(".");
    }
    if(WiFi.status()== WL_CONNECTED){
      WiFiClient client;
      HTTPClient http;
    
      String query = String(serverName) + "?WriteKey=" + String(WriteKey) + "&Temperature=" + String(tempF);
      // Your Domain name with URL path or IP address with path
      http.begin(client, query);
      
      // Specify content-type header
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      //Data to send with HTTP GET
      //String httpRequestData = serverName + "/?" + "WriteKey=" + WriteKey + "&Temperature=" + String(tempF);  //tempF         
      // Send HTTP GET request
      int httpResponseCode = http.GET();
      if (tempF <= 45) {
        //bool holder = TwilioSend(tempF);
      }
      http.end();
    }
    lastTime = millis();
  }
  WiFi.disconnect();
  delay(1000);
}
