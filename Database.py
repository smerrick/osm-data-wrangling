
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import csv


conn = psycopg2.connect(database = 'udacity', user = 'postgres', password = 'jack', host = '127.0.0.1', port = '5432')
print ('connected')

cur = conn.cursor()

cur.execute('''CREATE TABLE nodes (
    id BIGINT PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    username TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE nodes_tags (
    id BIGINT,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);

CREATE TABLE ways (
    id BIGINT PRIMARY KEY NOT NULL,
    username TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT
);

CREATE TABLE ways_tags (
    id BIGINT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);

CREATE TABLE ways_nodes (
    id BIGINT NOT NULL,
    node_id BIGINT NOT NULL,
    position BIGINT NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);''')

with open('nodes.csv', 'r', encoding='utf-8') as nodes:
    cur.copy_expert("""COPY nodes FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '"'""", nodes)

with open('nodes_tags.csv', 'r', encoding='utf-8') as nodes_tags:
    cur.copy_expert("""COPY nodes_tags FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '"'""", nodes_tags)
 

with open('ways.csv', 'r', encoding='utf-8') as ways:

    cur.copy_expert("""COPY ways FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '"'""", ways)

with open('ways_tags.csv', 'r', encoding='utf-8') as ways_tags:
  
    cur.copy_expert("""COPY ways_tags FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '"'""", ways_tags)

with open('ways_nodes.csv', 'r', encoding='utf-8') as ways_nodes:
    cur.copy_expert("""COPY ways_nodes FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '"'""", ways_nodes)

conn.commit()