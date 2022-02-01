import aiosqlite
import disnake
import io

async def get_gif(input_msg, gif_id=None):
    #check if a word in the message is in our tags
    #by gathering all the tags and their IDs
    async with aiosqlite.connect('sokka_dtbs.db') as db:
        cursor = await db.execute("SELECT * FROM gif_tags")
        tag_list = await cursor.fetchall()
        for row in tag_list:
            for i in row[1:]:
                if i in input_msg.lower():
                    gif_id = row[0]
                    break

        #can't use only 'if gif_id:' because Python considers 0 as None too
        #so if a gif's ID was 0, below code wouldn't be executed
        if gif_id != None:
            #gather catchphrases, gif's binary data, etc. from database
            cursor = await db.execute("SELECT * FROM gifs")
            gif_data = await cursor.fetchall()
    
            #we can use gif_id as an index since gif_ids start from 0 too
            binary_data = gif_data[gif_id][3]
            name = gif_data[gif_id][1]
            catchphrase = gif_data[gif_id][2]

            #convert binary data to a file
            gif_file = disnake.File(io.BytesIO(binary_data), filename=f'{name}.gif')
            return (name, catchphrase, gif_file)
    
        else:
            return None
