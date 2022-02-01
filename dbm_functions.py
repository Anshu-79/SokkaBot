import aiosqlite
import asyncio
import traceback

async def inserter(table_name : str, row : tuple):
    async with aiosqlite.connect('sokka_dtbs.db') as db:
        try:
            await db.execute(f"INSERT INTO {table_name} VALUES {row}")
            print(f'Inserted {row} in {table_name}')
        except Exception as exc:
            print(traceback.format_exception(type(exc), exc, exc.__traceback__))

