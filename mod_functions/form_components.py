import disnake

formComponents = [
    disnake.ui.TextInput(
        label="Channel Name",
        custom_id="channel",
        placeholder="Scheduled message's destination channel",
        style=disnake.TextInputStyle.short,
        max_length=100,
        required=True,
    ),
    disnake.ui.TextInput(
        label="Date",
        custom_id="date",
        placeholder="DD-MM-YYYY",
        style=disnake.TextInputStyle.short,
        min_length=10,
        max_length=10,
        required=True,
    ),
    disnake.ui.TextInput(
        label="Time",
        custom_id="time",
        placeholder="HH:MM:SS",
        style=disnake.TextInputStyle.short,
        min_length=8,
        max_length=8,
        required=True,
    ),
    disnake.ui.TextInput(
        label="Your Message",
        custom_id="message",
        placeholder="Type your message here",
        style=disnake.TextInputStyle.long,
        min_length=1,
        max_length=2000,
        required=True,
    ),
]
