import uuid

from mod_functions.sch_database_functions import reader


async def newTicket():
    ticket_id = uuid.uuid4().fields[1]
    data = await reader()

    if len(data) == 0:
        return ticket_id

    else:
        ticket_ids = [int(entry[4]) for entry in data]

        if ticket_id in ticket_ids:
            return False
        else:
            return ticket_id


async def ticketExists(ticket: int):
    data = await reader()

    try:
        ticket = int(ticket)
    except ValueError:
        return False

    if len(data) == 0:
        return False

    else:
        ticket_ids = [entry[4] for entry in data]

        if ticket in ticket_ids:
            # Returns all the data associated with that ticket
            vals = data[ticket_ids.index(ticket)]
            vals = [vals[0], vals[1], vals[2], vals[4]]
            dt = vals.pop(1)
            date = dt[:10]
            time = dt[10:]
            vals.extend([date, time])
            keys = ("channel", "message", "ticket_id", "date", "time")
            return dict(zip(keys, vals))

        else:
            return False
