import aiomysql
import asyncio
import os
import sqlite3
from functions.gif_functions.gif_database import gif_data_list as gif_data


def to_binary(file_path):
    with open(file_path, 'rb') as file:
        return file.read()

def get_gif(name):
    file_list = os.listdir('gifs')
    
    for file in file_list:
        if file.split('.')[0] == name:
            return to_binary(f"gifs/{file}")
    
    return None


                    
def main():
    class Database(object):
        def __enter__(self):
            self.conn = sqlite3.connect("sokka_dtbs.db")
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.conn.close()
        
        def __call__(self, query):
            c = self.conn.cursor()
            try:
                result = c.execute(query)
                self.conn.commit()
            except Exception as e:
                result = e
            return result

    
    
    with Database() as db:
        result = db("SELECT gif_id,name FROM gifs")
        result = result.fetchall()
        
        for r in result:
            print(r)
