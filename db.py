import sqlite3


def create_database():
    conn = sqlite3.connect("telega_home.db") # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()



    cursor.execute( """ CREATE TABLE IF NOT EXISTS DEVICE (
                  id INTEGER  PRIMARY KEY UNIQUE NOT NULL,
                  device_id INTEGER,
                  user_id TEXT,
                  name TEXT,
                  type TEXT,
                  alert_sentece TEXT
                   ) """ )

    cursor.execute(""" CREATE TABLE IF NOT EXISTS MODE_MESSAGE (
                      id INTEGER  PRIMARY KEY UNIQUE NOT NULL,
                      user_id TEXT,
                      mode TEXT,
                      message TEXT
                       ) """)

    cursor.execute(""" CREATE TABLE IF NOT EXISTS USER (
                          id INTEGER  PRIMARY KEY UNIQUE NOT NULL,
                          user_id TEXT,
                          token TEXT,
                          comp TEXT,
                          region TEXT
                           ) """)

    conn.commit()

create_database()