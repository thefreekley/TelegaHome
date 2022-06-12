#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

#define ID 1

#define OUTPUT_PIN 5


RF24 radio(10,9); 

byte address[][6] = {"1Node","2Node","3Node","4Node","5Node","6Node"};  //возможные номера труб

byte items[6]= {0,0,0,0,0,0};

byte currentId;
boolean broadcast;

byte command;
boolean process;


void setup(){
  
  Serial.begin(9600); //открываем порт для связи с ПК
  radio.begin(); //активировать модуль
  radio.setAutoAck(1);         //режим подтверждения приёма, 1 вкл 0 выкл
  radio.setRetries(0,30);     //(время между попыткой достучаться, число попыток)
  radio.enableAckPayload();    //разрешить отсылку данных в ответ на входящий сигнал
  radio.setPayloadSize(1);     //размер пакета, в байтах

  radio.openReadingPipe(1,address[0]);      //хотим слушать трубу 0
  radio.setChannel(0x60);  //выбираем канал (в котором нет шумов!)

  radio.setPALevel (RF24_PA_MAX); //уровень мощности передатчика. На выбор RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX
  radio.setDataRate (RF24_1MBPS); //скорость обмена. На выбор RF24_2MBPS, RF24_1MBPS, RF24_250KBPS
  //должна быть одинакова на приёмнике и передатчике!
  //при самой низкой скорости имеем самую высокую чувствительность и дальность!!
  // ВНИМАНИЕ!!! enableAckPayload НЕ РАБОТАЕТ НА СКОРОСТИ 250 kbps!
  
  radio.powerUp(); //начать работу
  radio.startListening();  //начинаем слушать эфир, мы приёмный модуль
  

  pinMode(OUTPUT_PIN,OUTPUT); 
  
}

byte counter=0;
boolean read_mode = false;
boolean input_mode = false; 

void loop(void) {
    static unsigned long timeLastReceive = 0;
    byte pipeNo, gotByte;                          
    while( radio.available(&pipeNo)){    // слушаем эфир со всех труб
      radio.read( &gotByte, 1 );         // чиатем входящий сигнал
      

      byte number = gotByte;

      if(number == 254) read_mode = true;
      if(number == 253) read_mode = false;
      
      Serial.print(number);
      Serial.print( " " );
      Serial.print(counter);
      Serial.print( " " );
      Serial.println(read_mode);
      

    
      
      timeLastReceive = millis();
      if(read_mode){
      
      if (counter == 1){
          if (number == 0) analogWrite(OUTPUT_PIN,0);      
          else if (number == 1) analogWrite(OUTPUT_PIN,250);
          else if (number == 2)input_mode = true;
          else if (number == 3)input_mode = false;
          counter = 0;
      }

      if (counter == 0){
        if (number == ID || number == 252){
           counter++;
        }
      }

    }

    }
    if(millis() - timeLastReceive > 1000 && counter!=0){
       counter = 0;
       read_mode = false;
    }

   
    


           
}



void sendTo(byte number){

  byte pipeNo, gotByte;                          
    
  radio.writeAckPayload(pipeNo,&number, 1 );  // отправляем обратно то что приняли
   
}
