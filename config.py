from os import getenv
from dotenv import load_dotenv
load_dotenv()
class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", "21482458"))
        self.API_HASH = getenv("API_HASH", "577573e5e3e8db6af7e680dcdde0f0da")
        self.BOT_TOKEN = getenv("BOT_TOKEN", "8783248365:AAHo07irwebfV5NHLihF7WV1gp8zXkCG9GM")
        self.MONGO_URL = getenv("MONGO_URL", "mongodb+srv://maga123:maga123@cluster0.6scbpzr.mongodb.net/?appName=Cluster0")
        self.LOGGER_ID = int(getenv("LOGGER_ID", "-1003567818438"))
        self.OWNER_ID = int(getenv("OWNER_ID", "8055987590"))
        self.DURATION_LIMIT = int(getenv("DURATION_LIMIT", 120)) * 60
        self.QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", 50))
        self.PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", 30))
        self.SESSION1 = getenv("SESSION", "AQFHy9oAmzL5T6OTifn6bPZ00b-n-2PV1sVV4o8UGqmhmwiyHV2O-E0i3eEjUWal08wN73fnLH6m0QXZdpL1vqS8R9T-z9m7SXmFfpxnadb252QU2lvHS1CG8jy7119SUWLanp4Sqt-FP_qnu9RIqbI5arrPIVetYNW2Aji3xo7QgxhcPE-XNBV63mkyqlPgetRlF0LZA3VFM2qmbm_2_znk6SaUT56jgMWLVDZ0cmcAmLRZgBWGL9YWjmtZTFMq0cDV5m66zYM8Ki81X6asW99REyPAruFWTdUWYgk_S0PRlgsFjiZ-CSWwsNbBQ0SKMQ-_0gL6O-3iF1XgGX-L3MNOkq2wYgAAAAIEBhvIAA"
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)
        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/AzerbaijanBots")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/ThisMaga")
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() == "true"
        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() == "true"
        self.THUMB_GEN: bool = getenv("THUMB_GEN", "True").lower() == "true"
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "True").lower() == "true"
        self.LANG_CODE = getenv("LANG_CODE", "az")
        self.COOKIES_URL = [
        url for url in getenv("COOKIES_URL", "https://batbin.me/beaus").split(" ")
        if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://r.resimlink.com/Zl3svDyiqX.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://r.resimlink.com/Zl3svDyiqX.jpg")
        self.START_IMG = getenv("START_IMG", "https://r.resimlink.com/Zl3svDyiqX.jpg")
    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
