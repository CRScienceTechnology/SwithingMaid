#include <Arduino.h>
#line 1 "C:\\Users\\Administrator\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\78686059\\ESP01S-SwithingMaid\\ESP01S-SwithingMaid.ino"
#include <ESP8266WiFi.h>
#include <PubSubClient.h> // 引入
#include <ArduinoJson.h> // 引入ArduinoJson库,解析JSON用

WiFiClient espClient;
PubSubClient client(espClient);


// GPIO Pin Configuration
#define PWM_Pin 0 // corresonding GPIO 0 as the PWM_PIN

// Maid Property
String maidcode="01"; //swithing maid code number

// WiFi
const char *ssid = "04"; // Enter your WiFi name
const char *password = "12345678";  // Enter WiFi password

// MQTT Server
const char *mqtt_broker = "47.94.167.240"; //MQTT服务器的IPV4地址，不需要加http前缀
const int mqtt_port = 1883;                //MQTT服务器的IPV4地址开放端口


// MQTT User
// 用于改写的String类
String mqtt_username_str = "swithingmaid" + maidcode + ' ' + WiFi.macAddress();
String mqtt_password_str = "swithingmaid" + maidcode + ' ' + WiFi.macAddress();
String topic_str = "swithing_maid_" + maidcode + "_state";
// 实际传入函数的字符串指针变量
const char *mqtt_username = mqtt_username_str.c_str();  //调用.c_str()方法把字符串变为字符串指针
const char *mqtt_password = mqtt_password_str.c_str();
const char *topic = topic_str.c_str();



                                  

long int currentMillis=0;
long int period_ms=0;
long int Task_curentMillis=0; 
bool ledState =false;


void callback(char *topic, byte *payload, unsigned int length);         // 回调函数，用于Loop消息函数的回调处理



#line 48 "C:\\Users\\Administrator\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\78686059\\ESP01S-SwithingMaid\\ESP01S-SwithingMaid.ino"
void setup();
#line 95 "C:\\Users\\Administrator\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\78686059\\ESP01S-SwithingMaid\\ESP01S-SwithingMaid.ino"
void loop();
#line 48 "C:\\Users\\Administrator\\AppData\\Local\\Arduino15\\RemoteSketchbook\\ArduinoCloud\\78686059\\ESP01S-SwithingMaid\\ESP01S-SwithingMaid.ino"
void setup() {  
    //setup阶段做一些前提准备
    Serial.begin(115200); // Set software serial baud to 115200;
    delay(1000);          // Delay for stability
    // 设置 PWM 频率为 50Hz (周期 20ms)
    analogWriteFreq(50);
    
    // Connecting to a WiFi network
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to the WiFi network");

    // Connecting to an MQTT broker
    client.setServer(mqtt_broker, mqtt_port);  // 设置IPV4地址及端口并尝试连接目标MQTT Server
    while (!client.connected()) 
    {
        String client_id = "ESP01S";
        client_id += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str()); //client_id.c_str()

        if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Public EMQX MQTT Server connected");
            
            client.publish(topic, "swithing maid is ready"); //发布主题
            client.subscribe(topic);             //订阅主题
            client.setCallback(callback);        //设置对订阅主题新消息的回调处理函数

            // 打印调试信息
            Serial.print("MQTT Username: ");
            Serial.println(mqtt_username);
            Serial.print("MQTT Password: ");
            Serial.println(mqtt_password);
            Serial.print("MQTT Topic: ");
            Serial.println(topic);
                
        } else {
            Serial.print("Failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }

}

void loop()
{
    // 检查WiFi连接状态
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi connection lost. Reconnecting...");
        WiFi.begin(ssid, password);
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.println("Re-connecting to WiFi...");
        }
        Serial.println("Connected to the WiFi network");

        // 重新连接MQTT broker
        while (!client.connected()) 
        {
            String client_id = "ESP01S";
            client_id += String(WiFi.macAddress());
            Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());

            if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
                Serial.println("Public EMQX MQTT Server connected");
                
                client.publish(topic, "swithing maid is ready"); //发布主题
                client.subscribe(topic);             //订阅主题
                client.setCallback(callback);        //设置对订阅主题新消息的回调处理函数

                // 打印调试信息
                Serial.print("MQTT Username: ");
                Serial.println(mqtt_username);
                Serial.print("MQTT Password: ");
                Serial.println(mqtt_password);
                Serial.print("MQTT Topic: ");
                Serial.println(topic);
                
            } else {
                Serial.print("Failed with state ");
                Serial.print(client.state());
                delay(2000);
            }
        }
    }

    client.loop();// 周期性处理 MQTT 客户端的网络通信和消息维护，如果有消息则会调用一次回调函数
    delay(100); // Delay for a short period in each loop iteration
}


//The parameters of the callback function are passed in automatically 
void callback(char *topic, byte *payload, unsigned int length)
{
    
    // Notice the message is received by maid
    Serial.print("Message arrived\n");     

    // Start Receive the message 
    String message;                  //message用于所订阅接收目标主题的状态消息
    for (int i = 0; i < length; i++) 
    {
        message += (char) payload[i]; // Convert *byte to string
    }
    Serial.println("Message is"+message);  

    // Analysis the received message
    StaticJsonDocument<200> jsonDoc;   // 创建200字节大小的jsonDoc对象，用于存储解析后的JSON数据
    deserializeJson(jsonDoc, message); // 解析这个message字符串，并将结果存储在 jsonDoc

    // Judge if jsonDoc has the correct format data like standard json data,then process the mission  
    // used json data content sample
    //
    // {
    //  "maidcode":"01",
    //  "status":"on",
    //  "angle":0
    // }

    if (jsonDoc.is<JsonObject>()) 
    {
        JsonObject jsonObj = jsonDoc.as<JsonObject>();
        const char* recieved_maid_code = jsonObj["maidcode"];
        const char* recieved_maid_status=jsonObj["status"];
        const float recieved_maid_rotate_angle=jsonObj["angle"].as<float>();

        const float transformed_angle = recieved_maid_rotate_angle*(255.0*0.125/180.0); // 将角度转化为0-255的数值


        if (strcmp(recieved_maid_code, maidcode.c_str()) == 0 &&strcmp(recieved_maid_status, "on")==0 ) // Notice：strcmp匹配完全相同才返回0
        {
           
           Serial.println("status:on");
           Serial.println("transformed angle value:"+String(transformed_angle));
           // 开启软 PWM
           for(int dutyCycle = 0; dutyCycle < 1023; dutyCycle++)// on esp01s the analogwrite ranges from 0 to 255 ,as the same time the pwm duty varies
          { 
            analogWrite(PWM_Pin,int(transformed_angle));// 设置占空比
          }
        } 
        else if (strcmp(recieved_maid_code, maidcode.c_str()) == 0 && strcmp(recieved_maid_status, "off")==0) 
        {  
           Serial.print("off");
           Serial.print("transformed 8-bit angle value:"+String(transformed_angle));
           // 关闭软 PWM
           for(int dutyCycle = 0; dutyCycle < 1023; dutyCycle++)
           { 
            analogWrite(PWM_Pin, 0);              
           }
        }
    }
}


// Learn:
// 1. printfln 比 print 多一个换行符 
// 2. Analog 函数的范围就是0-255
// 2. ESP01S 模拟 PWM 波的固定形式为为上述 for 循环语句内所示，用 while(1) 会造成堵塞

// Features:
// 1. ESP01S 在本次 analogWrite() 函数软模拟PWM波时，输入的数值范围是0-255，默认周期1ms，可以使用analogWriteFreq()进行频率设定，许可范围15~65535hz
// 2. SG90 舵机依靠 PWM 周期来决定可转动角度，
// ToDo:
// 1.解决输入角度180°时，产生的 PWM 占空比归零的问题


// ToDo:
// 1.解决启用 analogWriteFreq () 造成的 MQTT 消息响应缓慢问题

// Finished:
// 1.调整了 PWM 周期，使其能够从0转动到180°


// Used RAM:61311 Bytes (93%)
// Used Flash: 
