
import dbm_functions as dbm


clm_headers = ('channel', 'datetime', 'message', 'guild', 'ticket_id')

async def insert(input_data : dict) -> None:
    datetime = input_data['date'] + input_data['time']
    
    data = (input_data['channel name'], datetime, input_data['message'], input_data['guild_name'], input_data['ticket_id'])

    await dbm.inserter('announcements', clm_headers, data)
    
