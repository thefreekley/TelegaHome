import telebot
import config
from telebot import types
import serial
import sqlite3
import serial_port_list
import time
import threading
import sys

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd



open_comport_troggle = False
alarm_mode = True
change_alarm_mode = False
ser = False



class my_bot(telebot.TeleBot):

    def loop_poop(self):
        while True:

            if open_comport_troggle:
                str_ser = str(ser.readline())
                if (str_ser.find('move') != -1):
                    device_id = str_ser[str_ser.find('b') + 2 : str_ser.find('move')]

                    cursor.execute("SELECT alert_sentece,name from DEVICE WHERE user_id = ? AND device_id = ?",
                                   [str(self.user_id), int(device_id) ])

                    info = cursor.fetchall()

                    bot.send_message(self.message_chat_id, info[0][1] + ":" + info[0][0])
            else:
                pass
            time.sleep(0.1)

    def loop_alarm(self):
        while True:
            global alarm_mode,change_alarm_mode
            if alarm_mode:
                r = requests.get(config.URL_TEMPLATE)
                cursor.execute("SELECT region from USER WHERE user_id = ?", [self.user_id])
                info = cursor.fetchall()

                if len(info[0]) != 0:
                    print((r.text).find(info[0][0]))
                    if (r.text).find(info[0][0]) != -1:
                        if change_alarm_mode == False:
                            bot.send_message(self.message_chat_id, "ALARM in " + info[0][0] + "! I turn off all output device!")
                            change_alarm_mode = True
                            if open_comport_troggle:
                                ser.write(bytes([254]))
                                time.sleep(0.1)

                                ser.write(bytes([252]))
                                time.sleep(0.1)
                                ser.write(bytes([0]))
                                time.sleep(0.1)

                                ser.write(bytes([253]))
                                time.sleep(0.1)
                            else:
                                bot.send_message(self.message_chat_id,'Not connection to COMP')
                    else:
                        if change_alarm_mode == True:
                            bot.send_message(self.message_chat_id, "ALARM in " + info[0][0] + "is end. I turn on all output device!")
                            change_alarm_mode = False
                            if open_comport_troggle:
                                ser.write(bytes([254]))
                                time.sleep(0.1)

                                ser.write(bytes([252]))
                                time.sleep(0.1)
                                ser.write(bytes([1]))
                                time.sleep(0.1)

                                ser.write(bytes([253]))
                                time.sleep(0.1)
                            else:
                                bot.send_message(self.message_chat_id,'Not connection to COMP')




                if r.status_code == 200:
                    pass

            time.sleep(30)

    def start_alarm(self,message_chat_id, user_id):
        self.message_chat_id = message_chat_id
        self.user_id = user_id

        thread = threading.Thread(target=self.loop_alarm)
        thread.start()

    def start_action(self, message_chat_id, user_id):
        self.message_chat_id = message_chat_id
        self.user_id = user_id
        thread = threading.Thread(target=self.loop_poop)
        thread.start()



bot = my_bot(token = config.TOKEN, threaded=False)

conn = sqlite3.connect("telega_home.db", check_same_thread=False)
cursor = conn.cursor()

last_message = ''







@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    item1 = types.KeyboardButton("Menu")
    item2 = types.KeyboardButton("Add device")
    markup.add(item1,item2)
    bot.send_message(message.chat.id,'Start',reply_markup=markup)

    cursor.execute("SELECT user_id from USER WHERE user_id = ?", [str(message.from_user.id)])
    info = cursor.fetchall()
    if len(info[0])!=0:
        cursor.execute("INSERT into USER (user_id) VALUES (?)",
                       [str(message.from_user.id)])
        conn.commit()


    cursor.execute("SELECT comp from USER WHERE user_id = ?", [str(message.from_user.id)])
    info = cursor.fetchall()
    if len(info[0])!=0:
        connect_to_comp(info[0][0], str(message.from_user.id))
        if open_comport_troggle:
            bot.send_message(message.chat.id, 'Connected to ' + info[0][0])
            bot.start_action(message.chat.id, str(message.from_user.id))

    cursor.execute("SELECT region from USER WHERE user_id = ?", [str(message.from_user.id)])
    info = cursor.fetchall()
    if len(info[0]) != 0:
        bot.start_alarm(message.chat.id, str(message.from_user.id))














@bot.message_handler(content_types=['text'])
def message(message):
    if message.chat.type == 'private':

        last_message = give_last_message(message.from_user.id)


        if message.text == "Add device":
            # markup = types.InlineKeyboardMarkup(row_width = 2)
            # item1 = types.InlineKeyboardButton('Turn off the light in bathroom', callback_data = 'id:1')
            # item2 = types.InlineKeyboardButton('Turn off the light in bathroom', callback_data='id:2')
            # markup.add(item1, item2)
            bot.send_message(message.chat.id, 'Give device id:')
            set_last_message(message.from_user.id, 'Add device', 'Give device id:')
        elif message.text == "Menu":
            markup = types.InlineKeyboardMarkup()
            item1 = types.InlineKeyboardButton('Turn on all output device', callback_data='Turn on all output device')
            item2 = types.InlineKeyboardButton('Turn off all output device', callback_data='Turn off all output device')
            item3 = types.InlineKeyboardButton('Turn on all input device', callback_data='Turn on all input device')
            item4 = types.InlineKeyboardButton('Turn off all input device', callback_data='Turn off all input device')

            item5 = types.InlineKeyboardButton('Turn on alarmed mod', callback_data='Turn on alarmed mod')
            item6 = types.InlineKeyboardButton('Turn off alarmed mod', callback_data='Turn off alarmed mod')
            item10 = types.InlineKeyboardButton('Choose region', callback_data='Choose region')

            item7 = types.InlineKeyboardButton('Choose device', callback_data='Choose device')
            item8 = types.InlineKeyboardButton('Choose COMP', callback_data='Choose COMP')
            item9 = types.InlineKeyboardButton('Exit from program', callback_data='Exit from program')

            markup.row(item1,item2)
            markup.row(item3, item4)
            markup.row(item5, item6, item10)
            markup.add(item7)
            markup.add(item8)
            markup.add(item9)
            bot.send_message(message.chat.id, 'Menu', reply_markup=markup)

        else:
            if len(last_message) != 0:
                if last_message[2] == "Give device id:":
                    try:
                        id_device = int(message.text)

                        cursor.execute("SELECT device_id from DEVICE WHERE user_id = ?",
                                       [str(message.from_user.id)])
                        info = cursor.fetchall()
                        check_id = True
                        if len(info)!=0:
                            for i in info[0]:
                                if i == id_device:
                                    check_id = False

                        if check_id:
                            set_last_message(message.from_user.id, str(id_device), 'Give device name:')
                            bot.send_message(message.chat.id, 'Give device name:')
                        else:
                            bot.send_message(message.chat.id, 'You already used this id')


                    except ValueError:
                        bot.send_message(message.chat.id, 'It`s not number')
                elif last_message[2] == "Give device name:":
                    set_last_message(message.from_user.id, last_message[1] + "," + message.text, 'Give type of device:')

                    markup = types.InlineKeyboardMarkup(row_width = 3)
                    item1 = types.InlineKeyboardButton('Input', callback_data = 'Input')
                    item2 = types.InlineKeyboardButton('Output', callback_data='Output')
                    item3 = types.InlineKeyboardButton('Input/Output', callback_data='Input/Output')
                    markup.add(item1, item2, item3)

                    bot.send_message(message.chat.id, 'Give type of device:', reply_markup=markup)

                elif last_message[2] == 'Set alert message:':

                    split_data = last_message[1].split(",")
                    cursor.execute("INSERT into DEVICE ( user_id, device_id, name, type, alert_sentece ) VALUES (?,?,?,?,?)",
                                   [str(message.from_user.id), int(split_data[0]), split_data[1], split_data[2], message.text])
                    conn.commit()
                    set_last_message(message.from_user.id, None, None)
                    bot.send_message(message.chat.id, 'Your device is add!')





@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    global ser,open_comport_troggle,alarm_mode,change_alarm_mode
    try:
        if call.message:
            last_message = give_last_message(call.from_user.id)

            if last_message[2] ==  'Give type of device:':
                if call.data == 'Input':
                    bot.send_message(call.message.chat.id, 'You choose input type of device')
                elif call.data == 'Output':
                    bot.send_message(call.message.chat.id, 'You choose output type of device. Your device is add!')

                    split_data = last_message[1].split(",")

                    cursor.execute("INSERT into DEVICE (user_id, device_id, name, type, alert_sentece ) VALUES (?,?,?,?,?)",
                                   [str(call.from_user.id), int(split_data[0]), split_data[1], 'Output', None])
                    conn.commit()
                    set_last_message(call.from_user.id, None, None)

                elif call.data == 'Input/Output':
                    bot.send_message(call.message.chat.id, 'You choose input/output type of device')

                if call.data == 'Input' or call.data == 'Input/Output':
                    set_last_message(call.from_user.id, last_message[1] + "," + str(call.data), 'Set alert message:')
                    bot.send_message(call.message.chat.id, 'Set alert message:')
            else:
                if call.data == "Choose device":
                    cursor.execute("SELECT name,device_id from DEVICE WHERE user_id = ?",
                                   [str(call.from_user.id)])
                    info = cursor.fetchall()
                    markup = types.InlineKeyboardMarkup()

                    for i in info:

                        markup.row ( types.InlineKeyboardButton(i[0],callback_data='Change device: ' + str(i[1])),
                                     types.InlineKeyboardButton( "On", callback_data='On:' + str( i[1])),
                                     types.InlineKeyboardButton("Off", callback_data='Off:' + str( i[1])),
                                     )
                    bot.send_message(call.message.chat.id, 'Choose device:', reply_markup=markup)
                elif (call.data).find('Change device:')!= -1:

                    cursor.execute("SELECT name,device_id,type,alert_sentece from DEVICE WHERE user_id = ? AND device_id = ?",
                                   [str(call.from_user.id), int(call.data[15:]) ] )
                    info = cursor.fetchall()

                    markup = types.InlineKeyboardMarkup()
                    markup.add( types.InlineKeyboardButton("Delete device", callback_data='Delete device: +' + str( info[0][1] )) )

                    bot.send_message(call.message.chat.id, 'Name device: ' + info[0][0] + '\n' +
                                     'ID: ' + str(info[0][1]) + '\n' + 'Type: ' + info[0][2] +
                                     ((' \n Alert:' + info[0][3]) if info[0][3] is not None else '' )
                                     , reply_markup=markup)

                elif (call.data).find('Delete device:') != -1:
                    cursor.execute("DELETE FROM DEVICE WHERE user_id = ? AND device_id = ? ",
                                   [str(call.from_user.id), int((call.data)[16:])])

                    bot.send_message(call.message.chat.id, "Device was deleted!")

                elif call.data == 'Choose COMP':
                    serial_list = serial_port_list.serial_ports()
                    markup = types.InlineKeyboardMarkup()

                    for i in serial_list:
                        markup.row ( types.InlineKeyboardButton(i,callback_data='connect COMP: ' + i) )

                    bot.send_message(call.message.chat.id, 'Choose COMP:', reply_markup=markup)
                elif (call.data).find('connect COMP:') != -1:

                    if connect_to_comp( (call.data)[14:], call.from_user.id):
                        bot.send_message(call.message.chat.id, 'You connect to ' + (call.data)[14:])
                        bot.start_action(call.message.chat.id, str(call.from_user.id))
                    else:
                        bot.send_message(call.message.chat.id, 'Exists some problem with ' + (call.data)[14:])

                elif (call.data).find('On:') != -1:

                    if open_comport_troggle:

                        ser.write(bytes([254]))
                        time.sleep(0.1)
                        ser.write(bytes([int(call.data[3:])]))
                        time.sleep(0.1)
                        ser.write(bytes([1]))
                        time.sleep(0.1)
                        ser.write(bytes([253]))

                    else:
                        bot.send_message(call.message.chat.id, "COMP is not visible")

                elif (call.data).find('Off:') != -1:
                    if open_comport_troggle:
                        ser.write(bytes([254]))
                        time.sleep(0.1)

                        ser.write(bytes([int(call.data[4:])]))
                        time.sleep(0.1)
                        ser.write(bytes([0]))
                        time.sleep(0.1)

                        ser.write(bytes([253]))
                        time.sleep(0.1)
                    else:
                        bot.send_message(call.message.chat.id, "COMP is not visible")
                elif call.data == 'Turn on all output device':
                    if open_comport_troggle:
                        ser.write(bytes([254]))
                        time.sleep(0.1)

                        ser.write(bytes([252]))
                        time.sleep(0.1)
                        ser.write(bytes([1]))
                        time.sleep(0.1)

                        ser.write(bytes([253]))
                        time.sleep(0.1)
                    else:
                        bot.send_message(call.message.chat.id, "COMP is not visible")
                elif call.data == 'Turn off all output device':
                    if open_comport_troggle:
                        ser.write(bytes([254]))
                        time.sleep(0.1)

                        ser.write(bytes([252]))
                        time.sleep(0.1)
                        ser.write(bytes([0]))
                        time.sleep(0.1)

                        ser.write(bytes([253]))
                        time.sleep(0.1)
                    else:
                        bot.send_message(call.message.chat.id, "COMP is not visible")
                elif call.data == 'Turn on all input device':
                    if open_comport_troggle:
                        ser.write(bytes([254]))
                        time.sleep(0.1)

                        ser.write(bytes([251]))
                        time.sleep(0.1)
                        ser.write(bytes([1]))
                        time.sleep(0.1)

                        ser.write(bytes([253]))
                        time.sleep(0.1)
                    else:
                        bot.send_message(call.message.chat.id, "COMP is not visible")
                elif call.data == 'Turn off all input device':
                    if open_comport_troggle:
                        ser.write(bytes([254]))
                        time.sleep(0.1)

                        ser.write(bytes([251]))
                        time.sleep(0.1)
                        ser.write(bytes([0]))
                        time.sleep(0.1)

                        ser.write(bytes([253]))
                        time.sleep(0.1)
                    else:
                        bot.send_message(call.message.chat.id, "COMP is not visible")



                elif call.data == 'Exit from program':
                    bot.send_message(call.message.chat.id, 'You exit from program')

                    open_comport_troggle,ser = False,False
                    exit_program()

                elif call.data == "Choose region":
                    markup = types.InlineKeyboardMarkup()

                    for region in config.REGIONS:
                        markup.add(types.InlineKeyboardButton(region, callback_data='Select reg:' + region))

                    bot.send_message(call.message.chat.id, 'Choose region:', reply_markup=markup)

                elif (call.data).find('Select reg:') != -1:
                    region = call.data[11:]
                    try:
                        cursor.execute( 'UPDATE USER SET region = ? WHERE  user_id = ?',[region,str(call.from_user.id)])
                        conn.commit()
                        bot.send_message(call.message.chat.id, 'Your region is ' + region )
                    except:
                        bot.send_message(call.message.chat.id, 'To start connect to COMP')
                elif call.data == "Turn on alarmed mod":
                    alarm_mode = True
                    bot.start_alarm(call.message.chat.id, str(call.from_user.id))

                    cursor.execute("SELECT region from USER WHERE user_id = ?", [str(call.from_user.id)])
                    info = cursor.fetchall()

                    if len(info[0]) != 0:
                        bot.send_message(call.message.chat.id, 'Your start alarm mode to ' + info[0][0] )
                    else:
                        bot.send_message(call.message.chat.id, 'To start alarm mode choose your region')

                elif call.data == "Turn off alarmed mod":
                    alarm_mode = False
                    change_alarm_mode = False
                    
                    ser.write(bytes([254]))
                    time.sleep(0.1)

                    ser.write(bytes([252]))
                    time.sleep(0.1)
                    ser.write(bytes([1]))
                    time.sleep(0.1)

                    ser.write(bytes([253]))
                    time.sleep(0.1)














    except:
        pass

def exit_program():
    sys.exit()


def connect_to_comp(comp,user_id):
    global open_comport_troggle
    global ser
    try:
        ser = serial.Serial(comp, 9600, timeout=0)
        open_comport_troggle = True

        cursor.execute('UPDATE USER SET comp = ? WHERE  user_id = ?', [comp, str(user_id)])
        conn.commit()


    except:
        open_comport_troggle = False
        ser = False

    return open_comport_troggle

def set_last_message(user_id,message,mode):
    cursor.execute("DELETE FROM MODE_MESSAGE WHERE user_id = ?", [str(user_id)])
    cursor.execute("INSERT into MODE_MESSAGE (user_id, mode,message) VALUES (?,?,?)",
                   [str(user_id), message, mode])
    conn.commit()

def give_last_message(user_id):
    cursor.execute("SELECT user_id,mode,message from MODE_MESSAGE WHERE user_id = ?", [str(user_id)])
    info = cursor.fetchall()

    return info[0]


bot.polling(none_stop=True)