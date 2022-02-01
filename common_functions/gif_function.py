import aiosqlite
import disnake
import io

async def get_gif(input_msg):
    input_msg = input_msg.lower()
    async with aiosqlite.connect('sokka_dtbs.db') as db:
        cursor = await db.execute("SELECT * FROM gif_tags")
        tag_list = await cursor.fetchall()
        async for row in tag_list:
            for i in row[1:]:
                if i in input_msg:
                    gif_id = await row[0]
                    break
            
    async with aiosqlite.connect('sokka_dtbs.db') as db:
        cursor = await db.execute("SELECT gif_id, name, file FROM gifs")
        gif_data = cursor.fetchall()
        gif_binary = await gif_data[gif_data.index(gif_id)][2]
        gif_name = await gif_data[gif_data.index(gif_id)][1]

        gif_file = disnake.File(io.BytesIO(gif_binary.encode()), filename=f'{gif_name}.gif')
        return gif_file
    
    