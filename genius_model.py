import sqlite3

conn = sqlite3.connect('genius.db')

print "Opened database successfully"

conn.execute('''CREATE TABLE songs
        (id INT PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        views NUMERIC,
        song_link TEXT,
        created_on DATETIME,
        updated_on DATETIME);''')

print "Table created successfully: songs"

conn.execute('''CREATE TABLE artists
        (id INT PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        created_on DATETIME,
        updated_on DATETIME);''')

print "Table created successfully: artists"

conn.execute('''CREATE TABLE producers
        (id INT PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        created_on DATETIME,
        updated_on DATETIME);''')

print "Table created successfully: producers"

conn.execute('''CREATE TABLE writers
        (id INT PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        created_on DATETIME,
        updated_on DATETIME);''')

print "Table created successfully: writers"

conn.execute('''CREATE TABLE lyrics
        (id INT PRIMARY KEY NOT NULL,
        artist INT NOT NULL,
        snippet TEXT NOT NULL,
        created_on DATETIME,
        updated_on DATETIME);''')

print "Table created successfully: lyrics"

conn.close()
