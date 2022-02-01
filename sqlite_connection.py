import aiosqlite
import time


async def main():
    async with aiosqlite.connect('sokka_dtbs.db') as db:
        async with db.execute("SELECT * FROM gif_tags") as cursor:
            data = await cursor.fetchall()
            print(data)
            print(type(data))
            #async for row in cursor:
            #   print(type(row),row)
            #  time.sleep(1)
