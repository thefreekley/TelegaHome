/* В данном скетче с передающей части (ТХ) отправляется значение переменной counter,
 * переменная эта с каждым шагом увеличивается на единицу. Приёмник (RX) принимает
 * сигнал, и отправляет обратно то, что получил, используя функцию radio.writeAckPayload
 * То есть наш приёмник на одно мгновение становится передатчиком! Если наш передатчик (TX)
 * принимает ответный сигнал, он выдаёт то, что принял, и пишет посчитанное вермя между 
 * отправкой и приёмом сигнала в микросекундах. Данный скетч можно использовать для теста
 * модулей на качество связи, а также для понимания работы функции radio.writeAckPayload
 * by AlexGyver 2016
 */

#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

#define ID_1 2
#define ID_2 3

RF24 radio(10,9); // "создать" модуль на пинах 9 и 10 Для Уно
//RF24 radio(9,53); // для Меги

#define INPUT_PIN_2 5
#define INPUT_PIN_3 6

byte address[][6] = {"1Node","2Node","3Node","4Node","5Node","6Node"};  //возможные номера труб



void setup(){
  Serial.begin(9600); //открываем порт для связи с ПК

  radio.begin(); //активировать модуль
  radio.setAutoAck(1);         //режим подтверждения приёма, 1 вкл 0 выкл
  radio.setRetries(0,15);     //(время между попыткой достучаться, число попыток)
  radio.enableAckPayload();    //разрешить отсылку данных в ответ на входящий сигнал
  radio.setPayloadSize(32);     //размер пакета, в байтах

  radio.openWritingPipe(address[0]);   //мы - труба 0, открываем канал для передачи данных
  radio.setChannel(0x60);  //выбираем канал (в котором нет шумов!)

  radio.setPALevel (RF24_PA_MAX); //уровень мощности передатчика. На выбор RF24_PA_MIN, RF24_PA_LOW, RF24_PA_HIGH, RF24_PA_MAX
  radio.setDataRate (RF24_1MBPS); //скорость обмена. На выбор RF24_2MBPS, RF24_1MBPS, RF24_250KBPS
  //должна быть одинакова на приёмнике и передатчике!
  //при самой низкой скорости имеем самую высокую чувствительность и дальность!!
  // ВНИМАНИЕ!!! enableAckPayload НЕ РАБОТАЕТ НА СКОРОСТИ 250 kbps!

  radio.powerUp(); //начать работу
  radio.stopListening();  //не слушаем радиоэфир, мы передатчик
    pinMode(INPUT_PIN_2,INPUT); 
    pinMode(INPUT_PIN_3,INPUT); 
}

boolean input_mode_2 = true;
boolean input_mode_3 = true;


 
boolean read_mode = false;

byte counter=0;

byte current_id = 0;

void loop(void) {    
  byte gotByte;
      if (Serial.available()) {
     byte number = Serial.read();
     sendTo(number);

      if(number == 254) read_mode = true;
      if(number == 253) read_mode = false;


        if(read_mode){
      
      if (counter == 1){
          if (number == 1 && current_id == 251) {
            input_mode_2 = true;
            input_mode_3 = true;
          }
          else if (number == 0 && current_id == 251) {
            input_mode_2 = false;
            input_mode_3 = false;
          }

          else if (number == 1 && current_id == ID_1) input_mode_2 = true;  
          else if (number == 0 && current_id == ID_1) input_mode_2 = false;  

          else if (number == 1 && current_id == ID_2) input_mode_3 = true;  
          else if (number == 0 && current_id == ID_2) input_mode_3 = false;  
        
        
          

          
          counter = 0;
      }

      if (counter == 0){
        current_id = number;
//        if (number == ID || number == 251 ){
           counter++;
        
      }

    }
     
     }


 
    
    static unsigned long time_2 = 0;
     static byte old_value_2 = 0;
     
    if(millis()-time_2 > 1000){
      time_2 = millis();
       byte value_2 = digitalRead(INPUT_PIN_2);
      if (value_2 == 1 && old_value_2 == 0) Serial.print( String(ID_1) + "move");
      old_value_2 = value_2; 
    }
    
  

    static unsigned long time_3 = 0;
     static byte old_value_3 = 0;
     
    if(millis()-time_3 > 1000){
      time_3 = millis();
       byte value_3 = !digitalRead(INPUT_PIN_3);
      if (value_3 == 1 && old_value_3 == 0) Serial.print( String(ID_2) + "move");
      old_value_3 = value_3; 
    }
   
   


      
  
}

boolean check_input_mode_1(int PIN){
  static boolean old_value = 0;
  boolean change_value = 0;
  
  if( digitalRead(PIN) != old_value){
       if (old_value == 1 ) change_value = 1; 
  }
  
  old_value = digitalRead(PIN);
  return change_value;
}


boolean check_input_mode_2(int PIN){
  static boolean old_value = 0;
  boolean change_value = 0;
  
  if( digitalRead(PIN) != old_value){
       if (old_value == 1 ) change_value = 1; 
  }
  
  old_value = digitalRead(PIN);
  return change_value;
}






void sendTo(byte number){
    radio.write(&number,1);
}

//
//void sendOut(byte id, boolean value){
//  
//  byte counter = 254;
//  radio.write(&counter,1);   
//  
//  counter = id;
//  radio.write(&counter,1);   
//  counter = value;
//  radio.write(&counter,1);
//
//  counter = 253;
//  radio.write(&counter,1);
// 
//}
