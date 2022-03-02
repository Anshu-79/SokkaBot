import aiosqlite
import sqlite3


async def to_binary(file_path):
    with open(file_path, "rb") as file:
        return file.read()


# note that the order of elements of headers & row has to be the same
async def inserter(table_name: str, headers: tuple, row: tuple) -> None:
    try:
        if len(headers) == len(row):
            async with aiosqlite.connect("sokka_dtbs.db") as db:
                await db.execute(f"INSERT INTO {table_name}{headers} VALUES {row}")
                await db.commit()
                print(f"\nInserted {row} in {table_name}")

        else:
            print("Incorrect input. Ensure same number of inputs in headers & row.")

    except (sqlite3.OperationalError, sqlite3.IntegrityError) as exc:
        print(exc)


async def deleter(table_name: str, primary_key: int) -> None:
    async with aiosqlite.connect("sokka_dtbs.db") as db:
        try:
            table_info = await db.execute(f"PRAGMA table_info({table_name});")
            table_info = await table_info.fetchall()
            for row in table_info:
                if row[5] == 1:
                    pk_column_name = row[1]

            await db.execute(
                f"DELETE FROM {table_name} WHERE {pk_column_name} = {primary_key};"
            )
            await db.commit()
            print(f"\nDeleted row with Primary Key = {primary_key} from {table_name}")

        except sqlite3.OperationalError as exc:
            print(exc)


async def reader(**kwargs) -> list:
    table_name = kwargs["table"]
    columns = kwargs["columns"] if "columns" in kwargs.keys() else "*"
    order_by = kwargs["order_by"] if "order_by" in kwargs.keys() else None

    columns = [
        str(i) + ", " if columns.index(i) + 1 != len(columns) else str(i)
        for i in columns
    ]
    columns = "".join(columns)
    async with aiosqlite.connect("sokka_dtbs.db") as db:
        try:
            if not order_by:
                query = await db.execute(f"SELECT {columns} FROM {table_name};")
            elif order_by:
                query = await db.execute(
                    f"SELECT {columns} FROM {table_name} ORDER BY {order_by};"
                )
            data = await query.fetchall()

            return data

        except sqlite3.OperationalError as exc:
            print(exc)
