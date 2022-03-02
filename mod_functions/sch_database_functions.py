import dbm_functions as dbm
from mod_functions.text_to_timestamp import t2t

clm_headers = ("channel", "datetime", "message", "guild", "ticket_id", "author")


async def insert(input_data: dict) -> None:
    datetime = input_data["date"] + input_data["time"]

    data = (
        input_data["channel name"],
        datetime,
        input_data["message"],
        input_data["guild_name"],
        input_data["ticket_id"],
        input_data["author"],
    )

    await dbm.inserter("announcements", clm_headers, data)


async def reader() -> list:
    # gets the data in ASC ORDER by datetime
    data = await dbm.reader(table="announcements", order_by="datetime")
    return data


async def remover(ticket_id) -> None:
    await dbm.deleter("announcements", ticket_id)
