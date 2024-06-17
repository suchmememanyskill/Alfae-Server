import sys, os, utils, steamgriddb, json, re, zipfile
from urllib.parse import quote

ENABLED = os.getenv("EXTRA_ENABLED", "0") == "1" or os.getenv("EXTRA_ENABLED", "0").lower() == "true"
EXTRA_DIR = os.getenv("EXTRA_DIR", "./extra")

class ExtraGameFile:
    def __init__(self, foldername : str, filename : str):
        self.path = os.path.join(EXTRA_DIR, foldername, filename)
        self.filename = filename
        self.download_size = os.path.getsize(self.path)
        self.url = f"{utils.BASE_URL}/extra/{quote(foldername)}/{quote(self.filename)}"
        self.ext = self.filename.split(".")[-1]
    
    def to_dict(self) -> dict:
        return {
            "type": utils.GAME_EXTRA,
            "ext": self.ext,
            "version": "unk",
            "name": self.filename,
            "download_size": self.download_size,
            "game_size": self.download_size,
            "url": self.url,
        }
        

class ExtraGame:
    def __init__(self, foldername : str):
        self.foldername = foldername
        self.path = os.path.join(EXTRA_DIR, foldername)
        self.game_id = utils.squash_name(foldername)
        self.game_name = foldername
        self.files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        self.files.sort()

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "game_name": self.game_name,
            "files": [ExtraGameFile(self.foldername, f).to_dict() for f in self.files],
            "platform": "Extra"
        }

def load() -> list[ExtraGame]:
    if not ENABLED:
        utils.info("Extra module is disabled")
        return []

    if not os.path.exists(EXTRA_DIR):
        utils.error(f"Extra directory {EXTRA_DIR} does not exist")
        return []

    extras = []

    for dir in [f for f in os.listdir(EXTRA_DIR) if os.path.isdir(os.path.join(EXTRA_DIR, f))]:
        try:
            extras.append(ExtraGame(dir))
        except Exception as e:
            utils.error(f"Error loading extra {dir}: {str(e)}")
    
    utils.info(f"Loaded {len(extras)} extras")
    return extras