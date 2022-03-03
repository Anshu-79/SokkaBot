import dbm_functions as dbm

clm_headers = ("channel", "datetime", "message", "guild", "ticket_id", "author")

"""A collection of asynchronous DBM functions built specifically for the 'sch' command on the top of dbm_functions"""


async def insert(input_data: dict) -> None:

    data = (
        input_data["channel name"],
        input_data["date"] + input_data["time"],
        input_data["message"],
        input_data["guild_name"],
        input_data["ticket_id"],
        input_data["author"],
    )

    await dbm.inserter("announcements", clm_headers, data)


async def reader() -> list:
    # Gets the data in ASC ORDER by datetime
    # because we would later need to get the earliest announcement.
    # This makes it easier for us to just get the first element.
    data = await dbm.reader(table="announcements", order_by="datetime")
    return data


async def remover(ticket_id) -> None:

    await dbm.deleter("announcements", ticket_id)
