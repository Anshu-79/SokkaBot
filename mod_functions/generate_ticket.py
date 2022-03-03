import uuid

from mod_functions.sch_database_functions import reader


async def newTicket():
    ticket_id = uuid.uuid4().fields[1]
    data = await reader()

    if len(data) == 0:
        return ticket_id

    else:
        ticket_ids = [entry[4] for entry in data]

        if ticket_id in ticket_ids:
            return False
        else:
            return ticket_id
