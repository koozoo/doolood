import sqlite3 as sq
from pathlib import Path


class DB:
    def __init__(self, db_name='default.db'):
        self.db_name = db_name
        self.db_path = Path.cwd().joinpath(f'data/{db_name}')
        self.value = []

    def connect_db(self):
        self.con = sq.connect(self.db_path)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS videos (
        label TEXT,title TEXT,link TEXT)""")
        self.con.commit()
        self.cur.close()

    def close_db(self):
        self.con.close()

    def add_data(self, label, title, link):
        self.lable = label
        self.title = title
        self.link = link

        self.data = [self.lable, self.title, self.link]
        self.value.append(self.data)

    def insert_data(self):
        self.cur = self.con.cursor()
        for data_unit in self.value:
            self.cur.execute("""INSERT INTO videos VALUES(?,?,?)""", data_unit)
        self.con.commit()
        self.cur.close()

    def take_data(self):
        self.value = []
        self.cur = self.con.cursor()
        self.cur.execute("""SELECT * FROM videos""")
        self.value = self.cur.fetchall()

    def delete_table(self):
        self.cur = self.con.cursor()
        self.cur.execute("""DROP TABLE videos""")

