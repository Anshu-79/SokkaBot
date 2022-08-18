import youtube_dl as ytdl
import disnake

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist",
}


class Video:
    # Class containing information about a particular video.

    def __init__(self, url_or_search, requested_by):
        # Plays audio from (or searches for) a URL.
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            video = self._get_info(url_or_search)
            # gets all the info & stores it in video

            video_format = video["formats"][0]
            self.stream_url = video_format["url"]  # url for bot
            self.video_url = video["webpage_url"]  # url for users to click on
            self.title = video["title"]  # title of the video

            get_thumbnail = lambda x: x[
                -1
            ]  # function to get the highest res thumbnail as it's always the last one...
            self.thumbnail = get_thumbnail(video["thumbnails"])["url"]
            # gets the url of thumbnail with get_thumbnail()

            get_duration = (
                lambda t: str(t // 60) + " minutes " + str(t % 60) + " seconds"
                if (t >= 60)
                else str(t) + " seconds"
            )
            self.duration = get_duration(video["duration"])
            # gets the duration in secs & converts it in mins & secs

            self.artist = video["artist"] if "artist" in video else "None"

            self.uploader = video["uploader"] if "uploader" in video else "None"
            self.album = video["album"] if "album" in video else "None"
            # gets the artist, uploader & album & returns None if none exists.

            self.requested_by = requested_by

    def _get_info(self, video_url):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"]
                )  # get info for first video
            else:
                video = info
                return video

    def get_embed(self):
        # makes an embed out of this Video's information.

        embed = disnake.Embed(
            title=self.title,
            description=f"""
          Uploader: {self.uploader}
          Artist: {self.artist}
          Album: {self.album}
          Duration: {self.duration}""",
            url=self.video_url,
        )

        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.display_avatar.url,
        )

        if self.thumbnail:
            embed.set_image(url=self.thumbnail)
        return embed
